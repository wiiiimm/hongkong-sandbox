"""Check exact originals against already verified, revision-bound terrain sheets.

No acquisition, new revision, geometry edits, source approval or publication.
"""
import argparse
import json
import sys
import uuid
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from exact_packed_world_geometry_20261009 import decode_original_world_triangles

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','terrain-check','capture']:ap.add_argument('--'+k,required=True)
    ap.add_argument('--uid',action='append',required=True);ap.add_argument('--owned',action='store_true');a=ap.parse_args()
    assert all(n.startswith('government-xl-') and '/' not in n for n in [a.batch,a.terrain_check,a.capture])
    assert 0<len(a.uid)==len(set(a.uid))<=8
    base=ROOT/'docs/astra-city/government-import';out=base/a.batch;lp=HERE/'local'/a.batch/'reservation.json';refs=[Path(__file__)];pins={}
    def take(batch,name):
        if batch not in pins:pins[batch]=authenticate(base/batch)[1];refs.append(base/batch/'result.json')
        p=base/batch/name;assert digest(p.read_bytes())==pins[batch][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    donor=take(a.terrain_check,'summary.json');inputs=take(a.terrain_check,'source-inputs.json')['inputs'];selection=take(a.capture,'selection.json.gz')
    assert donor['originalSourceRevisionsVerified'] and donor['sourceRevisionsExplicitlyBound'] and not donor['terrainRevisionChanges']
    assert set(inputs)==set(donor['sheets']) and all(v['priorNativeTerrainResultExists'] for v in inputs.values())
    selected=[r for r in selection['rows'] if r['uid'] in a.uid];assert len(selected)==len(a.uid)
    paths={tuple(r['sourceTerrainPaths']) for r in donor['rows'] if r['status']=='original-terrain-checked'};assert len(paths)==1
    paths=next(iter(paths));assert paths
    if not a.owned:
        assert not out.exists() and not lp.parent.exists()
        claim=reservations.claim('cached-multisheet-ground-'+str(uuid.uuid4()),sorted({'building:'+u for u in a.uid}|{'source-terrain:'+s for s in inputs}),batch=a.batch,ttl=3600);assert claim['ok'],claim
        return execute_reserved(claim['reservation'],lp,[sys.executable,__file__,*sys.argv[1:],'--owned'])
    lease=read(lp);assert reservations.owns(lease) and not out.exists()
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest)
    decoder=module('cached_multisheet_decoder',HERE/'xl-second-pass.py');final=module('cached_multisheet_foundation',HERE/'xl-final-script-pass.py');ground=[]
    for name in paths:
        p=ROOT/name;assert digest(p.read_bytes())==pins[a.terrain_check][name];refs.append(p);gltf=read(p)
        for buffer in gltf.get('buffers',[]):
            q=p.parent/buffer['uri'];assert q.resolve().is_relative_to(p.parent.resolve()) and digest(q.read_bytes())==pins[a.terrain_check][str(q.relative_to(ROOT))];refs.append(q)
        ground.append(decoder.terrain_triangles(p))
    terrain=np.concatenate(ground);assert np.isfinite(terrain).all();rows=[]
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        for row in selected:
            native=row['native'];sheet=row['candidate']['entry']['sourceTile'];record=inputs[sheet]
            assert record['cacheKey']==native['cacheKey'] and record['resultSHA256']==native['resultSha']
            actual=db.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s',(native['cacheKey'],)).fetchone();assert actual and actual[0]==native['resultSha']
            assert next(m for m in actual[1]['models'] if m['modelId']==row['modelId'])==native['model']
            tile=ROOT/'3d-viewer'/row['source']['tile'];assert digest(tile.read_bytes())==row['source']['tileSHA256'] and next(f for f in read(tile)['buildings'] if f['uid']==row['uid'])==row['source']['building'];refs.append(tile)
            asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];refs.append(asset);tri=decode_original_world_triangles(asset.read_bytes());assert len(tri)==row['triangles']
            lo,hi=tri.min((0,1)),tri.max((0,1));local=terrain[(terrain[:,:,0].max(1)>=lo[0]-10)&(terrain[:,:,0].min(1)<=hi[0]+10)&(terrain[:,:,2].max(1)>=lo[2]-10)&(terrain[:,:,2].min(1)<=hi[2]+10)]
            form=row['source']['building'];foundation=final.foundation_context(tri,local,Polygon(form['rings'][0],form['rings'][1:]))
            rows.append(dict(uid=row['uid'],sourceSHA256=row['sourceSHA256'],nativeResultSHA256=native['resultSha'],sheet=sheet,status='original-terrain-checked',sourceTerrainPaths=list(paths),originalTerrainFoundation=foundation,installationApproved=False))
    assert digest(manifest.read_bytes())==selection['manifestSHA256'] and reservations.owns(lease)
    result=dict(uids=a.uid,rows=rows,sheets=donor['sheets'],originalSourceRevisionsVerified=True,sourceRevisionsExplicitlyBound=True,terrainRevisionChanges=[],downloads=0,sourceGeometryChanges=0,sourcePoseChanges=0,physicalAcceptance=False,installationApproved=False,publication=False,qualification=__doc__+' Each selected source native cache and result is independently matched to the authenticated donor sheet source-input record and current Neon native result. All terrain GLTF/buffer bytes are pinned. Full original source face foundation diagnostic only; current-scene checks remain separate.')
    save(out/'summary.json',result);refs.extend(HERE/n for n in ['xl-second-pass.py','xl-final-script-pass.py','exact_packed_world_geometry_20261009.py'])
    module('cached_multisheet_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'fresh-exact-original-verified-cached-multisheet-terrain-check',list(dict.fromkeys(refs)),result)
    print([dict(uid=r['uid'],buried=r['originalTerrainFoundation']['fullyBuriedTriangles'],upward=r['originalTerrainFoundation']['fullyBuriedUpwardTriangles'],coverage=r['originalTerrainFoundation']['completeTerrainTriangles'])for r in rows],flush=True)

if __name__=='__main__':main()
