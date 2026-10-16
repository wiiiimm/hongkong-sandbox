"""Preserve actual old ground outside the complete original Opus pair projection."""
from pathlib import Path
import subprocess,uuid
import numpy as np
import shapely
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
from rendered_patch_sampler import RenderedPatchSampler
import native_patch_resolution as patches

BATCH='government-xl-opus-preserved-neighbours-v1-20261016'
BASE=ROOT/'docs/astra-city/government-import';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
CAP=BASE/'government-xl-opus-basic-ground-capture-v1-20261016'
OLD=BASE/'government-xl-opus-private-terrain-v3-20261016'
NEIGH=BASE/'government-xl-opus-private-neighbours-v2-20261016'

PAIR=BASE/'government-xl-opus-pair-foundation-v2-20261016'

def main():
    assert not DOC.exists()and not LOCAL.exists()
    refs=[Path(__file__)];pins={}
    with connect()as c:
        c.execute('SET TRANSACTION READ ONLY')
        for folder in [CAP,OLD,NEIGH,PAIR]:
            r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
            for ref in r['evidenceRefs']:
                assert ref['path']not in pins or pins[ref['path']]==ref['sha256'];pins[ref['path']]=ref['sha256']
    for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
    original=read(OLD/'terrain-candidates.json')[0];patch=read(ROOT/original['path']);domain=read(OLD/'summary.json')['changedParentExtent'];selection=read(PAIR/'selection.json.gz');uids=[r['uid'] for r in selection['rows']];uid=uids[0]
    geometry=read(HERE/'local'/PAIR.name/'runtime-geometry.json.gz')['rows'];t=np.concatenate([np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)] for g in geometry])
    complete_projection=shapely.union_all([shapely.MultiPoint(face[:,[0,2]]).convex_hull for face in t]);exclude=complete_projection.buffer(.01,join_style='mitre')
    inputs=read(NEIGH/'neighbour-inputs.json.gz');byuid={r['building']['uid']:r for r in inputs['rows']};protect=[];accounts=[]
    for r in read(NEIGH/'neighbour-checks.json')['rows']:
        if not r['reasons']or r['existingNative']or r['candidate']or r['uid'] in uids:continue
        assert r['uid']=='landsd/319559:0'
        b=byuid[r['uid']]['building'];p=Polygon(b['rings'][0],b['rings'][1:]).buffer(.01,join_style='mitre');safe=p.difference(exclude);accounts.append(dict(uid=r['uid'],protectedAreaM2=safe.area,excludedSourceOverlapAreaM2=p.intersection(exclude).area))
        if safe.area>1e-8:protect.append(safe)
    protected=shapely.union_all(protect).intersection(shapely.box(*domain));assert protected.area>0 and protected.intersection(complete_projection).area==0
    before=read(CAP/'before-ground.json.gz');ground=np.asarray(before['completeRelevantDrawnTriplets']).reshape(-1,3,3);polys=shapely.polygons(ground[:,:,[0,2]]);valid=shapely.area(polys)>1e-10
    assert protected.difference(shapely.union_all(polys[valid])).area<1e-8,'Old ground must cover protected regions'
    helper=module('hotel_preserved_parent',HERE/'resolve-pass.py');parent=read(ROOT/'3d-viewer/city/data/terrain.json');grid=helper.terrain.fine.DemSampler(parent,rendered=True)
    roi=before['roi'];synthetic=dict(w=2,h=2,meta=dict(georef=dict(bE=roi[0]+834500,bN=816500-roi[1],aE=roi[2]-roi[0],aN=-(roi[3]-roi[1]))),nativeMesh=dict(position=ground.reshape(-1).tolist(),index=list(range(len(ground)*3))))
    sampler=RenderedPatchSampler(synthetic,grid,grid)
    claim=reservations.claim('opus-preserve-neighbours-'+str(uuid.uuid4()),['private-opus-preserved-ground'],batch=BATCH,ttl=1800);assert claim['ok'];lease=claim['reservation']
    try:
        DOC.mkdir();LOCAL.mkdir();proof=patches.preserve_parent_under_projection(patch,domain,protected,sampler)
        save(DOC/'preservation.json',dict(proof=proof,accounts=accounts,sourceProjectionIntersectionM2=0,completeSourceFaces=len(t),oldGroundFaces=len(ground),fullAcceptance=False))
        save(DOC/'pre-fill-terrain.json',patch)
        fill=patches.fill_parent_only_holes(patch,parent,domain,complete_projection,sampler)
        boundary=patches.snap_boundary_to_parent(patch,domain,grid)
        save(DOC/'repair-proof.json',dict(parentOnlyHoleFill=fill,boundary=boundary))
        save(DOC/'pre-validation-terrain.json',patch)
        from opus_terrain_overlap_v1_20261016 import qualify
        patch['nativeMesh'].pop('sourceOverlap',None)
        overlap_sources=[Path(__file__),HERE/'opus_terrain_overlap_v1_20261016.py',ROOT/original['path'],CAP/'before-ground.json.gz',Path(patches.__file__)]
        qualify(patch,parent,DOC,helper.validate_patch,overlap_sources)
        refs += overlap_sources
        path=DOC/'private-terrain.json';save(path,patch);candidate=dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()),uids=uids);save(DOC/'terrain-candidates.json',[candidate]);inputs['patches']=[candidate];save(DOC/'neighbour-inputs.json.gz',inputs);save(DOC/'selection.json.gz',selection)
        tool=HERE/'check-neighbours.mjs'
        with(DOC/'neighbours.log').open('w')as log:subprocess.run(['node',str(tool),str(DOC.relative_to(ROOT))+'/'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=600)
        metric_tool=HERE/'acceptance-metrics-retained-group-parent.mjs';source=HERE/'local'/PAIR.name
        with(DOC/'metrics.log').open('w')as log:subprocess.run(['node',str(metric_tool),'--selection',str((DOC/'selection.json.gz').relative_to(ROOT)),'--candidates',str(source.relative_to(ROOT)),'--terrain-candidates',str((DOC/'terrain-candidates.json').relative_to(ROOT)),'--out',str((DOC/'metrics.json').relative_to(ROOT)),'--geometry-out',str((LOCAL/'runtime-geometry.json.gz').relative_to(ROOT))],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=900)
        checks=read(DOC/'neighbour-checks.json');metrics=read(DOC/'metrics.json');assert all(not row.get('error') for row in metrics['rows'])
        for report in [checks,metrics]:
            for p,h in report['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
        foundation_helper=module('opus_preserved_foundation',HERE/'xl-final-script-pass.py')
        actual=read(LOCAL/'runtime-geometry.json.gz')['rows']
        pairtri=np.concatenate([np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)] for g in actual])
        pairground=np.concatenate([np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3) for g in actual])
        pairpolygon=shapely.union_all([Polygon(r['source']['building']['rings'][0],r['source']['building']['rings'][1:]) for r in selection['rows']])
        foundation=foundation_helper.foundation_context(pairtri,pairground,pairpolygon)
        refs += [HERE/'xl-final-script-pass.py',Path(foundation_helper.s.context.shared.__file__)]
        summary=dict(changedParentExtent=domain,coarseCells=read(OLD/'summary.json')['coarseCells'],pairedFoundation=foundation,ordinaryRegressions=[r for r in checks['rows']if r['reasons']and not r['existingNative']],nativePending=[r['uid']for r in checks['rows']if r['existingNative']and r['reasons']],targetMetrics=metrics['rows'],fullAcceptance=False,liveChanges=False)
        save(DOC/'summary.json',summary);refs += [tool,metric_tool,CAP/'before-ground.json.gz',LOCAL/'runtime-geometry.json.gz',Path(patches.__file__),HERE/'rendered_patch_sampler.py',HERE/'resolve-pass.py']
        result=module('hotel_preserved_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'opus-pair-source-disjoint-actual-parent-preservation-v1',list(dict.fromkeys(refs)),dict(uids=uids+sorted(byuid),summary=summary,fullAcceptance=False,newlyInstalled=0))
        print(dict(jobId=result['jobId'],ordinaryRegressions=len(summary['ordinaryRegressions']),nativePending=summary['nativePending']),flush=True)
    finally:
        if reservations.owns(lease):assert reservations.release(lease)['ok']

if __name__=='__main__':main()
