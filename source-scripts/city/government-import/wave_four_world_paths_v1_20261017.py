"""Recompute canonical failures and bounded original connection witnesses in four worlds."""
from pathlib import Path
import subprocess
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from wave_local_coplanar_paths_v3_20261017 import witness
BASE=ROOT/'docs/astra-city/government-import';ATTR=BASE/'government-xl-wave-actual-render-attributes-v1-20261017';PRIOR=BASE/'government-xl-wave-local-coplanar-paths-v3-20261017';SOURCE=BASE/'government-xl-wave-all-original-support-distance-v1-20261017';BATCH='government-xl-wave-four-world-paths-v1-20261017';DOC=BASE/BATCH

def main():
 assert not DOC.exists();refs=[Path(__file__)]+[HERE/n for n in ['wave_local_coplanar_paths_v3_20261017.py','wave_incident_side_intersections_v1_20261017.py','pool_incident_wall_contacts_v1_20261017.py','exact_packed_world_geometry_20261009.py']];pins={}
 for d in [ATTR,PRIOR]:
  r=read(d/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  refs.append(d/'result.json')
  for e in r['evidenceRefs']:
   assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 sources=read(SOURCE/'support-inputs.json')['sources'];worlds={'original':{r['uid']:decode_original_world_triangles((ROOT/r['candidate']['path']).read_bytes())for r in sources}};attrs=read(ATTR/'attributes.json.gz')['rows']
 for mode,key in [('literal','completeLiteralWorldPosition'),('left','completeExplicitLeftAssociatedFloat32WorldPosition'),('balanced','completeExplicitBalancedFloat32WorldPosition')]:worlds[mode]={r['uid']:np.array(r[key]).reshape(-1,3)[np.array(r['completeOriginalIndex']).reshape(-1,3)]for r in attrs}
 save(DOC/'worlds.json.gz',{m:{u:t.tolist()for u,t in world.items()}for m,world in worlds.items()});tool=HERE/'wave_four_world_interfaces_v1_20261017.mjs';subprocess.run(['node',str(tool),str((DOC/'worlds.json.gz').relative_to(ROOT)),str((DOC/'strict.json').relative_to(ROOT))],cwd=ROOT,check=True);strict=read(DOC/'strict.json');summary=[];details=[]
 for row in strict['rows']:
  mode=row['mode'];uid=row['uid'];world=worlds[mode];paths=[witness(world[uid],world['landsd/301560:0'],f,False)for f in row['unresolved']];result=dict(mode=mode,uid=uid,samples=row['proof']['samples'],strictContacts=row['proof']['strictContacts'],unresolved=len(paths),localSurfaceWitnesses=sum(p['witness']is not None for p in paths));summary.append(result);details.append(dict(**result,paths=paths));print(result,flush=True)
 save(DOC/'summary.json',dict(rows=summary,fullAcceptance=False));save(DOC/'paths.json.gz',dict(rows=details,fullAcceptance=False,qualification='All-surface context includes floors; not strict wall support approval. Every actual mode has freshly sampled canonical failures and independently recomputed exact local paths.'))
 for p,h in strict['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 out=module('wave_four_paths_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'four-world-original-assembly-canonical-and-local-surface-contacts-v1',list(set(refs)),dict(uids=[r['uid']for r in sources],summary=summary,fullAcceptance=False,newlyInstalled=0));print(out['jobId'],flush=True)
if __name__=='__main__':main()
