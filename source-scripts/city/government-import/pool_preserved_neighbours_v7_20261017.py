"""Preserve actual old ground outside the complete original pool projection."""
from pathlib import Path
import subprocess,uuid
import numpy as np
import shapely
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
from rendered_patch_sampler import RenderedPatchSampler
import native_patch_resolution as patches
from exact_runtime_coplanar_consolidation_20261010 import consolidate

BATCH='government-xl-sham-shui-po-pool-preserved-neighbours-v7-20261017'
BASE=ROOT/'docs/astra-city/government-import';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
CAP=BASE/'government-xl-sham-shui-po-pool-basic-ground-capture-v2-20261017'
OLD=BASE/'government-xl-sham-shui-po-pool-preserved-neighbours-v1-20261016'
FINITE=BASE/'government-xl-sham-shui-po-pool-basic-finite-v1-20261017'
FINITE2=BASE/'government-xl-sham-shui-po-pool-basic-finite-v2-20261017'
FINITE3=BASE/'government-xl-sham-shui-po-pool-basic-finite-v3-20261017'
NEIGH=BASE/'government-xl-sham-shui-po-pool-private-neighbours-v1-20261016'


def qualify_overlap(patch,doc,refs):
    # New exact terrain bytes require new proof; never transfer the old approval.
    mesh=patch['nativeMesh'];mesh.pop('sourceOverlap',None)
    raw=doc/'unapproved-terrain.json';save(raw,patch)
    tri=np.asarray(mesh['position'],dtype='<f4').astype(float).reshape(-1,3)[np.asarray(mesh['index']).reshape(-1,3)]
    polys=shapely.polygons(tri[:,:,[0,2]]);valid=shapely.area(polys)>1e-10;ids=np.flatnonzero(valid);ps=polys[valid]
    pairs=shapely.STRtree(ps).query(ps,predicate='intersects');rows=[];samples=0;maxerror=0
    for ia,ib in zip(*pairs):
        if ia>=ib:continue
        q=ps[ia].intersection(ps[ib])
        if q.area<=1e-10:continue
        coords=shapely.get_coordinates(q);errors=[]
        for face in [tri[ids[ia]],tri[ids[ib]]]:
            a,b,c=face;u=b-a;v=c-a;delta=coords-a[[0,2]];det=u[0]*v[2]-u[2]*v[0];assert det!=0
            s=(delta[:,0]*v[2]-delta[:,1]*v[0])/det;t=(u[0]*delta[:,1]-u[2]*delta[:,0])/det;bary=a[1]+s*u[1]+t*v[1];n=np.cross(u,v);plane=a[1]-(n[0]*delta[:,0]+n[2]*delta[:,1])/n[1]
            errors.append(float(np.max(np.abs(bary-plane))));samples+=len(coords)
        maxerror=max(maxerror,*errors);rows.append(dict(faces=[int(ids[ia]),int(ids[ib])],areaM2=q.area,equationErrorsM=errors))
    excess=float(shapely.area(ps).sum()-shapely.union_all(ps).area)
    if rows:
        assert maxerror<.01
        ref=lambda p:dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
        sourcefiles=[raw,Path(__file__),Path(patches.__file__),CAP/'before-ground.json.gz',OLD/'private-terrain.json']
        evidence=doc/'highest-surface-proof.json'
        save(evidence,dict(stagedGeometrySha256=ref(raw)['sha256'],nativeProjectedExcessM2=excess,float32HighestRayAgreement=dict(samples=samples,maxError=maxerror,rows=rows,method='All positive overlap polygons; affine plane and barycentric equations at every polygon vertex, bounding MAX error. Separate runtime sampler checks remain mandatory.'),source=dict(files=[ref(p) for p in sourcefiles])))
        mesh['sourceOverlap']=dict(policy='highest-native-surface',measuredProjectedExcessM2=excess,evidencePath=ref(evidence)['path'],evidenceSHA256=ref(evidence)['sha256']);refs.extend(sourcefiles)

