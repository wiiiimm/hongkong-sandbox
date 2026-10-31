"""Bind reused two-source clearance certificates to the current five-source capture."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';P='government-xl-royal-green8-'
BATCH=P+'two-to-five-equivalence-v1-20261024'
def main():
 out=BASE/BATCH;assert not out.exists();refs=[Path(__file__)];cache={}
 def take(n,p):
  if n not in cache:cache[n]=authenticate(BASE/n)[1];refs.append(BASE/n/'result.json')
  assert digest(p.read_bytes())==cache[n][str(p.relative_to(ROOT))];refs.append(p);return read(p)
 old=P+'two-current-runtime-v2-20261024';new=P+'five-current-runtime-v1-20261024';runtime={}
 for n in [old,new]:runtime[n]=take(n,HERE/'local'/n/'runtime-geometry.json.gz');take(n,BASE/n/'selection.json.gz')
 olds=P+'two-current-attributes-v2-20261024';news=P+'five-current-attributes-v1-20261024';attrs={n:take(n,BASE/n/'attributes.json.gz')for n in [olds,news]};rows=[]
 for u in ['landsd/235598:0','landsd/233190:0']:
  a,b=[next(r for r in runtime[n]['rows']if r['uid']==u)for n in [old,new]];assert a['sourceSHA256']==b['sourceSHA256']
  for k in ['position','index','drawnGroundGeometry']:assert np.array_equal(np.asarray(a[k]),np.asarray(b[k])),(u,k)
  x,y=[next(r for r in attrs[n]['rows']if r['uid']==u)for n in [olds,news]]
  for k in ['completeOriginalIndex','completeLiteralWorldPosition','completeExplicitLeftAssociatedFloat32WorldPosition','completeExplicitBalancedFloat32WorldPosition']:assert np.array_equal(np.asarray(x[k]),np.asarray(y[k])),(u,k)
  rows.append(dict(uid=u,sourceSHA256=a['sourceSHA256'],allSourceCoordinateStreamsIdentical=True,completeDrawnGroundIdentical=True,indicesIdentical=True))
 manifest=ROOT/'3d-viewer/city/data/manifest.json';refs.append(manifest)
 result=dict(uids=[r['uid']for r in rows],rows=rows,currentManifestSHA256=digest(manifest.read_bytes()),passed=True,sourceGeometryChanges=0,installationApproved=False,qualification='Exact input-array equality only. Older complete source/ground clearance proofs retain their full obligations and can be reused for these same two sources in the current five-source capture; no diagnostic is promoted to approval.')
 save(out/'summary.json',result);module('runtime_equivalence_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'current-four-world-source-and-complete-drawn-ground-input-equivalence',refs,result)
if __name__=='__main__':main()
