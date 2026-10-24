"""DRAFT complete original Museum cross-body graph, bounded68-face historical grade/cap routes.
Geometric only: no whole Museum/recovered actor/native/current/role/root approval.
"""
from pathlib import Path
from collections import defaultdict,deque
from fractions import Fraction as F
import json,numpy as np
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shell_intersections_20261009 import rational_face,intersection_points,cross,sub,dot
from exact_original_component_contacts_20261009 import contact_measure
from science_museum_original_open_sided_contact_topology_attribution_v1_20261011 import relative_interior
from exact_original_face_conservative_clearance_v5_20261010 import verify as finite
from exact_original_triangle_pair_column_gap_20261010 import verify as column
from exact_closed_ground_aabb_pruning_v1_20261011 import CompleteGround
from exact_original_upper_ground_interfaces_20261009 import exact_upper_ground_interfaces
from original_bound_facet_wall_context_v3_20261010 import best_original_vertex_exposure
B=ROOT/'docs/astra-city/government-import';T=B/'government-xl-science-museum-original-open-sided-contact-topology-attribution-v1-20261011';M=B/'government-xl-science-museum-original171-bounded-mount-grade-context-v1-20261011';DOC=B/'government-xl-science-museum-original24-body-graph-bounded-grade-caps-v1-20261011'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists()
 for folder in [T,M]:
  r=read(folder/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  for e in r['evidenceRefs']:assert ref(ROOT/e['path'])==e
 t=read(T/'diagnostic.json.gz');m=read(M/'diagnostic.json.gz');selection=B/'government-xl-science-museum-partial-parent-20261005/selection.json.gz';row=next(r for r in read(selection)['rows']if r['uid']=='landsd/80343:0');asset=ROOT/row['candidate']['path'];assert ref(asset)['sha256']==row['sourceSHA256']=='df4eeb38ea777cf3016a497db81c0c2a36ea880da7a3cb5b27a426e8768dbe28';tri=decode_original_world_triangles(asset.read_bytes());assert tri.shape==(11520,3,3)and digest(tri.astype('<f8').tobytes())==m['originalMuseumWorldSHA256'];bodies=t['originalMuseum11520FaceCensus']['sharedEdgeConnectedComponents'];assert len(bodies)==24;labels={i:k for k,fs in enumerate(bodies)for i in fs};zeros=t['originalMuseum11520FaceCensus']['exactNonrenderingOriginalFaces'];assert set(labels)|set(zeros)==set(range(11520));lo=tri.min(1);hi=tri.max(1);records=[];possible=0;tested=0;rf={}
 def face(i):
  if i not in rf:rf[i]=rational_face(tri[i])
  return rf[i]
 for k,fs in enumerate(bodies):
  others=np.asarray([i for z in bodies[k+1:]for i in z],int);possible+=len(fs)*len(others)
  for i in fs:
   if not len(others):continue
   js=others[np.all(hi[others]>=lo[i],axis=1)&np.all(hi[i]>=lo[others],axis=1)];tested+=len(js)
   for j0 in js:
    j=int(j0);a,b=face(i),face(j);points=sorted(intersection_points(a,b))
    if not points:continue
    measure=contact_measure(points);na=cross(sub(a[1],a[0]),sub(a[2],a[0]));nb=cross(sub(b[1],b[0]),sub(b[2],b[0]));cop=not any(cross(na,nb))and all(dot(na,sub(p,a[0]))==0 for p in b);mid=tuple(sum(p[h]for p in points)/len(points)for h in range(3));records.append(dict(originalFaces=[i,j],originalNonzeroBodies=[labels[i],labels[j]],exactIntersectionPoints=[[str(v)for v in p]for p in points],coplanar=cop,bothRelativeInteriorSurfaceCrossing=not cop and measure['dimension']>0 and relative_interior(a,mid)and relative_interior(b,mid),**measure))
  print(json.dumps(dict(completeBodiesThrough=k,exactAABBPairs=tested,allFiniteContacts=len(records))),flush=True)
 runtime=HERE/'local/government-xl-science-museum-partial-parent-20261005/runtime-geometry.json.gz';r=next(x for x in read(runtime)['rows']if x['uid']=='landsd/80343:0');assert r['sourceSHA256']==row['sourceSHA256'];ground=np.asarray(r['drawnGroundGeometry'],float).reshape(-1,3,3);ground=ground[np.any(np.cross(ground[:,1]-ground[:,0],ground[:,2]-ground[:,0])!=0,axis=1)];assert digest(ground.astype('<f8').tobytes())==m['historicalGroundCompleteCapturedArraySHA256'];complete_ground=CompleteGround(ground);assert complete_ground.ground_sha==m['historicalGroundCompleteCapturedArraySHA256'];nodes={};edges={};routes=[];qualified_cap_interfaces=[]
 def qualify(i):
  if i in nodes:return nodes[i]
  f=tri[i];n=np.cross(f[1]-f[0],f[2]-f[0]);p=finite(f,ground);lower=F(p['exactCertifiedLowerClearanceM']);pieces=[];wall=n[1]==0 and np.any(n);interfaces=exact_upper_ground_interfaces(tri,[i],ground)if wall else[];exposure=best_original_vertex_exposure(f,ground)if interfaces else None;grade=bool(interfaces)and exposure is not None and F(exposure['exactExposureLowerBoundM'])>0
  if p['groundProjectionCovered']and lower<=0:
   pieces=[dict(originalGroundFace=j,proof=column(f,ground[j]))for j in p['allProjectedBoundingCandidateOriginalGroundFacets']];gaps=[F(z['proof']['exactMinimumFiniteColumnGapM'])for z in pieces if z['proof']['exactClosedHorizontalProjectionsMeet']];assert gaps;lower=min(gaps)
  clear=p['groundProjectionCovered']and lower>0;up=bool(n[1]>0 and n[1]/np.linalg.norm(n)>.25);nodes[i]=dict(originalFace=i,wholeFiniteProof=p,refinedFiniteColumnPieces=pieces,exactLowerM=str(lower),strictClear=bool(clear),genuineExposedVerticalGradeWall=bool(grade),positiveExactUpperGroundInterfaces=interfaces,gradeVertexExposure=exposure,strictClearUpwardCap=bool(clear and up),eligible=bool(clear or grade));return nodes[i]
 def edge(a,b,key):
  pair=tuple(sorted([a,b]))
  if pair in edges:return edges[pair]
  proof=complete_ground.segment([[str(F(float(v)))for v in p]for p in key]);edges[pair]=dict(originalFaces=list(pair),wholeSharedSourceEdge=[list(p)for p in key],exactAABBCandidateGroundFaces=proof['originalGroundFaceBySelectedKernelFace'],completeHistoricalGroundSHA256=m['historicalGroundCompleteCapturedArraySHA256'],wholeExposedEdgeProof=proof,eligible=proof['strictlyExposedWholePositiveInterface']);return edges[pair]
 for body in [5,16]:
  fs=bodies[body];assert len(fs)==(32 if body==5 else 36);prior=m['completeHistoricalMuseumMinimumEdgeGradeInventory'][body];assert len(prior['completeOriginalMinimumHeightEdges'])==12 and all(z['fixedBandAgainstCompleteHistoricalDrawnGround']['verifiedCompleteOriginalEdgeContactBand']for z in prior['completeOriginalMinimumHeightEdges']);inc=defaultdict(set)
  for i in fs:
   qualify(i)
   for j in range(3):inc[tuple(sorted([tuple(tri[i,j]),tuple(tri[i,(j+1)%3])]))].add(i)
  roots=sorted(i for i in fs if nodes[i]['genuineExposedVerticalGradeWall']);parent={i:None for i in roots};queue=deque(roots)
  while queue:
   a=queue.popleft()
   for j in range(3):
    key=tuple(sorted([tuple(tri[a,j]),tuple(tri[a,(j+1)%3])]))
    for b in sorted(inc[key]-{a}):
     if b in parent or not nodes[b]['eligible']:continue
     if edge(a,b,key)['eligible']:parent[b]=a;queue.append(b)
  caps=sorted(i for i in parent if nodes[i]['strictClearUpwardCap']);paths=[]
  for cap in caps:
   path=[cap]
   while parent[path[-1]]is not None:path.append(parent[path[-1]])
   paths.append(dict(strictCapOriginalFace=cap,qualifiedWholeExposedSharedEdgePathToGrade=path))
   for raw in records:
    if cap not in raw['originalFaces']or raw['dimension']<=0:continue
    other=next(i for i in raw['originalFaces']if i!=cap)
    if labels[other]!=0:continue
    points=raw['exactIntersectionPoints'];ids=[];proof=None
    if raw['dimension']==1:
     assert len(points)==2;proof=complete_ground.segment(points);ids=proof['originalGroundFaceBySelectedKernelFace']
    else:assert raw['dimension']==2 and raw['coplanar']
    qualified_cap_interfaces.append(dict(completeCoplanarAreaPatchInsideWholeStrictClearCap=raw['dimension']==2,originalGradeBody=body,originalStrictCapFace=cap,contactedMuseumBody0Face=other,frozenGraphContact=raw,wholeContactSegmentExposureProof=proof,exactAABBCandidateGroundFaces=list(map(int,ids)),body0FullFiniteFacet=qualify(other),surfaceInterfaceOnlyNoLoadOrWholeBodyCredit=True))
  routes.append(dict(originalMuseumBody=body,completeOriginalBodyFaces=fs,allGenuineGradeFaces=roots,allStrictClearCapsReachedByWholeExposedEdges=paths,completeBoundedEligibleParentGraph=parent,complete32Or36FaceQualification=True))
 refs=[ref(p)for p in [Path(__file__),asset,selection,T/'diagnostic.json.gz',T/'result.json',M/'diagnostic.json.gz',M/'result.json',runtime,HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_shell_intersections_20261009.py',HERE/'exact_original_component_contacts_20261009.py',HERE/'science_museum_original_open_sided_contact_topology_attribution_v1_20261011.py',HERE/'exact_original_face_conservative_clearance_v5_20261010.py',HERE/'exact_original_triangle_pair_column_gap_20261010.py',HERE/'exact_closed_ground_aabb_pruning_v1_20261011.py',HERE/'test_exact_closed_ground_aabb_pruning_v1_20261011.py',HERE/'exact_original_rational_interface_segment_clearance_20261011.py',HERE/'exact_original_upper_ground_interfaces_20261009.py',HERE/'original_bound_facet_wall_context_v3_20261010.py',HERE/'original_bound_facet_wall_context_v2_20261010.py',HERE/'exact_original_projection_coverage_v2_20261010.py']]
 complete_ground.verify_binding()
 save(DOC/'diagnostic.json.gz',dict(uids=['landsd/80343:0','landsd/83471:0'],completeOriginalMuseumFaces=11520,completeOriginalMuseumNonzeroBodies=24,completeMuseumOriginalWorldSHA256=m['originalMuseumWorldSHA256'],completeCrossBodyFacetPairsConsidered=possible,completeInclusiveUnpadded3DAABBPairsTested=tested,allExactOriginalMuseumCrossBodyContacts=records,exactZeroMuseumFacesPreserved=zeros,completeTwoSourceBodyGradeCapRoutes=routes,qualifiedCapToBody0SurfaceInterfaceContexts=qualified_cap_interfaces,allExaminedWholeFacetProofs=list(nodes.values()),allExaminedWholeSharedEdgeProofs=list(edges.values()),historicalCompleteGroundSHA256=m['historicalGroundCompleteCapturedArraySHA256'],historicalGradeOnly=True,higherWallsOutside68FacetDomainNotExcluded=True,allRecovered171BodyRolesUnqualified=True,wholeMuseumBody0RootCredit=False,wholeMuseumReaccepted=False,wholeNativeReaccepted=False,currentAcceptance=False,identityAccepted=False,installationApproved=False,sourceOnly=True,geometryChanges=0,qualification='Complete24-body original finite surface-contact graph plus complete source bodies5/16 historical exact exposed grade-wall/whole exposed shared-edge/strict finite upward-cap route probes. Cross-body contact and graph reachability never grant support. Cap-to-body0 segments (whole exposed segment proof) or coplanar area patches inside an independently whole-facet strictly clear cap, and body0 facets are independently finite checked; no whole body0 grounding/load/mount/architecture credit. All recovered171 open facade roles,17 internal crossings/53 Museum crossings, identity mismatch/current ground/foreign/native/runtime and higher-wall obligations remain independent. No modified mesh or current capture.',evidenceRefs=refs));print(json.dumps(dict(sourceOnly=True,possiblePairs=possible,exactPairs=tested,contacts=len(records),qualifiedCapToBody0Segments=len(qualified_cap_interfaces),currentAcceptance=False)),flush=True)
if __name__=='__main__':main()
