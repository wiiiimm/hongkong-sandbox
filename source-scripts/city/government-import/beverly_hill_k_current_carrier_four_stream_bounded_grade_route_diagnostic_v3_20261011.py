"""Diagnostic only: original carrier finite-face/whole-edge route in exact frozen current drawn ground.
Existing reviewed kernels. No native reapproval or acceptance policy. Route is source-only diagnostic, not publication.
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
B=ROOT/'docs/astra-city/government-import';BATCH='government-xl-beverly-hill-k-current-carrier-four-stream-bounded-grade-route-diagnostic-v3-20261011';DOC=B/BATCH
RANK=B/'xl-terrain-recovery-20261010-next-current-native-cap-source-only-ranking-v1/diagnostic.json.gz'
CAPTURE=B/'government-xl-beverly-elm-complete-current-support-ground-capture-v2-20261011'
RUNTIME=HERE/'local'/CAPTURE.name/'runtime-geometry.json.gz'
LIMIT=128

def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def diagnose(n,g):
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
  r=dict(face=i,strictClear=bool(clear),genuineGradeInCapturedCurrentGround=bool(grade),eligibleForDiagnosticRoute=bool(clear or grade),wholeFiniteProof=prior,refinedFiniteColumnPieces=pieces,exactLowerM=str(lower),exactUpperGroundInterfaces=interfaces,vertexExposure=exposure);nodes[i]=r;return r
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
    if proof['genuineGradeInCapturedCurrentGround']:root=b;break
   if root is not None:break
 path=[]
 if root is not None:
  path=[root]
  while parents[path[-1]]is not None:path.append(parents[path[-1]])
 return dict(completeCarrierBodyCensus=whole,cap2122BodyFaces=capbody,allExaminedFaceProofs=list(nodes.values()),allExaminedWholeSharedEdgeProofs=list(edges.values()),boundedParents=parents,explicitFaceBudget=LIMIT,budgetReached=budget,diagnosticGradeFace=root,diagnosticPath=path,diagnosticPathFound=bool(path))
def main():
 assert not DOC.exists();rank=next(r for r in read(RANK)['rows']if r['uid']=='landsd/255543:0');native=rank['completeCandidateNativeInventory'][0];p=ROOT/native['asset']['path'];assert ref(p)==native['asset'];n=decode_original_world_triangles(p.read_bytes());assert len(n)==12640
 rt=next(r for r in read(RUNTIME)['rows']if r['uid']=='landsd/255939:0');g=np.asarray(rt['drawnGroundGeometry'],float).reshape(-1,3,3);captured=next(r for r in read(CAPTURE/'review.json')['actors']if r['uid']=='landsd/255939:0');assert len(g)==captured['completeActualRelevantGroundFaces']and digest(g.tobytes())==captured['completeActualRelevantGroundSHA256'];assert digest(n.tobytes())==captured['completeOriginalWorldSHA256'];assert read(CAPTURE/'result.json')['sourceOnly']
 attrs=read(CAPTURE/'actual-render-geometry.json.gz');a=next(r for r in attrs['rows']if r['uid']=='landsd/255939:0');index=np.asarray(a['completeOriginalIndex']).reshape(-1,3);streams={'original':n}
 for name,key in [('literal','completeLiteralWorldPosition'),('explicitLeftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('explicitBalancedF32','completeExplicitBalancedFloat32WorldPosition')]:streams[name]=np.asarray(a[key],float).reshape(-1,3)[index]
 proofs={};bindings={}
 for name,source in streams.items():
  h=digest(source.tobytes());bindings[name]=dict(completeWorldSHA256=h,completeFaces=len(source),proofTupleSHA256=h);assert source.shape==(12640,3,3)
  if h not in proofs:proofs[h]=diagnose(source,g)
 files=[Path(__file__),RANK,RUNTIME,p,CAPTURE/'result.json',CAPTURE/'review.json',CAPTURE/'capture-scope.json',CAPTURE/'actual-render-geometry.json.gz',B/'government-xl-beverly-hill-k-original-carrier-bounded-grade-route-diagnostic-v1-20261011/result.json',B/'government-xl-terrain-recovery-255543-original-physical-v1-20261009/native-neighbour-checks.json']+[HERE/(s+'.py')for s in ['exact_packed_world_geometry_20261009','exact_original_shared_edge_component_census_v2_20261011','test_exact_original_shared_edge_component_census_v2_20261011','exact_original_face_conservative_clearance_v5_20261010','exact_original_triangle_pair_column_gap_20261010','exact_original_rational_interface_segment_clearance_20261011','exact_original_upper_ground_interfaces_20261009','original_bound_facet_wall_context_v3_20261010']]
 refs=[ref(x)for x in files]
 result=dict(uids=['landsd/255543:0','landsd/255939:0'],sourceOnly=True,currentAcceptance=False,installationApproved=False,wholeNativeReapproval=False,sourceGeometryChanges=0,terrainGeometryChanges=0,freshMutableCapture=False,completeOriginalCarrierFaces=12640,completeOriginalCarrierWorldSHA256=digest(n.tobytes()),completeFrozenCurrentGroundFacets=len(g),completeFrozenCurrentGroundSHA256=digest(g.tobytes()),allFourStreamBindings=bindings,allDistinctWholeSourceTupleRouteDiagnostics=proofs,exactByteIdenticalFullWorldReuseOnly=True,currentQualifiedAcceptancePathProved=False,historical16DetailObligationsUnchanged=True,qualification='Four complete source representations against complete actual current carrier ground. Original grade/strict cap/whole-edge kernel logic applies to each distinct full world; only byte-identical entire tuples reuse proof. This is bounded128face source-only route nomination, not full12640 source clearance/native reapproval/foreign regression/current acceptance. Historical owned350cap gap and0/155 native lowrim support failures remain unchanged.',evidenceRefs=refs)
 for r in refs:assert ref(ROOT/r['path'])==r
 save(DOC/'diagnostic.json.gz',result);print(json.dumps(dict(bindings=bindings,routeSummaries={h:dict(capStrict=x['allExaminedFaceProofs'][0]['strictClear'],nodes=len(x['allExaminedFaceProofs']),edges=len(x['allExaminedWholeSharedEdgeProofs']),path=x['diagnosticPath'],budgetReached=x['budgetReached'])for h,x in proofs.items()},currentAcceptance=False)),flush=True)
if __name__=='__main__':main()
