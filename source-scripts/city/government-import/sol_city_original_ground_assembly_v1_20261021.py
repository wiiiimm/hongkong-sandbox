"""Whole original Sol City assembly against recovered exact source terrain."""
from pathlib import Path
import subprocess,numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-sol-city-original-ground-assembly-v1-20261021';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;OLD=BASE/'government-xl-sol-city-original-support-20261006';REC=BASE/'government-xl-sol-city-neighbour-recovery-v1-20261021'
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  for d in [OLD,REC]:
   r=read(d/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json');pins[d]={e['path']:e['sha256']for e in r['evidenceRefs']}
 def take(d,p):
  assert digest(p.read_bytes())==pins[d][str(p.relative_to(ROOT))];refs.append(p);return read(p)
 sources=take(OLD,OLD/'support-inputs.json')['sources'];rec=take(REC,REC/'recovery.json');neighbour=rec['rows'][0];tile=ROOT/'3d-viewer/city/data/tiles/-7_-9.json';forms={b['uid']:b for b in read(tile)['buildings']};refs.append(tile)
 assets={r['uid']:(ROOT/r['candidate']['path'],r['candidate']['entry']['sha256'])for r in sources};assets[neighbour['uid']]=(ROOT/neighbour['assetPath'],neighbour['sourceSHA256']);worlds={}
 for uid,(path,sha)in assets.items():assert digest(path.read_bytes())==sha;refs.append(path);worlds[uid]=decode_original_world_triangles(path.read_bytes())
 terrainpaths=rec['recovery']['terrainPaths'];assert len(terrainpaths)==1;path=ROOT/terrainpaths[0];take(REC,path)
 for b in read(path)['buffers']:
  p=path.parent/b['uri'];assert digest(p.read_bytes())==pins[REC][str(p.relative_to(ROOT))];refs.append(p)
 helper=module('sol_ground_decoder',HERE/'xl-second-pass.py');helper.LOCAL=LOCAL;ground=np.asarray(helper.terrain_triangles(path),dtype='<f8');save(LOCAL/'original-terrain.json.gz',dict(triangles=ground.tolist(),source=str(path.relative_to(ROOT))))
 final=module('sol_ground_foundation',HERE/'xl-final-script-pass.py');tool=HERE/'wave_retained_basic_support_v1_20261017.mjs';summary=[]
 for uid,tri in worlds.items():
  form=forms[uid];support=worlds['landsd/273271:0']if uid in ['landsd/273080:0','landsd/260034:0']else ground;combined=np.concatenate([ground,support])if support is not ground else ground
  f=final.foundation_context(tri,combined,Polygon(form['rings'][0],form['rings'][1:]));folder=DOC/uid.split('/')[1];save(folder/'foundation.json',f);save(folder/'input.json.gz',dict(podium=support.tolist(),rows=[dict(uid=uid,position=tri.reshape(-1).tolist(),index=list(range(len(tri)*3)))]))
  subprocess.run(['/home/williamli/.nvm/versions/node/v24.18.0/bin/node',str(tool),str(folder.relative_to(ROOT))],cwd=ROOT,check=True);r=read(folder/'support.json.gz');proof=r['rows'][0]['proof']
  for p,h in r['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
  item=dict(uid=uid,foundation={k:v for k,v in f.items()if k!='components'},samples=proof['samples'],strictContacts=proof['strictContacts'],unresolved=len(proof['unresolved']));summary.append(item);print(item,flush=True)
 refs.extend([tool,HERE/'xl-second-pass.py',HERE/'xl-final-script-pass.py',HERE/'exact_packed_world_geometry_20261009.py']);refs.extend(p for p in LOCAL.rglob('*')if p.is_file());save(DOC/'summary.json',dict(rows=summary,installationApproved=False));module('sol_ground_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-original-assembly-ground-foundations',refs,dict(uids=list(worlds),rows=summary,installationApproved=False,sourceGeometryChanges=0))
if __name__=='__main__':main()
