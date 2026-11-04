"""Compare complete original models with exact archived government terrain; diagnostic only."""
from pathlib import Path
import subprocess,numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';SRC=BASE/'government-xl-tko-podium-current-terrain-v2-20261021';BATCH='government-xl-tko-podium-original-ground-v1-20261021';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH

def main():
 assert not DOC.exists();receipt=read(SRC/'result.json');pins={}
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for e in receipt['evidenceRefs']:
  assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 rows=read(SRC/'selection.json.gz')['rows'];records={}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for r in rows:
   sha,result=c.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s',(r['native']['cacheKey'],)).fetchone();assert sha==r['native']['resultSha'];records[r['uid']]=dict(cacheKey=r['native']['cacheKey'],resultSHA256=sha,terrain=result['terrain'],artifacts=result['artifacts'])
 save(DOC/'source-records.json',records)
 names=subprocess.check_output(['rg','--files','--hidden','--no-ignore','-g','*.gltf','source-scripts/city'],cwd=ROOT,text=True).splitlines();byname={}
 for n in names:byname.setdefault(Path(n).name,[]).append(ROOT/n)
 helper=module('next_ground_decoder',HERE/'xl-second-pass.py');helper.LOCAL=LOCAL;final=module('next_ground_foundation',HERE/'xl-final-script-pass.py');summary=[];refs=[Path(__file__),SRC/'result.json',HERE/'xl-second-pass.py',HERE/'xl-final-script-pass.py']
 for row in rows:
  uid=row['uid'];terrains=records[uid]['terrain'];assert len(terrains)==1;t=terrains[0];candidates=[]
  if t.get('state')=='failed':
   summary.append(dict(uid=uid,state='original-terrain-source-decode-failed',terrainError=t.get('error'),sourceEntry=t.get('sourceEntry'),installationApproved=False));print(summary[-1],flush=True);continue
  for name,sha in t['sourceHashes'].items():
   if name.endswith('.gltf'):candidates.extend((p,sha)for p in byname.get(Path(name).name,[]))
  for f in t['preparedFiles']:
   if f['path'].endswith('.gltf'):candidates.extend((p,f['sha256'])for p in byname.get(Path(f['path']).name,[]))
  verified=[]
  for p,sha in candidates:
   if digest(p.read_bytes())!=sha:continue
   data=read(p);buffers=[p.parent/b['uri']for b in data['buffers']]
   expected={Path(n).name:h for n,h in t['sourceHashes'].items()}
   if all(b.is_file()and digest(b.read_bytes())==expected.get(b.name)for b in buffers):verified.append((p,buffers))
  if not verified:
   summary.append(dict(uid=uid,state='exact-original-terrain-cache-missing',artifact=records[uid]['artifacts'],installationApproved=False));print(summary[-1],flush=True);continue
  p,buffers=verified[0];refs.extend([p,*buffers]);ground=np.asarray(helper.terrain_triangles(p),dtype='<f8');assert len(ground)==t['triangles'];assert np.allclose([ground.min((0,1)),ground.max((0,1))],t['worldBounds'],atol=.002,rtol=0)
  tri=decode_original_world_triangles((ROOT/row['candidate']['path']).read_bytes());assert len(tri)==row['triangles'];b=row['source']['building'];f=final.foundation_context(tri,ground,Polygon(b['rings'][0],b['rings'][1:]));key=uid.split('/')[1]
  save(LOCAL/(key+'-ground.json.gz'),dict(completeOriginalTerrain=ground.tolist(),sourcePath=str(p.relative_to(ROOT))))
  save(DOC/(key+'.json'),dict(uid=uid,sourceSHA256=row['sourceSHA256'],terrainWorldSHA256=digest(ground.tobytes()),foundation=f,originalSheetOnly=True,installationApproved=False))
  item=dict(uid=uid,state='original-ground-measured',**{k:v for k,v in f.items()if k!='components'});summary.append(item);print(item,flush=True)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 refs.extend(ROOT/p for p in pins);refs.extend(p for p in LOCAL.rglob('*')if p.is_file());save(DOC/'summary.json',dict(rows=summary,installationApproved=False))
 module('next_ground_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'twenty-exact-original-sheet-ground-diagnostics',list(dict.fromkeys(refs)),dict(uids=[r['uid']for r in rows],rows=summary,installationApproved=False))
if __name__=='__main__':main()
