"""Check exact cached government terrain under explicit originals; no acquisition or publication."""
import argparse
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect,NATIVE_RUN
from china_ferry_current_foundations_v1_20261020 import authenticate
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from primrose_compound_foundation_v2_20261015 import module


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['batch','runtime','attributes']:p.add_argument('--'+name,required=True)
    p.add_argument('--terrain',action='append',required=True)
    p.add_argument('--uid',action='append',required=True)
    a=p.parse_args();base=ROOT/'docs/astra-city/government-import';out=base/a.batch;local=HERE/'local'/a.batch
    assert a.batch.startswith('government-xl-')and '/'not in a.batch and not out.exists()and not local.exists()
    refs=[Path(__file__)];pins={}
    def take(batch,path):
        if batch not in pins:pins[batch]=authenticate(base/batch)[1];refs.append(base/batch/'result.json')
        assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    selected=take(a.runtime,base/a.runtime/'selection.json.gz');wanted=set(a.uid);assert len(wanted)==len(a.uid)
    rows=[r for r in selected['rows']if r['uid']in wanted];assert len(rows)==len(wanted)>0
    attrs=take(a.attributes,base/a.attributes/'attributes.json.gz');assert attrs['startEndAllInputsVerified'];attrs={r['uid']:r for r in attrs['rows']}
    captured=take(a.runtime,HERE/'local'/a.runtime/'runtime-geometry.json.gz');captured={r['uid']:r for r in captured['rows']}
    keys={r['native']['cacheKey']for r in rows};assert len(keys)==1;key=next(iter(keys))
    with connect()as db:
        db.execute('SET TRANSACTION READ ONLY')
        found=db.execute('SELECT r.result_sha,r.result FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,key)).fetchone()
    assert found and all(r['native']['resultSha']==found[0]for r in rows)
    original=found[1];terrain_records=original['terrain'];assert terrain_records
    paths=[(ROOT/name).resolve()for name in a.terrain];assert len(set(paths))==len(paths)==len(terrain_records)
    bindings=[]
    for record in terrain_records:
        matches=[path for path in paths if path.name==Path(record['sourceEntry']).name];assert len(matches)==1
        path=matches[0];assert path.is_relative_to(ROOT)
        for name,sha in record['sourceHashes'].items():
            source=path.parent/Path(name).name;assert digest(source.read_bytes())==sha;refs.append(source)
        bindings.append(dict(path=str(path.relative_to(ROOT)),record=record))
    decoder=module('cached_original_terrain_decoder',HERE/'xl-second-pass.py');decoder.LOCAL=local
    ground=np.concatenate([decoder.terrain_triangles(path)for path in paths]);assert len(ground)==sum(r['triangles']for r in terrain_records)
    for proofpath in (local/'terrain-repairs').glob('*/proof.json'):
        proof=read(proofpath);assert proof['sourceGeometryChanged']is False and proof['geometryProof']['sourcePositionsAndIndicesPreserved']
    final=module('cached_original_terrain_foundation',HERE/'xl-final-script-pass.py');results=[]
    for row in rows:
        uid=row['uid'];attr=attrs[uid];asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256']==attr['sourceSHA256']==captured[uid]['sourceSHA256'];refs.append(asset)
        assert next(m for m in original['models']if m['modelId']==row['modelId'])==row['native']['model']
        tile=ROOT/'3d-viewer'/row['source']['tile'];assert digest(tile.read_bytes())==row['source']['tileSHA256'];assert next(f for f in read(tile)['buildings']if f['uid']==uid)==row['source']['building'];refs.append(tile)
        ix=np.asarray(attr['completeOriginalIndex']).reshape(-1,3)
        worlds=dict(original=decode_original_world_triangles(asset.read_bytes()),**{mode:np.asarray(attr[field],dtype='<f8').reshape(-1,3)[ix]for mode,field in [('literal','completeLiteralWorldPosition'),('leftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('balancedF32','completeExplicitBalancedFloat32WorldPosition')]})
        runtime=captured[uid];assert np.array_equal(worlds['literal'],np.asarray(runtime['position']).reshape(-1,3)[np.asarray(runtime['index']).reshape(-1,3)])
        for mode,tri in worlds.items():
            assert len(tri)==row['triangles'];lo,hi=tri.min((0,1)),tri.max((0,1))
            keep=(ground[:,:,0].max(1)>=lo[0]-10)&(ground[:,:,0].min(1)<=hi[0]+10)&(ground[:,:,2].max(1)>=lo[2]-10)&(ground[:,:,2].min(1)<=hi[2]+10)
            f=final.foundation_context(tri,ground[keep],Polygon(row['source']['building']['rings'][0],row['source']['building']['rings'][1:]))
            save(out/(uid.split('/')[1]+'--'+mode+'.json'),dict(uid=uid,mode=mode,foundation=f,sourceWorldSHA256=digest(tri.astype('<f8').tobytes())))
            result=dict(uid=uid,mode=mode,triangles=f['triangles'],covered=f['completeTerrainTriangles'],buried=f['fullyBuriedTriangles'],buriedUpward=f['fullyBuriedUpwardTriangles'],buriedAreaFraction=f['fullyBuriedAreaFraction'],minimumGapM=f['minimumGapM'],terrainContextFaces=int(keep.sum()))
            results.append(result);print(result,flush=True)
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selected['manifestSHA256'];refs.append(manifest)
    save(out/'native-terrain-binding.json',dict(nativeRun=NATIVE_RUN,nativeStageKey=key,nativeStageSHA256=found[0],sources=bindings))
    result=dict(uids=sorted(wanted),rows=results,sourceSHA256ByUid={r['uid']:r['sourceSHA256']for r in rows},originalTerrainFaces=len(ground),originalTerrainWorldSHA256=digest(ground.astype('<f8').tobytes()),currentManifestSHA256=selected['manifestSHA256'],networkDownloadBytes=0,sourceGeometryChanges=0,sourcePoseChanges=0,terrainInstalled=False,physicalAcceptance=False,installationApproved=False,publication=False,qualification='Exact native-run terrain glTF/buffer hashes verified from existing cache; complete original decoder positions/indices preserved. Foundations are against original terrain context only, not a staged replacement or current drawn terrain. No terrain publication, clipping, support acceptance or model edits.')
    save(out/'summary.json',result);refs.extend(path for path in local.rglob('*')if path.is_file());refs.extend([HERE/'xl-second-pass.py',HERE/'xl-final-script-pass.py',HERE/'exact_packed_world_geometry_20261009.py'])
    module('cached_original_terrain_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'exact-cached-government-terrain-four-world-foundation-diagnostic',refs,result)


if __name__=='__main__':main()
