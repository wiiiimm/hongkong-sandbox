"""Reusable complete unchanged indexed-source ordinary ground-root investigation.

Immutable source-only analysis of an existing hash-pinned physical snapshot.
Future throughput version: time-bounded lease heartbeats and eight-component
checkpoint batches avoid a database round trip for every tiny source island.
Exact pair discovery and final whole-graph recomputation remain unchanged.
No current acceptance, geometry edits, model-review state or publication.
"""
import argparse,json,subprocess,sys,uuid,time
from pathlib import Path
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest,reservations,jobs,connect,Jsonb,dict_row
from xl_source_stream_binding_20261009 import source_stream_binding
from exact_original_shell_intersections_20261009 import rational_face,intersection_points
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_ordinary_ground_root_graph_20261009 import verify

def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}
def main():
 p=argparse.ArgumentParser();p.add_argument('--uid',required=True,action='append');p.add_argument('--physical',required=True);p.add_argument('--batch',required=True);p.add_argument('--contact-reuse');p.add_argument('--max-components',type=int,default=80);args=p.parse_args();assert args.max_components>0
 doc=ROOT/'docs/astra-city/government-import'/args.batch;assert not doc.exists()
 prior=ROOT/args.physical;geometry=HERE/'local'/prior.name/'runtime-geometry.json.gz'
 rows=[r for r in read(prior/'selection.json.gz')['rows'] if r['uid'] in args.uid];assert len(rows)==len(set(args.uid))==len(args.uid)
 runtimes={r['uid']:r for r in read(geometry)['rows']};actors=[];indexed=[];pieces=[];groundpieces=[];cursor=0;assets=[];maximum_roundoff=0
 for source in rows:
  runtime=runtimes[source['uid']];asset=ROOT/source['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==source['sourceSHA256']==runtime['sourceSHA256'] and read(prior/'neon-sync.json')['resultVerified'];assets.append(asset)
  runtime_positions=np.asarray(runtime['position'],float).reshape(-1,3);indices=np.asarray(runtime['index'],dtype=np.uint32).reshape(-1,3);runtime_part=runtime_positions[indices];decoded=decode_original_world_triangles(raw);assert decoded.shape==runtime_part.shape and np.max(np.abs(decoded-runtime_part))<=1e-9;maximum_roundoff=max(maximum_roundoff,float(np.max(np.abs(decoded-runtime_part))));assert len(decoded)==source['native']['model']['triangles']
  # Source-author exact geometry, independently matched to every runtime index.
  # No tolerance is used for authored contact or merging disconnected parts.
  positions=np.empty_like(runtime_positions);assigned={}
  for ids,face in zip(indices,decoded):
   for vertex,point in zip(ids,face):
    vertex=int(vertex)
    if vertex in assigned:assert np.array_equal(assigned[vertex],point),'Original source assigns inconsistent shared vertex'
    else:assigned[vertex]=point;positions[vertex]=point
  assert set(assigned)==set(range(len(positions))),'Unreferenced original runtime vertex'
  part=positions[indices];assert np.array_equal(part,decoded)

  actors.append({'uid':source['uid'],'sourceSHA256':digest(raw),'originalStreamBindingSHA256':digest(json.dumps(source_stream_binding(raw),sort_keys=True,separators=(',',':')).encode()),'globalFaceRange':[cursor,cursor+len(part)],'completeOriginalFaceCount':len(part),'originalWorldTrianglesSHA256':digest(part.tobytes())})
  indexed.append({'uid':source['uid'],'sourceSHA256':digest(raw),'position':positions.reshape(-1).tolist(),'index':indices.reshape(-1).tolist()});pieces.append(part);groundpieces.append(np.asarray(runtime['drawnGroundGeometry'],float).reshape(-1,3,3));cursor+=len(part)
 tri=np.concatenate(pieces);ground=np.unique(np.concatenate(groundpieces).reshape(-1,9),axis=0).reshape(-1,3,3)
 claim=reservations.claim('ordinary-source-support-'+str(uuid.uuid4()),['immutable-source-proof:'+args.batch],batch=args.batch,ttl=3600);assert claim['ok'],claim;lease=json.loads(json.dumps(claim['reservation'],default=str));save(HERE/'local'/args.batch/'reservation.json',lease)
 try:
  components=[]
  for actor in actors:
   lo,hi=actor['globalFaceRange'];parent=list(range(len(tri)));edges={}
   def find(i):
    while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
    return i
   for i in range(lo,hi):
    vertices=[tuple(p) for p in tri[i]]
    for a,b in zip(vertices,vertices[1:]+vertices[:1]):
     edge=tuple(sorted((a,b)))
     if edge in edges:parent[find(i)]=find(edges[edge])
     else:edges[edge]=i
   groups={}
   for i in range(lo,hi):groups.setdefault(find(i),[]).append(i)
   components.extend({'actorUID':actor['uid'],'globalOriginalFaces':faces,'bounds':[tri[faces].min(axis=(0,1)).tolist(),tri[faces].max(axis=(0,1)).tolist()]} for faces in sorted(groups.values(),key=lambda f:min(f)))
  progress_path=HERE/'local'/args.batch/'compute-progress.json.gz'
  progress_binding=dict(runtimeGeometrySHA256=digest(geometry.read_bytes()),completeOriginalWorldTrianglesSHA256=digest(tri.tobytes()),completeOriginalComponentsSHA256=digest(json.dumps(components,sort_keys=True,separators=(',',':')).encode()),runnerSHA256=digest(Path(__file__).read_bytes()))
  contacts=[];rational={};tested=0;resume_component=0;last_heartbeat=time.monotonic();last_output=time.monotonic()
  def pulse(force=False):
   nonlocal last_heartbeat
   if force or time.monotonic()-last_heartbeat>=20:
    assert reservations.heartbeat(lease)['ok'];last_heartbeat=time.monotonic()
  if progress_path.exists():
   progress=read(progress_path);assert progress['binding']==progress_binding,'Saved computation input/runner differs';contacts=progress['contacts'];tested=progress['tested'];resume_component=progress['nextComponent'];assert type(resume_component) is int and 0<=resume_component<=len(components)
  reuse_refs=[]
  if args.contact_reuse:
   oldfolder=ROOT/args.contact_reuse;old=read(oldfolder/'diagnostic.json.gz');oldreceipt=read(oldfolder/'result.json')
   with connect() as c:
    c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(oldreceipt['jobId'],)).fetchone()==('complete',oldreceipt)
   assert old=={k:v for k,v in oldreceipt.items() if k!='jobId'} and ref(HERE/'original_ordinary_ground_root_graph_20261009.py') in oldreceipt['evidenceRefs']
   assert old['actors']==actors and old['components']==components and old['binding']['completeOriginalWorldTrianglesSHA256']==digest(tri.tobytes()) and old['binding']['originalIndexedSourcesSHA256']==digest(json.dumps(indexed,sort_keys=True,separators=(',',':')).encode())
   contacts=old['contactWitnesses'];tested=old['exactPairsTested'];resume_component=len(components);reuse_refs=[ref(oldfolder/'diagnostic.json.gz'),ref(oldfolder/'result.json')]
   save(progress_path,dict(binding=progress_binding,contacts=contacts,tested=tested,nextComponent=resume_component,completeProof=False,sourceContactDiscoveryOnlyReused=True,allGroundRootsAndEveryCreditedContactRecomputedByFinalKernel=True,reusedReceipt=ref(oldfolder/'result.json')))
  stopped_at=min(len(components),resume_component+args.max_components)
  def face(i):
   if i not in rational:rational[i]=rational_face(tri[i])
   return rational[i]
  for a in range(resume_component,stopped_at):
   ca=components[a]
   for b in range(a+1,len(components)):
    cb=components[b]
    if np.any(np.maximum(ca['bounds'][0],cb['bounds'][0])>np.minimum(ca['bounds'][1],cb['bounds'][1])):continue
    af=np.asarray(ca['globalOriginalFaces'],int);bf=np.asarray(cb['globalOriginalFaces'],int);small,large=(af,bf) if len(af)<=len(bf) else (bf,af)
    polys=shapely.box(tri[large,:,0].min(axis=1),tri[large,:,2].min(axis=1),tri[large,:,0].max(axis=1),tri[large,:,2].max(axis=1));tree=shapely.STRtree(polys);witness=None
    for i in small:
     t=tri[i]
     for k in tree.query(shapely.box(t[:,0].min(),t[:,2].min(),t[:,0].max(),t[:,2].max())):
      j=int(large[k]);u=tri[j]
      if t[:,1].max()<u[:,1].min() or u[:,1].max()<t[:,1].min():continue
      if not np.any(np.cross(t[1]-t[0],t[2]-t[0])) or not np.any(np.cross(u[1]-u[0],u[2]-u[0])):continue
      tested+=1
      if tested%500==0:pulse()
      if len(intersection_points(face(int(i)),face(j)))>=2:witness=[int(i),j] if int(i) in ca['globalOriginalFaces'] else [j,int(i)];break
     if witness:break
    if witness:contacts.append({'components':[a,b],'globalOriginalFaces':witness})
   if (a+1)%8==0 or a+1==stopped_at:
    save(progress_path,dict(binding=progress_binding,contacts=contacts,tested=tested,nextComponent=a+1,completeProof=False,qualification='In-progress compute cache only. Every credited contact/ground root recomputed by final strict graph verifier; partial discovery earns zero acceptance credit.'))
   pulse()
   if time.monotonic()-last_output>=20 or a+1==stopped_at:
    print(json.dumps({'component':a,'components':len(components),'contacts':len(contacts),'exactPairsTested':tested}),flush=True);last_output=time.monotonic()
  if stopped_at<len(components):
   print(json.dumps(dict(computeCheckpointOnly=True,nextComponent=stopped_at,totalComponents=len(components),contacts=len(contacts),exactPairsTested=tested,installationApproved=False)),flush=True);return
  binding={'completeOriginalWorldTrianglesSHA256':digest(tri.tobytes()),'currentDrawnGroundSHA256':digest(ground.tobytes()),'groundInterfacesInputSHA256':digest(geometry.read_bytes()),'supportScope':'complete-current-drawn-ground-only','originalIndexedSourcesSHA256':digest(json.dumps(indexed,sort_keys=True,separators=(',',':')).encode())}
  result=verify(tri,actors,components,contacts,indexed,ground,expected_binding=binding,current_binding=binding)
  refs=[ref(p) for p in [Path(__file__),geometry,prior/'selection.json.gz',prior/'result.json',progress_path,*assets,HERE/'original_ordinary_ground_root_graph_20261009.py',HERE/'test_original_ordinary_ground_root_graph_20261009.py',HERE/'original_ordinary_rim_accounting_20261009.py',HERE/'test_original_ordinary_rim_accounting_20261009.py',HERE/'original_wall_rim_accounting_20261009.py',HERE/'original_multi_actor_support_graph_20261009.py',HERE/'exact_original_shell_intersections_20261009.py',HERE/'exact_packed_world_geometry_20261009.py',HERE/'xl_source_stream_binding_20261009.py']]
  refs.extend(reuse_refs)
  result.update(sourceContactDiscoveryOnlyReused=bool(args.contact_reuse),allGroundRootsAndEveryCreditedContactFreshlyRecomputed=True,exactContactWorldBasis='complete-provider-root-decoded-original-world-no-coordinate-tolerance',batch=args.batch,uids=sorted(args.uid),actors=actors,components=components,contactWitnesses=contacts,binding=binding,exactPairsTested=tested,evidenceRefs=refs,originalPackedWorldMaximumNumericalRoundoffM=maximum_roundoff,currentRegionalRebindRequired=True,historicalInputHashes=read(geometry)['inputHashes'],installationApproved=False,newlyInstalled=0,scriptExternalAICalls=0,modelGeometryChanges=0,requiresCompute=True)
  result=json.loads(json.dumps(result));save(doc/'diagnostic.json.gz',result)
  stage='immutable-coupled-original-ordinary-ground-root-support-batched-discovery-v1';jid=jobs.enqueue(args.batch,stage,{'evidenceRefs':refs,'diagnostic':ref(doc/'diagnostic.json.gz')});job=jobs.claim(args.batch,lease['owner'],[stage],lease_seconds=1800);assert job and job['id']==jid
  final={**result,'jobId':jid}
  with connect() as con:
   con.row_factory=dict_row;con.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(con,lease)
   for r in refs:assert ref(ROOT/r['path'])==r
   assert con.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(final),jid,job['owner'],job['token'])).rowcount==1
  with connect() as con:
   con.execute('SET TRANSACTION READ ONLY');assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',final)
  save(doc/'result.json',final);save(doc/'neon-sync.json',{'jobId':jid,'resultVerified':True});print(json.dumps({'uid':args.uid,'jobId':jid,'supportInterfaceAccepted':result['supportInterfaceAccepted'],'components':len(components),'roots':result['ordinaryGroundRootComponents'],'reasons':result['reasons'],'publication':False}),flush=True)
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
