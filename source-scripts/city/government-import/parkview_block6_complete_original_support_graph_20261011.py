"""Complete original cross-edge-body interfaces and one explicitly bounded native path.
No source changes, inferred roots, point glue, whole-native approval or live capture.
"""
from pathlib import Path
from collections import defaultdict,deque
from fractions import Fraction as F
import numpy as np,shapely,json
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_finite_triangle_contacts_20261010 import finite_intersection_points
from exact_original_shell_intersections_20261009 import rational_face
from exact_original_component_contacts_20261009 import contact_measure
from exact_original_face_conservative_clearance_v5_20261010 import verify as finite
from exact_original_rational_interface_segment_clearance_20261011 import verify as segment
from exact_original_upper_ground_interfaces_20261009 import exact_upper_ground_interfaces
from original_bound_facet_wall_context_v3_20261010 import best_original_vertex_exposure
BASE=ROOT/'docs/astra-city/government-import';OLD=BASE/'government-xl-parkview-block6-bounded-original-clear-cap-probe-v1-20261011'
BATCH='government-xl-parkview-block6-complete-original-support-paths-v1-20261011';DOC=BASE/BATCH
PROBE=BASE/'government-xl-terrain-recovery-parkview-block11-complete-original-proposed-current-probe-v4-20261011'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();r=read(OLD/'diagnostic.json.gz');ownpath=ROOT/r['evidenceRefs'][2]['path'];own=decode_original_world_triangles(ownpath.read_bytes());assert digest(own.tobytes())==r['completeOriginalOwnedWorldSHA256'];cs=r['completeOwnedNonzeroEdgeCensus']['sharedEdgeConnectedComponents'];labels=np.zeros(len(own),int)
 for i,fs in enumerate(cs):labels[fs]=i
 lo=own.min(1);hi=own.max(1);tree=shapely.STRtree(shapely.box(lo[:,0],lo[:,2],hi[:,0],hi[:,2]));records=[];pairs=0;cache={};adj={i:set()for i in range(len(cs))}
 for i,f in enumerate(own):
  js=tree.query(shapely.box(lo[i,0],lo[i,2],hi[i,0],hi[i,2]));js=js[(js>i)&(labels[js]!=labels[i])&(hi[js,1]>=lo[i,1])&(lo[js,1]<=hi[i,1])]
  for j in sorted(map(int,js)):
   pairs+=1;assert pairs<=20000
   if i not in cache:cache[i]=rational_face(own[i])
   if j not in cache:cache[j]=rational_face(own[j])
   points=finite_intersection_points(cache[i],cache[j])
   if points:
    a,b=int(labels[i]),int(labels[j]);measure=contact_measure(points);records.append(dict(bodies=[a,b],originalFaces=[i,j],**measure))
    if measure['dimension']>0:adj[a].add(b);adj[b].add(a)
 parents={0:None};q=deque([0])
 while q:
  a=q.popleft()
  for b in sorted(adj[a]):
   if b not in parents:parents[b]=a;q.append(b)
 nativepath=ROOT/next(x['path']for x in r['evidenceRefs']if x['path'].endswith('glb.gz')and x['path']!=str(ownpath.relative_to(ROOT)));n=decode_original_world_triangles(nativepath.read_bytes());assert digest(n.tobytes())==r['completeOriginalNativeWorldSHA256'];runtime=HERE/'local'/PROBE.name/'runtime-geometry.json.gz';rt=next(x for x in read(runtime)['rows']if x['uid']=='landsd/254491:0');g=np.asarray(rt['drawnGroundGeometry'],float).reshape(-1,3,3);assert digest(g.tobytes())==r['completeCurrentGroundSHA256']
 path=[45598,54320,54319,54656,54655,58400];interfaces=exact_upper_ground_interfaces(n,[path[0]],g);exposure=best_original_vertex_exposure(n[path[0]],g);facetproofs=[dict(face=i,proof=finite(n[i],g))for i in path[:-1]];edges=[]
 for a,b in zip(path,path[1:]):
  shared=sorted(set(map(tuple,n[a]))&set(map(tuple,n[b])));assert len(shared)==2
  edges.append(dict(faces=[a,b],sharedOriginalEdge=[[str(F(float(v)))for v in p]for p in shared],proof=segment([[str(F(float(v)))for v in p]for p in shared],g)))
 cap=read(OLD/'paired-cap-refinement.json.gz');assert cap['strictWholeCapClear']
 refs=[ref(p)for p in [Path(__file__),OLD/'result.json',OLD/'diagnostic.json.gz',OLD/'paired-cap-refinement.json.gz',ownpath,nativepath,runtime,PROBE/'selection.json.gz',HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_finite_triangle_contacts_20261010.py',HERE/'exact_original_shell_intersections_20261009.py',HERE/'exact_original_component_contacts_20261009.py',HERE/'exact_original_face_conservative_clearance_v5_20261010.py',HERE/'exact_original_rational_interface_segment_clearance_20261011.py',HERE/'exact_original_upper_ground_interfaces_20261009.py',HERE/'original_bound_facet_wall_context_v3_20261010.py',HERE/'original_bound_facet_wall_context_v2_20261010.py',HERE/'exact_original_projection_coverage_v2_20261010.py']]
 result=dict(uids=r['uids'],completeOriginalFaces=11041,completeOriginalWorldSHA256=digest(own.tobytes()),completeSourceEdgeBodyFaces=cs,completeCrossBodyAABBCandidatePairs=pairs,allExactCrossBodyContacts=records,completePositiveDimensionalAdjacency={a:sorted(bs)for a,bs in adj.items()},mainBodyRootIsConditionalCarrierContactOnly=True,completeConditionalParents=parents,unreachedBodies=sorted(set(adj)-set(parents)),allOriginalBodiesHaveConditionalPositiveInterfacePath=len(parents)==len(cs),nativePathFaces=path,gradeWallExactInterfaces=interfaces,gradeWallCompleteVertexExposure=exposure,nativePathFacetProofs=facetproofs,nativePathCompleteSharedEdgeProofs=edges,strictCapRef=ref(OLD/'paired-cap-refinement.json.gz'),completePinnedGroundSHA256=digest(g.tobytes()),nativePathAllSharedEdgesStrictlyExposed=all(p['proof']['strictlyExposedWholePositiveInterface']for p in edges),sourceOnly=True,currentAcceptance=False,structuralSupportAccepted=False,sourceGeometryChanges=0,installationApproved=False,newlyInstalled=0,evidenceRefs=refs)
 save(DOC/'diagnostic.json.gz',result);print(json.dumps(dict(candidatePairs=pairs,contacts=len(records),reached=len(parents),unreached=result['unreachedBodies'],gradeInterfaces=len(interfaces),exposure=exposure['exactExposureLowerBoundM'],edgeExposed=[p['proof']['strictlyExposedWholePositiveInterface']for p in edges],facetbounds=[(p['face'],p['proof'].get('exactCertifiedLowerClearanceM'),p['proof']['groundProjectionCovered'])for p in facetproofs])),flush=True)
if __name__=='__main__':main()
