"""Exact adverse witness for the unchanged 4.1mm named boundary limit.

This disproves the old proposed finite boundary certificate, not source identity
in general or the installability of the unchanged original government model.
"""
from fractions import Fraction as F
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from fung_yip_original_distinct_party_edge_identity_20261010 import UID,FOREIGN,BOUNDARY_GUARDS
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-fung-yip-full-native-domain-exact-boundary-counterexample-v3-20261024'

def squared_distance(point,a,b):
 d=tuple(b[k]-a[k] for k in range(2));den=sum(v*v for v in d);assert den>0
 t=max(F(0),min(F(1),sum((point[k]-a[k])*d[k] for k in range(2))/den))
 return sum((point[k]-a[k]-t*d[k])**2 for k in range(2))

def main():
 out=BASE/BATCH;assert not out.exists();refs=[Path(__file__)];pins={}
 def take(n,f):
  if n not in pins:pins[n]=authenticate(BASE/n)[1];refs.append(BASE/n/'result.json')
  p=BASE/n/f;assert digest(p.read_bytes())==pins[n][str(p.relative_to(ROOT))];refs.append(p);return read(p)
 n='government-xl-after-royal-next-four-with-supports-identity-v1-20261024'
 raw=take(n,'79883:0/identity.json');assert raw['sourceSHA256']=='f6034a6d28e0f7d82bc2094e9817ea253fe700695d3d228825ea794c5375b6d5'
 assert set(raw['reasons'])=={'fresh-current-spatial-bound:sourceExcessCoveredByUnrelatedFormsM2','full-source-unrelated-overlap'}
 sel=take('government-xl-fung-yip-full-native-domain-runtime-v1-20261024','selection.json.gz');source=next(r for r in sel['rows']if r['uid']==UID)
 old=BASE/'government-xl-fung-yip-distinct-original-shared-boundary-diagnostic-v2-20261010'
 diagnostic,_=authenticate(old);refs.append(old/'result.json');forms={f['uid']:f for f in diagnostic['allCurrentForms']}
 assert source['source']['building']==forms[UID]
 from no1_garden_original_overhead_roof_edge_identity_20261010 import polygon
 own=polygon(forms[UID]['rings']);foreign=polygon(forms[FOREIGN[1]]['rings'])
 chain=shapely.line_merge(own.boundary.intersection(foreign.boundary));assert chain.geom_type=='LineString'
 vertices=np.array([[-2381.1865234375,38.2236328125],[-2384.55078125,27.40625],[-2378.966796875,45.3662109375]])
 # These are literal vertices of one exact partition of the authentic source's
 # projected excess. Require the partition to appear in the failed proposal,
 # rather than substituting an arbitrary shape near the shared boundary.
 from test_fung_yip_original_distinct_party_edge_identity_20261010 import fixture
 import fung_yip_original_distinct_party_edge_identity_20261010 as named
 original=named.finite_chain_certificate;seen=[]
 def observe(coords,c,g):
  result=original(coords,c,g)
  if result is None:seen.append((np.array(coords),np.array(c),g))
  return result
 named.finite_chain_certificate=observe
 try:
  try:named.named_proof(*fixture())
  except AssertionError as error:failure=str(error)
  else:raise AssertionError('Historical exact proposal unexpectedly passes')
 finally:named.finite_chain_certificate=original
 assert any(np.array_equal(p,vertices)and np.array_equal(c,np.asarray(chain.coords))and g==.0041 for p,c,g in seen)
 # Choose a witness by a cheap numerical search, then prove every assertion
 # from the exact binary source vertices and rational barycentric weights.
 best=None
 for i in range(401):
  a=i/400;b=(1-a)*np.arange(401)/400
  points=vertices[0]+(vertices[1]-vertices[0])*a+(vertices[2]-vertices[0])*b[:,None]
  distances=shapely.distance(shapely.points(points),chain);j=int(np.argmax(distances));key=float(distances[j])
  if best is None or key>best[0]:best=(key,i,j)
 _,i,j=best;a=F(i,400);b=(1-a)*F(j,400);weights=[1-a-b,a,b];assert min(weights)>=0 and sum(weights)==1
 tri=[[F(float(v))for v in q]for q in vertices]
 point=tuple(sum(weights[k]*tri[k][d]for k in range(3))for d in range(2))
 c=[[F(float(v))for v in q]for q in chain.coords]
 distances=[squared_distance(point,x,y)for x,y in zip(c,c[1:])]
 threshold=F(BOUNDARY_GUARDS[FOREIGN[1]]);assert threshold==F(.0041)
 assert all(d>threshold**2 for d in distances)
 result=dict(uids=[UID],sourceSHA256=raw['sourceSHA256'],currentManifestSHA256=sel['manifestSHA256'],sourceFormSHA256=raw['sourceFormSHA256'],rawIdentityReasonsRetained=raw['reasons'],foreignUid=FOREIGN[1],literalPartitionTriangle=vertices.tolist(),literalSharedChain=list(chain.coords),exactBarycentricWeights=list(map(str,weights)),exactPoint=list(map(str,point)),exactSquaredDistanceToEveryFiniteSegment=list(map(str,distances)),exactThresholdSquared=str(threshold**2),diagnosticDistanceM=float(min(distances))**.5,existingGuardM=float(threshold),allFiniteSegmentsStrictlyOutsideExistingGuard=True,sourceSpecificProposalFailure=failure,sourceGeometryChanges=0,sourcePoseChanges=0,identityAccepted=False,physicalAccepted=False,installationApproved=False,permanentRejection=False,requiredNextAction='Different source-identity evidence or explicitly authorised policy decision; repeating this 4.1mm certificate cannot pass. No source edit, relaxed limit, corruption claim or installation approval.',qualification='Exact interior point is a convex combination of the authentic projected partition triangle. Exact distances to EVERY literal finite shared-boundary segment exceed the unchanged guard. Vertex-only distances were insufficient; this is a real adverse witness, not merely a loose conservative bound.')
 refs.extend(HERE/n for n in ['fung_yip_original_distinct_party_edge_identity_20261010.py','test_fung_yip_original_distinct_party_edge_identity_20261010.py','no1_garden_original_overhead_roof_edge_identity_20261010.py','exact_original_polygon_triangle_partition_20261010.py'])
 # Bind every immutable historical input used by the reproduction.
 for name in ['government-xl-fung-yip-three-podium-primary-relationships-20261010','government-xl-terrain-recovery-fung-yip-original-pair-current-recovery-v2-20261010','government-xl-terrain-recovery-fung-yip-foreign-original-recovery-v1-20261010','xl-terrain-recovery-20261010-fung-yip-current-identity-guard-checkpoint-v1']:
  receipt=BASE/name/'result.json'
  if receipt.exists():authenticate(BASE/name);refs.append(receipt)
  for filename in ['diagnostic.json','diagnostic.json.gz','selection.json.gz']:
   path=BASE/name/filename
   if path.exists():refs.append(path)
 for name in ['government-xl-terrain-recovery-fung-yip-original-pair-current-recovery-v2-20261010','government-xl-terrain-recovery-fung-yip-foreign-original-recovery-v1-20261010']:
  for source in read(BASE/name/'selection.json.gz')['rows']:
   if source['uid'] in {UID,*FOREIGN}:
    asset=ROOT/source['candidate']['path'];assert digest(asset.read_bytes())==source['sourceSHA256'];refs.append(asset)
 save(out/'summary.json',result)
 module('fung_exact_adverse_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-unchanged-source-boundary-guard-counterexample',refs,result)
 print(dict(distance=result['diagnosticDistanceM'],guard=float(threshold),installationApproved=False),flush=True)
if __name__=='__main__':main()
