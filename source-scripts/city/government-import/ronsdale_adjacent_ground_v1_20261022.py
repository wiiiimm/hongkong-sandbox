"""Recover exact adjacent government terrain and complete Ronsdale podium diagnosis."""
from pathlib import Path
import uuid,numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-ronsdale-adjacent-ground-v1-20261022';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH

def main():
 assert not DOC.exists();uid='landsd/233771:0';refs=[Path(__file__)]
 def take(batch,p):
  folder=BASE/batch;_,pins=authenticate(folder);assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.extend([folder/'result.json',p]);return read(p)
 old='government-xl-ronsdale-podium-original-ground-v1-20261022';original=take(old,HERE/'local'/old/'original-terrain.json.gz');row=take(old,BASE/old/'selection.json.gz')['rows'][0]
 cap='government-xl-remaining-forty-assembly-runtime-v1-20261021';g=next(r for r in take(cap,HERE/'local'/cap/'runtime-geometry.json.gz')['rows']if r['uid']==uid);assert g['sourceSHA256']==row['sourceSHA256']
 key='fcf57290a127afed55a48d0bd6f058464d03ff1c88b8bcb65a8a85289adf2846';sheet='11-SE-11B'
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');sha,result=c.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s',(key,)).fetchone();prior=c.execute("SELECT result-'models' FROM astra_modelling.city_source_directories WHERE sheet=%s ORDER BY created_at DESC LIMIT 1",(sheet,)).fetchone()[0]
 assert sha=='f3cda538ccab32121b2ddaeec0f4ae0b0947f28ba1c4d0a48f1a846cde4253cc'
 claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['building:'+uid,'source-terrain:'+sheet],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  decoder=module('ronsdale_adjacent_decode',HERE/'xl-second-pass.py');decoder.LOCAL=LOCAL;recovery=decoder.source_sheet(sheet,[],prior,{},[]);paths=[ROOT/p for p in recovery['terrainPaths']];assert len(paths)==1
  terrain=result['terrain'][0]
  for name,h in terrain['sourceHashes'].items():
   p=paths[0].parent/Path(name).name;assert digest(p.read_bytes())==h;refs.append(p)
  adj=decoder.terrain_triangles(paths[0]);tri=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];lo,hi=tri.min((0,1)),tri.max((0,1));adj=adj[(adj[:,:,0].max(1)>=lo[0]-10)&(adj[:,:,0].min(1)<=hi[0]+10)&(adj[:,:,2].max(1)>=lo[2]-10)&(adj[:,:,2].min(1)<=hi[2]+10)];ground=np.concatenate([np.asarray(original['triangles']),adj]);b=row['source']['building'];f=module('ronsdale_foundation',HERE/'xl-final-script-pass.py').foundation_context(tri,ground,Polygon(b['rings'][0],b['rings'][1:]))
  save(LOCAL/'original-terrain.json.gz',dict(triangles=ground.tolist(),adjacentPaths=[str(p.relative_to(ROOT))for p in paths]));refs.append(LOCAL/'original-terrain.json.gz');save(DOC/'source-recovery.json',dict(recovery=recovery,nativeCacheKey=key,nativeResultSHA256=sha,terrain=terrain))
  r=dict(uids=[uid],uid=uid,sourceSHA256=row['sourceSHA256'],originalTerrainFoundation=f,installationApproved=False,sourceGeometryChanges=0);save(DOC/'summary.json',r)
  refs.extend([HERE/'xl-second-pass.py',HERE/'xl-final-script-pass.py']);refs.extend(p for p in LOCAL.rglob('*.json')if p.is_file());module('ronsdale_adjacent_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-adjacent-original-terrain-foundation',refs,r);print(dict(covered=f['completeTerrainTriangles'],faces=f['triangles'],buried=f['fullyBuriedTriangles']),flush=True)
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
