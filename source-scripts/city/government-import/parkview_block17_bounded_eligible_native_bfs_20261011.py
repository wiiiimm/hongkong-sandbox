"""Block17 bounded unchanged native eligible-face / whole exposed-edge BFS.
Frozen ground context, no new renderer/current acceptance or whole-native credit.
"""
from collections import defaultdict,deque
from pathlib import Path
from fractions import Fraction as F
import numpy as np,json
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_face_conservative_clearance_v5_20261010 import verify as finite
from exact_original_triangle_pair_column_gap_20261010 import verify as column
from exact_original_rational_interface_segment_clearance_20261011 import verify as segment
from exact_original_upper_ground_interfaces_20261009 import exact_upper_ground_interfaces
from original_bound_facet_wall_context_v3_20261010 import best_original_vertex_exposure
B=ROOT/'docs/astra-city/government-import';OLD=B/'government-xl-parkview-next-three-original-cap-contacts-v1-20261011';CAP=B/'government-xl-parkview-next-three-exact-cap-refinement-v1-20261011';CARRIER=B/'government-xl-parkview-block6-fresh-current-carrier-capture-v1-20261011';BATCH='government-xl-parkview-block17-bounded-eligible-native-route-v1-20261011';DOC=B/BATCH;UID='landsd/256116:0'
LIMIT=192

