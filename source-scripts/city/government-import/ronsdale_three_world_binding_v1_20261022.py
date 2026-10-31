"""Bind complete original and renderer arrays; identical inputs permit exact proof reuse."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-ronsdale-three-world-binding-v1-20261022';DOC=BASE/BATCH
UIDS={'landsd/256898:0','landsd/256702:0','landsd/233771:0'}
def main():
 assert not DOC.exists();refs=[Path(__file__)];cache={}
 def take(n,p):
  if n not in cache:cache[n]=authenticate(BASE/n)[1];refs.append(BASE/n/'result.json')
  assert digest(p.read_bytes())==cache[n][str(p.relative_to(ROOT))];refs.append(p);return read(p)
 n='government-xl-ronsdale-three-source-runtime-v1-20261022';selection=take(n,BASE/n/'selection.json.gz');runtime=take(n,HERE/'local'/n/'runtime-geometry.json.gz');n='government-xl-ronsdale-three-render-attributes-v1-20261022';attr=take(n,BASE/n/'attributes.json.gz');assert attr['startEndAllInputsVerified'];assert {r['uid']for r in runtime['rows']}=={r['uid']for r in attr['rows']}==UIDS
 rows=[]
 for r in selection['rows']:
  uid=r['uid'];asset=ROOT/r['candidate']['path'];assert digest(asset.read_bytes())==r['sourceSHA256'];refs.append(asset);a=next(x for x in attr['rows']if x['uid']==uid);g=next(x for x in runtime['rows']if x['uid']==uid);assert a['sourceSHA256']==g['sourceSHA256']==r['sourceSHA256'];indices=np.asarray(a['completeOriginalIndex']).reshape(-1,3)
  worlds={'original':decode_original_world_triangles(asset.read_bytes())}
  for mode,field in [('literal','completeLiteralWorldPosition'),('explicitLeftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('explicitBalancedF32','completeExplicitBalancedFloat32WorldPosition')]:worlds[mode]=np.asarray(a[field],dtype='<f8').reshape(-1,3)[indices]
  captured=np.asarray(g['position'],dtype='<f8').reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];assert np.array_equal(captured,worlds['literal'])
  hashes={mode:digest(t.astype('<f8').tobytes())for mode,t in worlds.items()};row=dict(uid=uid,sourceSHA256=r['sourceSHA256'],triangles=r['triangles'],worldSHA256ByMode=hashes,allFourArraysIdentical=len(set(hashes.values()))==1);rows.append(row);print(row,flush=True)
 result=dict(uids=sorted(UIDS),rows=rows,allFourArraysIdentical=all(r['allFourArraysIdentical']for r in rows),installationApproved=False,sourceGeometryChanges=0,qualification='Complete ordered drawn triangle arrays, not counts or bounds. Numerical proofs can be reused only where exact source/support/ground and actual witness bindings are also verified. No performance/GPU guarantee or publication approval.')
 save(DOC/'binding.json',result);refs.append(HERE/'exact_packed_world_geometry_20261009.py');module('ronsdale_world_binding_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-original-four-world-array-binding',refs,result)
if __name__=='__main__':main()
