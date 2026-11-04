"""Complete source membership/topology context for 132 still-unrooted bodies.

Source geometry is never edited. Images highlight original triangles and show
explicitly cropped source host context, not a physical or architectural proof.
No body is classified as machinery, signage, a closed solid or a visual role.
"""
from pathlib import Path
from collections import defaultdict,deque
import gzip,json,struct,importlib.util,uuid
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shared_edge_component_census_v2_20261011 import census
BASE=ROOT/'docs/astra-city/government-import'
BATCH='xl-terrain-recovery-20261011-elements132-remaining-original-bodies-context-v1';DOC=BASE/BATCH
GRAPH=BASE/'xl-terrain-recovery-20261011-elements-complete-owned-original-contact-graph-v1'
CAPS=BASE/'xl-terrain-recovery-20261011-elements998-bounded-four-stream-grade-cap-paths-v1'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def primitive_inventory(raw,offset):
 data=gzip.decompress(raw);magic,version,total=struct.unpack_from('<III',data);assert magic==0x46546c67 and version==2 and total==len(data)
 size,kind=struct.unpack_from('<II',data,12);assert kind==0x4e4f534a;doc=json.loads(data[20:20+size]);rows=[];cursor=offset
 def visit(node_id,ancestors):
  nonlocal cursor
  assert node_id not in ancestors;node=doc['nodes'][node_id]
  if 'mesh'in node:
   for primitive_id,p in enumerate(doc['meshes'][node['mesh']]['primitives']):
    assert p.get('mode',4)==4 and 'indices'in p;count=doc['accessors'][p['indices']]['count'];assert count%3==0
    rows.append(dict(node=node_id,ancestors=ancestors,mesh=node['mesh'],primitive=primitive_id,indicesAccessor=p['indices'],attributes=p['attributes'],globalOriginalFaces=list(range(cursor,cursor+count//3))));cursor+=count//3
  for child in node.get('children',[]):visit(child,ancestors+[node_id])
 for root in doc['scenes'][doc.get('scene',0)]['nodes']:visit(root,[])
 return rows,cursor,dict(providerRootHierarchySHA256=digest(json.dumps(doc,sort_keys=True,separators=(',',':')).encode()),completeSceneRootNodes=doc['scenes'][doc.get('scene',0)]['nodes'])
def main():
 assert not DOC.exists();refs=[ref(Path(__file__))]
 for folder in [GRAPH,CAPS]:
  r=read(folder/'result.json')
  with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  refs.extend([ref(folder/'result.json'),ref(folder/'diagnostic.json.gz')]);assert ref(folder/'diagnostic.json.gz')in r['evidenceRefs']
 g=read(GRAPH/'diagnostic.json.gz');caps=read(CAPS/'diagnostic.json.gz');seedset=set.intersection(*[{r['ownedBody']for r in row['all20OriginalInterfacesAccounted']if r['diagnosticStrictGradeCapPath']}for row in caps['rows']]);adj=defaultdict(set)
 for row in g['oneExactPositiveWitnessPerOwnedInvolvingBodyPair']:
  a,b=row['components']
  if b<998:adj[a].add(b);adj[b].add(a)
 reached=set(seedset);q=deque(sorted(seedset))
 while q:
  for other in sorted(adj[q.popleft()]):
   if other not in reached:reached.add(other);q.append(other)
 remaining=sorted(set(range(998))-reached);assert len(reached)==866 and len(remaining)==132
 worlds=[];primitive_rows=[];hierarchy=[];offset=0
 for source,count in zip(g['binding']['completeSourceInputs'][:2],[12129,11680]):
  p=ROOT/source['asset']['path'];assert ref(p)==source['asset'];refs.append(ref(p));raw=p.read_bytes();world=decode_original_world_triangles(raw);assert len(world)==count
  assert digest(world.tobytes())==caps['rows'][0]['completeWorldSHA256'][source['uid']]
  rows,end,root=primitive_inventory(raw,offset);assert end==offset+count;primitive_rows.extend(rows);hierarchy.append(dict(uid=source['uid'],sourceSHA256=source['sourceSHA256'],**root));worlds.append(world);offset=end
 world=np.concatenate(worlds);assert len(world)==23809;face_primitive={f:p for p in primitive_rows for f in p['globalOriginalFaces']};assert set(face_primitive)==set(range(23809))
 helpers=['exact_packed_world_geometry_20261009.py','exact_original_shared_edge_component_census_v2_20261011.py','xl-popcorn-source-investigations-checkpoints-20261009.py'];refs.extend(ref(HERE/n)for n in helpers)
 claim=reservations.claim('elements132-source-context-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];records=[]
 try:
  for body_id in remaining:
   row=g['components'][body_id];ids=row['globalOriginalFaces'];t=world[ids];edgefaces=defaultdict(list)
   for face in ids:
    for a,b in zip(world[face],np.roll(world[face],-1,axis=0)):
     if tuple(a)==tuple(b):continue
     edge=tuple(sorted([tuple(a),tuple(b)]));edgefaces[edge].append(dict(globalOriginalFace=face,originalDirectedEndpoints=[a.tolist(),b.tolist()]))
   edges=[dict(originalUndirectedEndpoints=[list(p)for p in e],incidences=faces)for e,faces in sorted(edgefaces.items())];boundary=[r for r in edges if len(r['incidences'])==1]
   inv=census(world,ids);assert len(inv['sharedEdgeConnectedComponents'])==1 and not inv['exactNonrenderingOriginalFaces']
   membership=[]
   for p in primitive_rows:
    selected=sorted(set(ids)&set(p['globalOriginalFaces']))
    if selected:membership.append(dict(**{k:v for k,v in p.items()if k!='globalOriginalFaces'},globalOriginalFaces=selected))
   assert sorted(f for p in membership for f in p['globalOriginalFaces'])==ids
   records.append(dict(originalBody=body_id,actorUID=row['actorUID'],completeGlobalOriginalFaces=ids,completeOriginalBounds=row['bounds'],completeExactEdgeCensus=inv,completeOriginalEdgeInventory=edges,completeOriginalBoundaryEdges=boundary,completeSourcePrimitiveMembership=membership,closedSolidOrFunctionCertified=False,visualRoleAccepted=False,rootOrBridgeCredit=False))
   if len(records)%16==0:assert reservations.heartbeat(lease)['ok']and reservations.owns(lease)
  def panel(ax,body_id,with_host):
   row=g['components'][body_id];ids=row['globalOriginalFaces'];t=world[ids];lo=t.min((0,1));hi=t.max((0,1));extent=hi-lo;margin=np.maximum(extent*.15,[.2,.2,.2]);context=[]
   if with_host:
    host=4 if row['actorUID']=='landsd/204145:0' else 657;hostids=g['components'][host]['globalOriginalFaces'];tri=world[hostids];keep=np.all(tri.max(1)>=lo-margin,axis=1)&np.all(tri.min(1)<=hi+margin,axis=1);context=[f for f,k in zip(hostids,keep)if k]
    if context:ax.add_collection3d(Poly3DCollection(world[context][:,:,[0,2,1]],facecolors='#c4cdd6',edgecolors='#7b8794',linewidths=.1,alpha=.32))
   ax.add_collection3d(Poly3DCollection(t[:,:,[0,2,1]],facecolors='#cc3d36',edgecolors='#69221e',linewidths=.15,alpha=.85))
   ax.set_xlim(lo[0]-margin[0],hi[0]+margin[0]);ax.set_ylim(lo[2]-margin[2],hi[2]+margin[2]);ax.set_zlim(lo[1]-margin[1],hi[1]+margin[1]);ax.set_box_aspect(np.maximum(extent+2*margin,.01)[[0,2,1]]);ax.view_init(elev=23,azim=-55);ax.set_title(str(body_id)+' / '+str(len(ids))+' original faces',fontsize=8);ax.set_axis_off()
   return dict(originalBody=body_id,completeHighlightedGlobalOriginalFaces=ids,croppedContextSourceFaces=context,contextIsVisualOnlyNotQualifiedHost=True)
  tall=sorted([i for i in remaining if i not in [839,893,902]],key=lambda i:g['components'][i]['bounds'][1][1]-g['components'][i]['bounds'][0][1],reverse=True)[:3];selected=[839,893,902]+tall
  fig=plt.figure(figsize=(18,10),dpi=100);render_refs=[]
  for k,i in enumerate(selected):render_refs.append(panel(fig.add_subplot(2,3,k+1,projection='3d'),i,True))
  fig.suptitle('Original remaining bodies: complete highlighted geometry / cropped source context / no role or support credit',fontsize=12);fig.tight_layout();DOC.mkdir(parents=True);fig.savefig(DOC/'remaining-rooftop-assemblies-and-tall-surfaces-1800x1000.png');plt.close(fig)
  fig=plt.figure(figsize=(24,51),dpi=100)
  for k,i in enumerate(remaining):panel(fig.add_subplot(17,8,k+1,projection='3d'),i,False)
  fig.suptitle('Every one of 132 original unrooted bodies; isolated original source geometry',fontsize=14);fig.tight_layout();fig.savefig(DOC/'all-132-isolated-original-bodies-2400x5100.png');plt.close(fig)
  assert all(ref(ROOT/r['path'])==r for r in refs);output=dict(uids=['landsd/204145:0','landsd/204143:0'],all132Bodies=records,completeRemainingOriginalFaces=sum(len(r['completeGlobalOriginalFaces'])for r in records),completeProviderHierarchy=hierarchy,selectedVisualPanels=render_refs,sourceGraph866ReachabilityNotPhysicalCredit=True,sourceOnly=True,currentAcceptance=False,visualRoleAccepted=False,sourceGeometryChanges=0,rootOrBridgeCredit=False,evidenceRefs=refs);save(DOC/'diagnostic.json.gz',output);assert reservations.heartbeat(lease)['ok']and reservations.owns(lease)
  spec=importlib.util.spec_from_file_location('elements132_context_freeze',HERE/helpers[-1]);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,'elements132-complete-original-body-boundary-primitive-visual-context-diagnostic-v1',[ROOT/r['path']for r in refs]+list(DOC.iterdir()),dict(uids=output['uids'],sourceOnly=True,completeUnrootedOriginalBodies=132,completeRemainingOriginalFaces=output['completeRemainingOriginalFaces'],visualRoleAccepted=False,currentAcceptance=False,newlyInstalled=0))
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
