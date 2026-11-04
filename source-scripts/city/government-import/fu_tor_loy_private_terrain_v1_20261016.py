from pathlib import Path
import subprocess,uuid
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
import fu_tor_loy_original_terrain_v1_20261016 as prior

BATCH='government-xl-fu-tor-loy-private-terrain-v1-20261016'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
LOCAL=HERE/'local'/BATCH

def main():
    assert not DOC.exists()and not LOCAL.exists()
    receipt=read(prior.DOC/'result.json');refs=[Path(__file__),Path(prior.__file__),prior.DOC/'result.json']
    with connect()as c:
        c.execute('SET TRANSACTION READ ONLY')
        assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
    for ref in receipt['evidenceRefs']:
        assert digest((ROOT/ref['path']).read_bytes())==ref['sha256'];refs.append(ROOT/ref['path'])
    manifest=ROOT/'3d-viewer/city/data/manifest.json';manifestsha=digest(manifest.read_bytes())
    selection=read(prior.PRIOR/'selection.json.gz');assert selection['manifestSHA256']==manifestsha
    row=selection['rows'][0];entry=row['candidate']['entry'];parentpath=ROOT/'3d-viewer/city/data/terrain.json';parent=read(parentpath)
    helper=module('hotel_private_patch_constructor',HERE/'resolve-pass.py');foundation_helper=module('hotel_private_patch_foundation',HERE/'xl-final-script-pass.py')
    current=read(manifest);oldentry=next(t for t in current['terrainPatches'] if t['url']=='city/data/government-native-72357-0.json');oldpath=ROOT/'3d-viewer'/oldentry['url'];old=read(oldpath);refs.append(oldpath)
    retained=[]
    for url in current['officialModelCatalogues']:
        cp=ROOT/'3d-viewer'/url
        for model in read(cp)['models']:
            if model['uid']=='landsd/72357:0':retained.append(model);refs.append(cp)
    assert len(retained)==1
    allbounds=np.asarray([entry['worldBounds'],retained[0]['worldBounds']]);combined=[allbounds[:,0,:].min(axis=0).tolist(),allbounds[:,1,:].max(axis=0).tolist()]
    cells=helper.rectangle_for(combined,parent);cells=[min(cells[0],old['coarseCells'][0]),min(cells[1],old['coarseCells'][1]),max(cells[2],old['coarseCells'][2]),max(cells[3],old['coarseCells'][3])]
    group=dict(uids=[row['uid'],'landsd/72357:0'],cells=cells);bounds=helper.extent(cells,parent)
    pieces=[];sources=[]
    for relative in read(prior.DOC/'summary.json')['terrainPaths']:
        path=ROOT/relative;t=helper.context.triangles(path)
        mask=(t[:,:,0].max(axis=1)>=bounds[0])&(t[:,:,0].min(axis=1)<=bounds[2])&(t[:,:,2].max(axis=1)>=bounds[1])&(t[:,:,2].min(axis=1)<=bounds[3]);pieces.append(t[mask]);sources.append(dict(path=relative,sha256=digest(path.read_bytes()),provenance=str((prior.DOC/'summary.json').relative_to(ROOT))))
    claim=reservations.claim('museum-private-terrain-'+str(uuid.uuid4()),['private-original-terrain:'+row['uid']],batch=BATCH,ttl=1800);assert claim['ok'];lease=claim['reservation']
    try:
        DOC.mkdir();LOCAL.mkdir()
        lo,hi=combined;core=[lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]
        validate=helper.validate_patch
        def capture_then_validate(p,parent):
            save(DOC/'pre-validation-terrain.json',p);return validate(p,parent)
        helper.validate_patch=capture_then_validate
        patch=helper.make_patch(group,parent,np.concatenate(pieces),sources,native_core=core)
        patchpath=DOC/'private-terrain.json';save(patchpath,patch)
        candidates=[dict(path=str(patchpath.relative_to(ROOT)),sha256=digest(patchpath.read_bytes()),replaces=dict(url=oldentry['url'],sha256=digest(oldpath.read_bytes()),retainedUids=['landsd/72357:0']))];save(DOC/'terrain-candidates.json',candidates);save(DOC/'selection.json.gz',selection)
        original_local=HERE/'local'/prior.PRIOR.name
        tool=HERE/'acceptance-metrics-retained-group-parent.mjs'
        cmd=['node',str(tool),'--selection',str((DOC/'selection.json.gz').relative_to(ROOT)),'--candidates',str(original_local.relative_to(ROOT)),'--terrain-candidates',str((DOC/'terrain-candidates.json').relative_to(ROOT)),'--out',str((DOC/'metrics.json').relative_to(ROOT)),'--geometry-out',str((LOCAL/'runtime-geometry.json.gz').relative_to(ROOT))]
        with(DOC/'worker.log').open('w')as log:subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=900)
        metrics=read(DOC/'metrics.json');assert not metrics['rows'][0].get('error'),metrics['rows'][0]
        g=read(LOCAL/'runtime-geometry.json.gz')['rows'][0];t=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3);b=row['source']['building']
        foundation=foundation_helper.foundation_context(t,ground,Polygon(b['rings'][0],b['rings'][1:]))
        save(DOC/'summary.json',dict(uid=row['uid'],changedParentExtent=bounds,coarseCells=group['cells'],originalCore=core,privateTerrainFaces=len(patch['nativeMesh']['index'])//3,foundation=foundation,metrics=metrics['rows'][0],neighboursChecked=False,fullAcceptance=False,liveTerrainChanged=False))
        for p,h in metrics['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
        refs += [LOCAL/'runtime-geometry.json.gz',Path(helper.__file__),Path(foundation_helper.__file__),Path(foundation_helper.s.context.shared.__file__)]
        assert digest(manifest.read_bytes())==manifestsha
        result=module('hotel_private_terrain_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'unchanged-fu-tor-loy-private-original-terrain-renderer-v1',refs,dict(uids=[row['uid']],foundation=foundation,fullAcceptance=False,newlyInstalled=0,liveTerrainChanged=False))
        print(dict(jobId=result['jobId'],summary=read(DOC/'summary.json')),flush=True)
    finally:
        if reservations.owns(lease):assert reservations.release(lease)['ok']

if __name__=='__main__':main()
