"""Full unchanged source assembly diagnostic, preserving the runtime-fit hold."""
from pathlib import Path
import subprocess
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest
from primrose_compound_foundation_v2_20261015 import module
from china_ferry_current_foundations_v1_20261020 import authenticate
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-siu-hong-original-assembly-v1-20261021';DOC=BASE/BATCH
SRC=BASE/'government-xl-siu-hong-companion-sources-v1-20261021';GROUND=BASE/'government-xl-siu-hong-original-ground-v1-20261021'
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={};used={}
 for folder in [SRC,GROUND]:
  _,bound=authenticate(folder);refs.append(folder/'result.json')
  for p,h in bound.items():
   assert p not in pins or pins[p]==h
   pins[p]=h
 def take(p):
  k=str(p.relative_to(ROOT));assert digest(p.read_bytes())==pins[k];used[k]=pins[k];refs.append(p);return read(p)
 nominees=take(SRC/'nominations.json')['rows'];assert {r['uid']for r in nominees}=={'landsd/190963:0','landsd/233417:0'}
 paths={'landsd/190963:0':HERE/'local/government-xl-next-twenty-current-terrain-v6-20261021/assets/e4220c79428d6234672c3d40f49660dad2b7ab877884fff2c9b3f1acc2dc96ed.glb.gz','landsd/233417:0':HERE/'local/government-xl-eight-further-original-closures-20261008/assets/60d6ebb76a84c0f82fc4faa378e8d57309beec7097b685d828e3c5e51b308d59.glb.gz'}
 worlds={};rows=[]
 for n in nominees:
  p=paths[n['uid']];assert digest(p.read_bytes())==n['model']['asset']['sha256'];refs.append(p);used[str(p.relative_to(ROOT))]=digest(p.read_bytes())
  tile=ROOT/'3d-viewer'/n['source']['tile'];assert next(b for b in read(tile)['buildings']if b['uid']==n['uid'])==n['source']['building'];refs.append(tile);used[str(tile.relative_to(ROOT))]=digest(tile.read_bytes())
  worlds[n['uid']]=decode_original_world_triangles(p.read_bytes());assert len(worlds[n['uid']])==n['model']['triangles']
 ground=np.asarray(take(HERE/'local'/GROUND.name/'190963:0-ground.json.gz')['completeOriginalTerrain']).reshape(-1,3,3)
 final=module('siu_hong_original_foundation',HERE/'xl-final-script-pass.py');tool=HERE/'wave_retained_basic_support_v1_20261017.mjs'
 for n in nominees:
  uid=n['uid'];b=n['source']['building'];tri=worlds[uid];support=ground if uid=='landsd/233417:0' else worlds['landsd/233417:0'];foundation=final.foundation_context(tri,ground if uid=='landsd/233417:0' else np.concatenate([ground,support]),Polygon(b['rings'][0],b['rings'][1:]));folder=DOC/uid.split('/')[1]
  save(folder/'foundation.json',foundation);save(folder/'input.json.gz',dict(podium=support.tolist(),rows=[dict(uid=uid,position=tri.reshape(-1).tolist(),index=list(range(len(tri)*3)))]))
  subprocess.run(['/home/williamli/.nvm/versions/node/v24.18.0/bin/node',str(tool),str(folder.relative_to(ROOT))],cwd=ROOT,check=True)
  report=read(folder/'support.json.gz');proof=report['rows'][0]['proof']
  for p,h in report['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p);used[p]=h
  item=dict(uid=uid,foundation={k:v for k,v in foundation.items()if k!='components'},strictContacts=proof['strictContacts'],samples=proof['samples'],unresolved=len(proof['unresolved']),strictSupportPassed=proof['passed']);rows.append(item);print(item,flush=True)
 for p,h in used.items():assert digest((ROOT/p).read_bytes())==h
 refs.extend([tool,HERE/'xl-final-script-pass.py',HERE/'exact_packed_world_geometry_20261009.py',HERE/'china_ferry_current_foundations_v1_20261020.py'])
 result=dict(uids=sorted(worlds),rows=rows,installationApproved=False,sourceGeometryChanges=0,qualification='Complete original-coordinate numerical diagnostic only. Historical podium runtime footprint-fit rejection remains unresolved; no renderer or identity waiver.')
 save(DOC/'summary.json',result);module('siu_assembly_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'siu-hong-full-original-assembly-support-foundation',list(dict.fromkeys(refs)),result)
if __name__=='__main__':main()
