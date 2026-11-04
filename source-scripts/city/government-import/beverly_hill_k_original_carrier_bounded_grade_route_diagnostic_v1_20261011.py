"""Diagnostic only: original carrier finite-face/whole-edge route in exact frozen historical drawn ground.
Existing reviewed kernels. No fresh current qualification, native reapproval or acceptance policy.
"""
from collections import defaultdict,deque
from pathlib import Path
from fractions import Fraction as F
import numpy as np,json
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shared_edge_component_census_v2_20261011 import census
from exact_original_face_conservative_clearance_v5_20261010 import verify as finite
from exact_original_triangle_pair_column_gap_20261010 import verify as column
from exact_original_rational_interface_segment_clearance_20261011 import verify as segment
from exact_original_upper_ground_interfaces_20261009 import exact_upper_ground_interfaces
from original_bound_facet_wall_context_v3_20261010 import best_original_vertex_exposure
B=ROOT/'docs/astra-city/government-import';BATCH='government-xl-beverly-hill-k-original-carrier-bounded-grade-route-diagnostic-v1-20261011';DOC=B/BATCH
RANK=B/'xl-terrain-recovery-20261010-next-current-native-cap-source-only-ranking-v1/diagnostic.json.gz'
RUNTIME=HERE/'local/government-xl-terrain-recovery-255543-original-physical-v1-20261009/runtime-geometry.json.gz'
LIMIT=128

