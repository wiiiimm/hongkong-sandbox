"""Attribute existing foundation failures to unchanged podium versus terrain."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from china_ferry_current_foundations_v1_20261020 import authenticate,face_diagnostics
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-tko-grandiose-burial-attribution-v1-20261021';DOC=BASE/BATCH
FOUND=BASE/'government-xl-tko-grandiose-joint-foundations-v3-20261021'
RUNTIME=BASE/'government-xl-tko-grandiose-joint-runtime-v2-20261021'
def main():
 assert not DOC.exists()
 refs=[Path(__file__),HERE/'china_ferry_current_foundations_v1_20261020.py',HERE/'xl-final-script-pass.py'];pins={}
 for folder in [FOUND,RUNTIME]:
  receipt,bound=authenticate(folder);refs.append(folder/'result.json')
  for p,h in bound.items():
   assert p not in pins or pins[p]==h
   pins[p]=h
 used={}
 def take(p):
  key=str(p.relative_to(ROOT));assert digest(p.read_bytes())==pins[key]
  used[key]=pins[key];refs.append(p);return read(p)
 runtime={r['uid']:r for r in take(HERE/'local'/RUNTIME.name/'runtime-geometry.json.gz')['rows']}
 final=module('tko_attribution_foundation',HERE/'xl-final-script-pass.py');summary=[]
 for uid in runtime:
  if uid in ['landsd/246824:0','landsd/265489:0']:continue
  for mode in ['original','literal','leftF32','balancedF32']:
   folder=FOUND/mode/uid.split('/')[1];inp=take(folder/'input.json.gz');prior=take(folder/'foundation.json');row=inp['rows'][0]
   if prior['fullyBuriedTriangles']==0:continue
   ground=np.asarray(runtime[uid]['drawnGroundGeometry']).reshape(-1,3,3)
   tri=np.asarray(row['position']).reshape(-1,3)[np.asarray(row['index']).reshape(-1,3)];podium=np.asarray(inp['podium']).reshape(-1,3,3)
   results={name:face_diagnostics(final,tri,surface) for name,surface in [('terrainOnly',ground),('podiumOnly',podium),('combined',np.concatenate([ground,podium]))]}
   assert len(results['combined']['buriedFaces'])==prior['fullyBuriedTriangles']
   assert sum(f['upward'] for f in results['combined']['buriedFaces'])==prior['fullyBuriedUpwardTriangles']
   save(DOC/mode/(uid.split('/')[1]+'.json.gz'),dict(uid=uid,mode=mode,sourceWorldSHA256=digest(tri.tobytes()),podiumWorldSHA256=digest(podium.tobytes()),results=results,installationApproved=False))
   counts={name:dict(buried=len(r['buriedFaces']),upward=sum(f['upward'] for f in r['buriedFaces']),uncovered=len(r['uncoveredFaceIndices'])) for name,r in results.items()}
   summary.append(dict(uid=uid,mode=mode,counts=counts));print(summary[-1],flush=True)
 for p,h in used.items():assert digest((ROOT/p).read_bytes())==h
 result=dict(uids=sorted(runtime),rows=summary,installationApproved=False,sourceGeometryChanges=0,qualification='Attribution only; preserves strict foundation failures and grants no exception.')
 save(DOC/'summary.json',result)
 module('tko_attribution_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-podium-versus-terrain-burial-attribution',list(dict.fromkeys(refs)),result)
if __name__=='__main__':main()
