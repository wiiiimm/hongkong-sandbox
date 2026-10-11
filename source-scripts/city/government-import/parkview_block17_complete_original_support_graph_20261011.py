"""Block17 complete original cross-body contact graph, conditional cap path only.
No current capture/acceptance, geometry edits, point bridges or role inference.
"""
from pathlib import Path
from collections import deque
import numpy as np,shapely,json,time
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_finite_triangle_contacts_20261010 import finite_intersection_points
from exact_original_shell_intersections_20261009 import rational_face
from exact_original_component_contacts_20261009 import contact_measure
B=ROOT/'docs/astra-city/government-import'
OLD=B/'government-xl-parkview-next-three-original-cap-contacts-v1-20261011'
CAP=B/'government-xl-parkview-next-three-exact-cap-refinement-v1-20261011'
BATCH='government-xl-parkview-block17-complete-original-support-graph-v1-20261011'
DOC=B/BATCH;UID='landsd/256116:0'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();start=time.monotonic();old=read(OLD/'diagnostic.json.gz');r=next(x for x in old['rows']if x['uid']==UID);ownpath=ROOT/r['source']['path'];assert ref(ownpath)==r['source'];own=decode_original_world_triangles(ownpath.read_bytes());assert own.shape==(15614,3,3)and np.isfinite(own).all()and digest(own.tobytes())==r['completeOriginalWorldSHA256'];cs=r['completeOriginalNonzeroEdgeCensus']['sharedEdgeConnectedComponents'];accounted={f for c in cs for f in c};degenerate=sorted(set(range(len(own)))-accounted);assert len(cs)==93 and degenerate==[24,25]and all(not np.any(np.cross(own[i,1]-own[i,0],own[i,2]-own[i,0]))for i in degenerate);labels=np.full(len(own),-1,int)
 for i,fs in enumerate(cs):labels[fs]=i
 lo=own.min(1);hi=own.max(1);tree=shapely.STRtree(shapely.box(lo[:,0],lo[:,2],hi[:,0],hi[:,2]));records=[];pairs=0;cache={};adj={i:set()for i in range(len(cs))}
 for i,f in enumerate(own):
  if labels[i]<0:continue
  js=tree.query(shapely.box(lo[i,0],lo[i,2],hi[i,0],hi[i,2]));js=js[(js>i)&(labels[js]>=0)&(labels[js]!=labels[i])&(hi[js,1]>=lo[i,1])&(lo[js,1]<=hi[i,1])]
  for j in sorted(map(int,js)):
   pairs+=1;assert pairs<=50000,'Bounded graph candidate budget'
   if i not in cache:cache[i]=rational_face(own[i])
   if j not in cache:cache[j]=rational_face(own[j])
   points=finite_intersection_points(cache[i],cache[j])
   if points:
    a,b=int(labels[i]),int(labels[j]);measure=contact_measure(points);records.append(dict(bodies=[a,b],originalFaces=[i,j],**measure))
    if measure['dimension']>0:adj[a].add(b);adj[b].add(a)
  if i%2000==0:print(json.dumps(dict(face=i,candidates=pairs,contacts=len(records),elapsed=time.monotonic()-start)),flush=True)
 roots=r['directlyContactingOwnedNonzeroEdgeBodies'];assert roots==[0];parents={b:None for b in roots};q=deque(roots)
 while q:
  a=q.popleft()
  for b in sorted(adj[a]):
   if b not in parents:parents[b]=a;q.append(b)
 unreached=sorted(set(adj)-set(parents));details=[]
 for b in unreached:
  f=own[cs[b]];details.append(dict(body=b,faces=cs[b],originalBounds=[f.min((0,1)).tolist(),f.max((0,1)).tolist()],anyExactContacts=[c for c in records if b in c['bodies']],roleUnresolved=True))
 refs=[ref(p)for p in [Path(__file__),ownpath,OLD/'diagnostic.json.gz',OLD/'result.json',CAP/'diagnostic.json.gz',CAP/'result.json',HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_finite_triangle_contacts_20261010.py',HERE/'exact_original_shell_intersections_20261009.py',HERE/'exact_original_component_contacts_20261009.py',HERE/'exact_original_shared_edge_component_census_v2_20261011.py']]
 result=dict(uids=[UID],source=r['source'],completeOriginalFaces=len(own),completeOriginalWorldSHA256=digest(own.tobytes()),completeSourceEdgeBodyFaces=cs,completeOriginalDegenerateFaces=degenerate,degenerateFacesReceiveNoSupportOrBridgeCredit=True,degenerateRoleUnresolved=True,completeCrossBodyAABBCandidatePairs=pairs,allExactCrossBodyContacts=records,completePositiveDimensionalAdjacency={a:sorted(bs)for a,bs in adj.items()},conditionalCapRootBodies=roots,nativeOriginalCapFace=54418,mainBodyRootIsConditionalCarrierContactOnly=True,completeConditionalParents=parents,unreachedBodies=unreached,unreachedBodyDetails=details,allOriginalBodiesHaveConditionalPositiveInterfacePath=len(parents)==len(cs),historicalReasonsUnchanged=r['historicalReasonsUnchanged'],sourceOnly=True,currentAcceptance=False,structuralSupportAccepted=False,sourceGeometryChanges=0,terrainChanges=0,installationApproved=False,newlyInstalled=0,elapsedSeconds=time.monotonic()-start,evidenceRefs=refs)
 for x in refs:assert ref(ROOT/x['path'])==x
 save(DOC/'diagnostic.json.gz',result);print(json.dumps(dict(candidates=pairs,contacts=len(records),reached=len(parents),unreached=unreached,elapsed=result['elapsedSeconds'])),flush=True)
if __name__=='__main__':main()