def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();r=read(OLD/'diagnostic.json.gz');owned=next(x for x in r['rows']if x['uid']==UID);selection=read(CARRIER/'selection.json.gz');assert selection['manifestSHA256']=='cb79525c2c95d96eb0c9868158bfe04c21a60135ec5a8e755ccea106c972b402';nr=selection['rows'][0];npth=ROOT/nr['candidate']['path'];assert digest(npth.read_bytes())==nr['sourceSHA256'];n=decode_original_world_triangles(npth.read_bytes());rp=HERE/'local'/CARRIER.name/'runtime-geometry.json.gz';rt=next(x for x in read(rp)['rows']if x['uid']=='landsd/254491:0');g=np.asarray(rt['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3);assert digest(n.tobytes())==r['completeOriginalNativeWorldSHA256']and digest(g.tobytes())==r['completeFrozenGroundSHA256'];lo=g[:,:,[0,2]].min(1);hi=g[:,:,[0,2]].max(1)
 caprow=next(x for x in read(CAP/'diagnostic.json.gz')['rows']if x['uid']==UID);assert caprow['cap']==54418 and caprow['wholeFiniteCapStrictClear']and caprow['existingStrictCapProofReused'];capprior=caprow['priorProof'];assert capprior['groundProjectionCovered']and F(capprior['exactCertifiedLowerClearanceM'])>0
 incidence=defaultdict(set)
 for i,t in enumerate(n):
  if not np.any(np.cross(t[1]-t[0],t[2]-t[0])):continue
  for j in range(3):incidence[tuple(sorted((tuple(t[j]),tuple(t[(j+1)%3]))))].add(i)
 checkpointPath=B/'government-xl-parkview-block6-bounded-eligible-native-route-v2-20261011/diagnostic.json.gz';checkpoint=read(checkpointPath);assert checkpoint['completeOriginalNativeWorldSHA256']==digest(n.tobytes()) and checkpoint['completePinnedGroundSHA256']==digest(g.tobytes())
 reusednodes={p['face']:p for p in checkpoint['allExaminedFaceProofs']};reusededges={tuple(p['faces']):p for p in checkpoint['allExaminedWholeSharedEdgeProofs']}
 nodes={54418:dict(face=54418,eligible=True,strictClear=True,genuineGrade=False,priorWholeFiniteProof=capprior,refinedFiniteColumnPieces=[],exactLowerM=capprior['exactCertifiedLowerClearanceM'],exactPositiveUpperGroundInterfaces=[],completeGradeVertexExposure=None)};edgeproofs={};parent={54418:None};queue=deque([54418]);root=None;bounded=False;reusedfaces=[];reusededgekeys=[]
 def qualify(i):
  if i in nodes:return nodes[i]
  if i in reusednodes:nodes[i]=reusednodes[i];reusedfaces.append(i);return nodes[i]
  f=n[i];normal=np.cross(f[1]-f[0],f[2]-f[0]);prior=finite(f,g);lower=F(prior['exactCertifiedLowerClearanceM']);pieces=[];iswall=normal[1]==0 and np.any(normal);interfaces=[];exposure=None
  if iswall:
   interfaces=exact_upper_ground_interfaces(n,[i],g)
   if interfaces:exposure=best_original_vertex_exposure(f,g)
  genuine=bool(interfaces)and exposure is not None and F(exposure['exactExposureLowerBoundM'])>0
  if prior['groundProjectionCovered']and lower<=0 and not genuine:
   ids=prior['allProjectedBoundingCandidateOriginalGroundFacets']
   pieces=[dict(originalGroundFace=j,proof=column(f,g[j]))for j in ids];gaps=[F(p['proof']['exactMinimumFiniteColumnGapM'])for p in pieces if p['proof']['exactClosedHorizontalProjectionsMeet']];assert gaps;lower=min(gaps)
  clear=prior['groundProjectionCovered']and lower>0
  p=dict(face=i,eligible=bool(clear or genuine),strictClear=bool(clear),genuineGrade=bool(genuine),priorWholeFiniteProof=prior,refinedFiniteColumnPieces=pieces,exactLowerM=str(lower),exactPositiveUpperGroundInterfaces=interfaces,completeGradeVertexExposure=exposure)
  nodes[i]=p;print(json.dumps(dict(face=i,eligible=p['eligible'],grade=genuine,covered=prior['groundProjectionCovered'],lower=str(lower))),flush=True);return p
 def edge(a,b,shared):
  key=tuple(sorted((a,b)))
  if key in edgeproofs:return edgeproofs[key]
  if key in reusededges:edgeproofs[key]=reusededges[key];reusededgekeys.append(list(key));return edgeproofs[key]
  endpoints=np.asarray(shared,float);ids=np.flatnonzero(np.all(hi>=endpoints[:,[0,2]].min(0),axis=1)&np.all(lo<=endpoints[:,[0,2]].max(0),axis=1));assert len(ids)
  proof=segment([[str(F(float(v)))for v in p]for p in shared],g[ids]);p=dict(faces=list(key),exactAABBCandidateGroundFaces=list(map(int,ids)),completeGroundFaces=len(g),completeGroundSHA256=digest(g.tobytes()),strictDisjointClosedAABBPruning=True,originalSubsetProof=proof,eligible=proof['strictlyExposedWholePositiveInterface']);edgeproofs[key]=p;return p
 while queue and root is None:
  a=queue.popleft()
  for j in range(3):
   shared=tuple(sorted((tuple(n[a,j]),tuple(n[a,(j+1)%3]))))
   for b in sorted(incidence[shared]-{a}):
    if b==54320 or tuple(sorted((a,b)))==(52248,52249):continue
    if b in parent:continue
    if len(nodes)>=LIMIT and b not in nodes:bounded=True;continue
    # Edge exposure is independent; a buried edge cannot authorize a child.
    ep=edge(a,b,shared)
    if not ep['eligible']:continue
    p=qualify(b)
    if not p['eligible']:continue
    parent[b]=a;queue.append(b)
    if p['genuineGrade']:root=b;break
   if root is not None:break
 path=[]
 if root is not None:
  path=[root]
  while parent[path[-1]]is not None:path.append(parent[path[-1]])
 refs=[ref(p)for p in [checkpointPath,Path(__file__),npth,rp,CARRIER/'selection.json.gz',CARRIER/'capture-scope.json',CARRIER/'result.json',OLD/'result.json',OLD/'diagnostic.json.gz',CAP/'result.json',CAP/'diagnostic.json.gz',HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_face_conservative_clearance_v5_20261010.py',HERE/'exact_original_triangle_pair_column_gap_20261010.py',HERE/'exact_original_rational_interface_segment_clearance_20261011.py',HERE/'exact_original_upper_ground_interfaces_20261009.py',HERE/'original_bound_facet_wall_context_v3_20261010.py',HERE/'original_bound_facet_wall_context_v2_20261010.py',HERE/'exact_original_projection_coverage_v2_20261010.py']]
 for x in refs:assert ref(ROOT/x['path'])==x
 result=dict(uids=[UID],nativeOriginalCapFace=54418,recordedFrozenBaselineManifestSHA256=selection['manifestSHA256'],historicalReasonsUnchanged=owned['historicalReasonsUnchanged'],inheritedExactIdenticalFaceProofs=reusedfaces,inheritedExactIdenticalEdgeProofs=reusededgekeys,terrainChanges=0,completeOriginalNativeFaces=len(n),completeOriginalNativeWorldSHA256=digest(n.tobytes()),completePinnedGroundSHA256=digest(g.tobytes()),completePinnedGroundFaces=len(g),explicitQualificationFaceBudget=LIMIT,qualificationBudgetReached=bounded,allExaminedFaceProofs=list(nodes.values()),allExaminedWholeSharedEdgeProofs=list(edgeproofs.values()),completeBoundedEligibleParents=parent,qualifiedGenuineGradeFace=root,qualifiedOriginalPathToStrictCap=path,boundedOriginalPathProved=root is not None,explicitExcludedCoverageGapFace=54320,explicitExcludedPartlyBuriedEdge=[52248,52249],wholeNativeReaccepted=False,sourceOnly=True,notFreshCurrentCapture=True,currentAcceptance=False,installationApproved=False,newlyInstalled=0,evidenceRefs=refs)
 save(DOC/'diagnostic.json.gz',result);print(json.dumps(dict(root=root,path=path,nodes=len(nodes),edges=len(edgeproofs),budgetReached=bounded)),flush=True)
if __name__=='__main__':main()