def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();rank=next(r for r in read(RANK)['rows']if r['uid']=='landsd/255543:0');native=rank['completeCandidateNativeInventory'][0];p=ROOT/native['asset']['path'];assert ref(p)==native['asset'];n=decode_original_world_triangles(p.read_bytes());assert len(n)==12640
 rt=next(r for r in read(RUNTIME)['rows']if r['uid']=='landsd/255543:0');g=np.asarray(rt['drawnGroundGeometry'],float).reshape(-1,3,3);assert len(g)==350
 whole=census(n,list(range(len(n))));capbody=next(c for c in whole['sharedEdgeConnectedComponents']if 2122 in c);incidence=defaultdict(set)
 for i,t in enumerate(n):
  if not np.any(np.cross(t[1]-t[0],t[2]-t[0])):continue
  for j in range(3):incidence[tuple(sorted((tuple(t[j]),tuple(t[(j+1)%3]))))].add(i)
 lo=g[:,:,[0,2]].min(1);hi=g[:,:,[0,2]].max(1);nodes={};edges={}
 def qualify(i):
  if i in nodes:return nodes[i]
  f=n[i];normal=np.cross(f[1]-f[0],f[2]-f[0]);prior=finite(f,g);lower=F(prior['exactCertifiedLowerClearanceM']);pieces=[];wall=normal[1]==0 and np.any(normal);interfaces=[];exposure=None
  if wall:
   interfaces=exact_upper_ground_interfaces(n,[i],g)
   if interfaces:exposure=best_original_vertex_exposure(f,g)
  grade=bool(interfaces)and exposure is not None and F(exposure['exactExposureLowerBoundM'])>0
  if prior['groundProjectionCovered']and lower<=0 and not grade:
   pieces=[dict(originalGroundFace=j,proof=column(f,g[j]))for j in prior['allProjectedBoundingCandidateOriginalGroundFacets']];gaps=[F(x['proof']['exactMinimumFiniteColumnGapM'])for x in pieces if x['proof']['exactClosedHorizontalProjectionsMeet']];assert gaps;lower=min(gaps)
  clear=prior['groundProjectionCovered']and lower>0
  r=dict(face=i,strictClear=bool(clear),genuineGradeInFrozenHistoricalGround=bool(grade),eligibleForDiagnosticRoute=bool(clear or grade),wholeFiniteProof=prior,refinedFiniteColumnPieces=pieces,exactLowerM=str(lower),exactUpperGroundInterfaces=interfaces,vertexExposure=exposure);nodes[i]=r;return r
 def edge(a,b,shared):
  key=tuple(sorted((a,b)))
  if key in edges:return edges[key]
  ends=np.asarray(shared,float);ids=np.flatnonzero(np.all(hi>=ends[:,[0,2]].min(0),axis=1)&np.all(lo<=ends[:,[0,2]].max(0),axis=1))
  proof=segment([[str(F(float(v)))for v in point]for point in shared],g[ids])if len(ids)else None
  r=dict(faces=list(key),completeGroundSHA256=digest(g.tobytes()),allClosedAABBCandidateGroundFaces=list(map(int,ids)),proof=proof,eligible=bool(proof and proof['strictlyExposedWholePositiveInterface']));edges[key]=r;return r
 cap=qualify(2122);parents={2122:None}if cap['strictClear']else {};q=deque(parents);root=None;budget=False
 while q and root is None:
  a=q.popleft()
  for j in range(3):
   shared=tuple(sorted((tuple(n[a,j]),tuple(n[a,(j+1)%3]))))
   for b in sorted(incidence[shared]-{a}):
    if b in parents:continue
    if len(nodes)>=LIMIT and b not in nodes:budget=True;continue
    if not edge(a,b,shared)['eligible']:continue
    proof=qualify(b)
    if not proof['eligibleForDiagnosticRoute']:continue
    parents[b]=a;q.append(b)
    if proof['genuineGradeInFrozenHistoricalGround']:root=b;break
   if root is not None:break
 path=[]
 if root is not None:
  path=[root]
  while parents[path[-1]]is not None:path.append(parents[path[-1]])
 files=[Path(__file__),RANK,RUNTIME,p,B/'government-xl-terrain-recovery-255543-original-physical-v1-20261009/native-neighbour-checks.json']+[HERE/(s+'.py')for s in ['exact_packed_world_geometry_20261009','exact_original_shared_edge_component_census_v2_20261011','test_exact_original_shared_edge_component_census_v2_20261011','exact_original_face_conservative_clearance_v5_20261010','exact_original_triangle_pair_column_gap_20261010','exact_original_rational_interface_segment_clearance_20261011','exact_original_upper_ground_interfaces_20261009','original_bound_facet_wall_context_v3_20261010']]
 refs=[ref(x)for x in files]
 result=dict(uids=['landsd/255543:0','landsd/255939:0'],sourceOnly=True,currentAcceptance=False,installationApproved=False,wholeNativeReapproval=False,sourceGeometryChanges=0,terrainGeometryChanges=0,freshMutableCapture=False,completeOriginalCarrierFaces=len(n),completeOriginalCarrierWorldSHA256=digest(n.tobytes()),completeOriginalCarrierBodyCensus=whole,originalCap2122GenuineBodyFaces=capbody,completeFrozenHistoricalGroundFacets=len(g),completeFrozenHistoricalGroundSHA256=digest(g.tobytes()),frozenGroundScope='Exact actual drawn ground around owned255543 in original physical20261009 proposed terrain capture; not full carrier ground/current installation surface. Coverage failures retained. Any positive path needs independent actual complete current rebind, no grade/root credit here.',allExaminedFaceProofs=list(nodes.values()),allExaminedWholeSharedEdgeProofs=list(edges.values()),boundedDiagnosticParents=parents,explicitFaceBudget=LIMIT,budgetReached=budget,qualifiedHistoricalGradeFace=root,historicalDiagnosticPath=path,historicalDiagnosticPathFound=bool(path),currentQualifiedPathProved=False,historical16DetailObligationsUnchanged=True,evidenceRefs=refs)
 for r in refs:assert ref(ROOT/r['path'])==r
 save(DOC/'diagnostic.json.gz',result);print(json.dumps(dict(carrierBodies=len(whole['sharedEdgeConnectedComponents']),capBodyFaces=len(capbody),capStrict=cap['strictClear'],nodes=len(nodes),edges=len(edges),budgetReached=budget,path=path,currentQualified=False)),flush=True)
if __name__=='__main__':main()
