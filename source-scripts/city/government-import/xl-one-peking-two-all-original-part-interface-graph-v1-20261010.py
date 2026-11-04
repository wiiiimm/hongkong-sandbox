"""Every original part interface, with zero-area primitive contacts kept separate."""
import importlib.util,json
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
BATCH='government-xl-one-peking-two-all-original-part-interface-graph-v1-20261010'
BASE=ROOT/'docs/astra-city/government-import';DOC=BASE/BATCH
PARTS=BASE/'government-xl-one-peking-two-complete-original-component-contacts-v2-20261010'
SOURCE=BASE/'government-xl-one-peking-hullett-complete-original-boundary-context-v1-20261010'
def main():
 assert not DOC.exists();parts=read(PARTS/'diagnostic.json.gz');source=read(SOURCE/'diagnostic.json.gz');rows={r['uid']:r for r in source['sources']};meshes={};nodes=[];assets=[]
 for actor in parts['actors']:
  uid=actor['uid'];p=ROOT/rows[uid]['source']['path'];raw=p.read_bytes();assert digest(raw)==actor['sourceSHA256'];a=decode_original_world_triangles(raw);assert digest(a.astype('<f8').tobytes())==actor['worldTrianglesSHA256']
  meshes[uid]=a;assets.append(p)
  for i,ids in enumerate(actor['completeOriginalParts']):
   selected=a[ids];nodes.append(dict(uid=uid,part=i,originalFaceIDs=ids,bounds=[selected.min((0,1)).tolist(),selected.max((0,1)).tolist()]))
 contacts=[];tested_component_pairs=0;rejected_bounds_pairs=0
 for ia,left in enumerate(nodes):
  alo,ahi=np.asarray(left['bounds'])
  for ib in range(ia+1,len(nodes)):
   right=nodes[ib];blo,bhi=np.asarray(right['bounds'])
   if np.any(ahi<blo) or np.any(bhi<alo):rejected_bounds_pairs+=1;continue
   proof=exact_finite_contacts(meshes[left['uid']],left['originalFaceIDs'],meshes[right['uid']],right['originalFaceIDs']);assert proof['allPairsExamined'];tested_component_pairs+=1
   if proof['contacts']:
    area_interfaces=[c for c in proof['contacts'] if c['dimension']>0 and c['sourcePrimitiveDimensionA']==c['sourcePrimitiveDimensionB']==2]
    contacts.append(dict(nodeA=ia,nodeB=ib,completeFiniteContactProof=proof,positiveTwoAreaPrimitiveInterfaces=area_interfaces,nonStructuralPointOrSegmentPrimitiveContacts=[c for c in proof['contacts'] if not(c['dimension']>0 and c['sourcePrimitiveDimensionA']==c['sourcePrimitiveDimensionB']==2)]))
 graph={i:[] for i in range(len(nodes))}
 for edge in contacts:
  if edge['positiveTwoAreaPrimitiveInterfaces']:graph[edge['nodeA']].append(edge['nodeB']);graph[edge['nodeB']].append(edge['nodeA'])
 # This is only a source association diagnosis. The two largest-part seeds
 # have not yet been certified against actual current ground/footings.
 seeds=[i for i,n in enumerate(nodes) if n['part']==0];reached=set(seeds);todo=list(seeds)
 while todo:
  for j in graph[todo.pop()]:
   if j not in reached:reached.add(j);todo.append(j)
 out=dict(uids=list(meshes),nodes=nodes,completePartInterfacePairs=contacts,totalParts=len(nodes),testedComponentPairs=tested_component_pairs,boundsRejectedComponentPairs=rejected_bounds_pairs,allPartPairsAccounted=tested_component_pairs+rejected_bounds_pairs==len(nodes)*(len(nodes)-1)//2,areaFacetAssociationSeedsOnly=seeds,areaFacetAssociationReachableNodes=sorted(reached),sourceAssociationUnconnectedNodes=sorted(set(graph)-reached),sourceGeometryChanges=0,physicalSupportAccepted=False,groundRootsAccepted=False,installationApproved=False,qualification='Complete finite part graph only. All point/segment primitive contacts remain explicit and give zero structural graph credit. Two area-facet interfaces are association evidence only, not rooted/support/collision acceptance. All actual current ground/footings, finite clearance/foreign/runtime roles remain required.')
 save(DOC/'diagnostic.json.gz',out)
 s=importlib.util.spec_from_file_location('peking_full_part_graph_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 m.freeze(BATCH,'complete-original-part-interface-graph-source-association-only-v1',[Path(__file__),PARTS/'result.json',PARTS/'diagnostic.json.gz',SOURCE/'result.json',SOURCE/'diagnostic.json.gz',HERE/'exact_original_finite_triangle_contacts_20261010.py',HERE/'exact_original_shell_intersections_20261009.py',HERE/'exact_original_component_contacts_20261009.py',HERE/'exact_packed_world_geometry_20261009.py',*assets],out)
 print(json.dumps({k:out[k] for k in ['totalParts','testedComponentPairs','allPartPairsAccounted','areaFacetAssociationReachableNodes','sourceAssociationUnconnectedNodes']}),flush=True)
if __name__=='__main__':main()
