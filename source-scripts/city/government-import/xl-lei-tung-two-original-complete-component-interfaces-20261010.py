"""Complete unchanged two-original component interfaces; no support acceptance."""
import itertools,json,numpy as np
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_component_contacts_20261009 import exact_component_contacts
from source_closed_components import components
from lei_tung_lower_platform_current_bound_identity_20261010 import DOC as INPUT,UID,PLATFORM
BATCH='government-xl-lei-tung-two-original-complete-component-interfaces-20261010';DOC=INPUT.parent/BATCH

def main():
 assert not DOC.exists();rows=read(INPUT/'selection.json.gz')['rows'];worlds={};parts={};nodes={};edges=[];interfaces=[]
 for r in rows:
  raw=(ROOT/r['candidate']['path']).read_bytes();assert digest(raw)==r['sourceSHA256'];a=decode_original_world_triangles(raw);worlds[r['uid']]=a;parts[r['uid']]=components(a)['components']
  for i,p in enumerate(parts[r['uid']]):
   f=p['faceIndices'];v=a[f];key=r['uid']+'#'+str(i);nodes[key]={'uid':r['uid'],'component':i,'completeOriginalFaceIndices':f,'completeOriginalFaces':len(f),'sourceSHA256':r['sourceSHA256'],'worldBounds':[v.min((0,1)).tolist(),v.max((0,1)).tolist()],'originalTopology':p}
 for ka,kb in itertools.combinations(nodes,2):
  na,nb=nodes[ka],nodes[kb];a=worlds[na['uid']][na['completeOriginalFaceIndices']];b=worlds[nb['uid']][nb['completeOriginalFaceIndices']]
  if np.any(a.min((0,1))>b.max((0,1))) or np.any(b.min((0,1))>a.max((0,1))):continue
  c=exact_component_contacts(worlds[na['uid']],na['completeOriginalFaceIndices'],worlds[nb['uid']],nb['completeOriginalFaceIndices'],maximum_pairs=1000000);pos=[v for v in c['contacts'] if v['dimension']>0];interfaces.append({'componentA':ka,'componentB':kb,'completeExactContacts':c,'positiveInterfaces':pos})
  if pos:edges.append([ka,kb])
 anchors=[UID+'#5',UID+'#9'];reachable=set(anchors)
 while True:
  old=set(reachable)
  for a,b in edges:
   if a in reachable:reachable.add(b)
   if b in reachable:reachable.add(a)
  if old==reachable:break
 refs=[Path(__file__),INPUT/'selection.json.gz',HERE/'exact_packed_world_geometry_20261009.py',HERE/'source_closed_components.py',HERE/'exact_original_component_contacts_20261009.py']+[ROOT/r['candidate']['path'] for r in rows]
 save(DOC/'diagnostic.json.gz',{'uids':[UID,PLATFORM],'completeOriginalFaceCounts':[len(worlds[UID]),len(worlds[PLATFORM])],'completeOriginalComponentCounts':[len(parts[UID]),len(parts[PLATFORM])],'completeOriginalWorldHashes':{u:digest(a.astype('<f8').tobytes()) for u,a in worlds.items()},'completeOriginalComponentNodes':nodes,'completeExactOriginalInterfaces':interfaces,'positiveDimensionalEdges':edges,'provisionalUpperMainComponents':anchors,'connectedToUpperMainByOriginalPositiveContacts':sorted(reachable),'notConnectedToUpperMain':sorted(set(nodes)-reachable),'inputHashes':{str(p.relative_to(ROOT)):digest(p.read_bytes()) for p in refs},'groundAnchorAccepted':False,'physicalAccepted':False,'installationApproved':False,'qualification':'Complete original source component contact graph only. Every component retained; positive dimensional contacts distinct from point touches. Upper-main contacts are not terrain roots or structural/load-bearing certification. Current drawn ground/full source foundation/foreign/native/runtime gates remain independent.'});print(json.dumps({'components':len(nodes),'positiveComponentEdges':len(edges),'connected':len(reachable),'notConnected':sorted(set(nodes)-reachable)}),flush=True)
if __name__=='__main__':main()