def main():
    assert not DOC.exists()and not LOCAL.exists()
    refs=[Path(__file__)];pins={}
    with connect()as c:
        c.execute('SET TRANSACTION READ ONLY')
        for folder in [CAP,OLD,NEIGH,FINITE,FINITE2,FINITE3,BASE/'government-xl-sham-shui-po-pool-native-scope-v1-20261016']:
            r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
            for ref in r['evidenceRefs']:
                assert ref['path']not in pins or pins[ref['path']]==ref['sha256'];pins[ref['path']]=ref['sha256']
    for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
    original=read(OLD/'terrain-candidates.json')[0];patch=read(ROOT/original['path']);domain=read(NEIGH/'summary.json')['changedParentExtent'];selection=read(OLD/'selection.json.gz');uid=selection['rows'][0]['uid']
    geometry=read(HERE/'local/government-xl-sham-shui-po-pool-current-ground-v1-20261016/runtime-geometry.json.gz')['rows'];t=np.concatenate([np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)] for g in geometry])
    complete_projection=shapely.union_all([shapely.MultiPoint(face[:,[0,2]]).convex_hull for face in t]);exclude=complete_projection.buffer(.01,join_style='mitre')
    inputs=read(NEIGH/'neighbour-inputs.json.gz');byuid={r['building']['uid']:r for r in inputs['rows']};protect=[];accounts=[]
    actors=read(CAP/'basic-actors.json.gz')['rows'];assert len(actors)==84
    failures=read(FINITE/'summary.json');assert failures['all84ActorsComplete']
    affected={r['uid'] for r in failures['rows'] if r['introducedUnproved'] or r['afterUncovered']}
    assert affected=={'landsd/819:0','landsd/164001:0','landsd/228000:0','landsd/246023:0','landsd/264577:0'}
    newest=read(FINITE2/'summary.json');assert newest['all84ActorsComplete']
    affected.update(r['uid'] for r in newest['rows'] if r['introducedUnproved'] or r['afterUncovered'])
    assert len(affected)==7
    latest=read(FINITE3/'summary.json');assert latest['all84ActorsComplete']
    affected.update(r['uid'] for r in latest['rows'] if r['introducedUnproved'] or r['afterUncovered'])
    assert len(affected)==8 and 'way/174098287:0' in affected
    for actor in actors:
        if actor['uid'] not in affected:continue
        t_actor=np.asarray(actor['position']).reshape(-1,3)[np.asarray(actor['index']).reshape(-1,3)]
        projection=shapely.union_all([shapely.MultiPoint(face[:,[0,2]]).convex_hull for face in t_actor])
        p=projection.convex_hull.buffer(.01,join_style='mitre');safe=p.difference(exclude)
        accounts.append(dict(uid=actor['uid'],completeRenderedFaces=len(t_actor),preservationBoundary='Complete actor convex hull; all original rendered projections retained, source exclusion unchanged',protectedAreaM2=safe.area,excludedSourceOverlapAreaM2=p.intersection(exclude).area))
        if safe.area>1e-8:protect.append(safe)
    native_bounds=read(BASE/'government-xl-sham-shui-po-pool-native-scope-v1-20261016/complete-bounds.json.gz')['rows']
    native=next(r for r in native_bounds if r['uid']=='landsd/99395:0')
    for lo,hi in native['completeFourWorldBounds']:
        p=shapely.box(lo[0],lo[2],hi[0],hi[2]).buffer(.01,join_style='mitre')
        assert p.intersection(exclude).area==0
        protect.append(p)
    accounts.append(dict(uid=native['uid'],policy='Preserve current ground under every complete four-world bound; full native regression still required.'))
    protected=shapely.union_all(protect).intersection(shapely.box(*domain));assert protected.area>0 and protected.intersection(complete_projection).area==0
    before=read(CAP/'before-ground.json.gz');ground=np.asarray(before['completeRelevantDrawnTriplets']).reshape(-1,3,3);polys=shapely.polygons(ground[:,:,[0,2]]);valid=shapely.area(polys)>1e-10
    covered=shapely.union_all(polys[valid]);missing=protected.difference(covered);print(dict(protectedM2=protected.area,missingM2=missing.area,missingBounds=missing.bounds),flush=True)
    preservationCoverage=dict(requestedAreaM2=protected.area,uncoveredAreaM2=missing.area,uncoveredGeoJSON=shapely.to_geojson(missing),policy='Preserve only existing drawn surface; uncovered slivers receive no preservation claim and remain subject to complete actor checks.')
    protected=protected.intersection(covered)
    assert protected.difference(covered).area<1e-8
    helper=module('hotel_preserved_parent',HERE/'resolve-pass.py');parent=read(ROOT/'3d-viewer/city/data/terrain.json');grid=helper.terrain.fine.DemSampler(parent,rendered=True)
    roi=before['roi'];synthetic=dict(w=2,h=2,meta=dict(georef=dict(bE=roi[0]+834500,bN=816500-roi[1],aE=roi[2]-roi[0],aN=-(roi[3]-roi[1]))),nativeMesh=dict(position=ground.reshape(-1).tolist(),index=list(range(len(ground)*3))))
    sampler=RenderedPatchSampler(synthetic,grid,grid)
    claim=reservations.claim('pool-preserve-neighbours-'+str(uuid.uuid4()),['private-pool-preserved-ground'],batch=BATCH,ttl=1800);assert claim['ok'];lease=claim['reservation']
    try:
        DOC.mkdir();LOCAL.mkdir();save(DOC/'preservation-coverage.json',preservationCoverage);proof=patches.preserve_parent_under_projection(patch,domain,protected,sampler)
        save(DOC/'preservation.json',dict(proof=proof,accounts=accounts,sourceProjectionIntersectionM2=0,completeSourceFaces=len(t),oldGroundFaces=len(ground),fullAcceptance=False))
        save(DOC/'pre-fill-terrain.json',patch)
        fill=patches.fill_parent_only_holes(patch,parent,domain,complete_projection,sampler)
        boundary=patches.snap_boundary_to_parent(patch,domain,grid)
        save(DOC/'repair-proof.json',dict(parentOnlyHoleFill=fill,boundary=boundary))
        save(DOC/'pre-validation-terrain.json',patch)
        faces=np.asarray(patch['nativeMesh']['position'],dtype='<f4').astype(float).reshape(-1,3)[np.asarray(patch['nativeMesh']['index']).reshape(-1,3)]
        consolidated,certificate=consolidate(faces)
        save(DOC/'exact-coplanar-certificate.json.gz',certificate)
        patch['nativeMesh']['position']=consolidated.reshape(-1).tolist()
        patch['nativeMesh']['index']=list(range(consolidated.size//3))
        refs.extend([HERE/n for n in ['exact_runtime_coplanar_consolidation_20261010.py','exact_coplanar_boundary_census_20261010.py','exact_runtime_coplanar_groups_20261010.py']])
        print(dict(beforeFaces=len(faces),afterFaces=len(consolidated)),flush=True)
        qualify_overlap(patch,DOC,refs)
        assert len(patch['nativeMesh']['index'])//3<=25000, 'Final terrain exceeds existing triangle budget'
        helper.validate_patch(patch,parent)
        path=DOC/'private-terrain.json';save(path,patch);candidate=dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()),uids=[r['uid'] for r in selection['rows']],replaces=original['replaces']);save(DOC/'terrain-candidates.json',[candidate]);inputs['patches']=[candidate];save(DOC/'neighbour-inputs.json.gz',inputs);save(DOC/'selection.json.gz',selection)
        tool=HERE/'check-neighbours.mjs'
        with(DOC/'neighbours.log').open('w')as log:subprocess.run(['node',str(tool),str(DOC.relative_to(ROOT))+'/'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=600)
        metric_tool=HERE/'acceptance-metrics-retained-group-parent.mjs';source=HERE/'local/government-xl-sham-shui-po-pool-current-ground-v1-20261016'
        with(DOC/'metrics.log').open('w')as log:subprocess.run(['node',str(metric_tool),'--selection',str((DOC/'selection.json.gz').relative_to(ROOT)),'--candidates',str(source.relative_to(ROOT)),'--terrain-candidates',str((DOC/'terrain-candidates.json').relative_to(ROOT)),'--out',str((DOC/'metrics.json').relative_to(ROOT)),'--geometry-out',str((LOCAL/'runtime-geometry.json.gz').relative_to(ROOT))],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=900)
        checks=read(DOC/'neighbour-checks.json');metrics=read(DOC/'metrics.json');assert not any(r.get('error') for r in metrics['rows'])
        for report in [checks,metrics]:
            for p,h in report['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
        summary=dict(changedParentExtent=domain,coarseCells=patch['coarseCells'],ordinaryRegressions=[r for r in checks['rows']if r['reasons']and not r['existingNative']],nativePending=[r['uid']for r in checks['rows']if r['existingNative']and r['reasons']],targetMetrics=metrics['rows'],fullAcceptance=False,liveChanges=False)
        save(DOC/'summary.json',summary);refs += [tool,metric_tool,CAP/'before-ground.json.gz',LOCAL/'runtime-geometry.json.gz',Path(patches.__file__),HERE/'rendered_patch_sampler.py',HERE/'resolve-pass.py']
        result=module('hotel_preserved_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'pool-source-disjoint-actual-parent-preservation-v1',list(dict.fromkeys(refs)),dict(uids=[uid]+sorted(byuid),summary=summary,fullAcceptance=False,newlyInstalled=0,privateTerrainGeometryChanged=True,liveAssetsChanged=False))
        print(dict(jobId=result['jobId'],ordinaryRegressions=len(summary['ordinaryRegressions']),nativePending=summary['nativePending']),flush=True)
    finally:
        if reservations.owns(lease):assert reservations.release(lease)['ok']

if __name__=='__main__':main()
