"""Test exact triangle closure before considering tower/podium solid-overlap review.

Diagnostic only. Closed edges do not establish a valid, self-intersection-free
solid or waive any source support, foundation, wall or runtime requirement.
"""
import importlib.util,json,subprocess,sys,uuid
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations,connect,jobs,Jsonb,dict_row
BATCH='government-xl-hsbc-original-assembly-topology-20261008'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
LOCAL=HERE/'local'/BATCH
OLD=ROOT/'docs/astra-city/government-import/government-xl-hsbc-centre-supports-20261005'
CONTEXT=ROOT/'docs/astra-city/government-import/government-xl-22-complete-group-official-context-v2-20261008'
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}
def module(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def topology(triangles):
 vertices,inverse=np.unique(triangles.reshape(-1,3),axis=0,return_inverse=True);faces=inverse.reshape(-1,3)
 edges=np.concatenate([faces[:,[0,1]],faces[:,[1,2]],faces[:,[2,0]]]);ordered=np.sort(edges,axis=1)
 _,edge_inverse,counts=np.unique(ordered,axis=0,return_inverse=True,return_counts=True)
 winding=np.bincount(edge_inverse,weights=np.where(edges[:,0]<edges[:,1],1,-1))
 cross=np.cross(triangles[:,1]-triangles[:,0],triangles[:,2]-triangles[:,0]);degenerate=np.linalg.norm(cross,axis=1)<=1e-12
 centred=triangles-vertices.mean(axis=0)
 volume=float(np.einsum('ij,ij->i',centred[:,0],np.cross(centred[:,1],centred[:,2])).sum()/6)
 return {'triangles':len(triangles),'exactUniqueVertices':len(vertices),'boundaryEdges':int((counts==1).sum()),'nonManifoldEdges':int((counts>2).sum()),'inconsistentTwoFaceWindingEdges':int(((counts==2)&(winding!=0)).sum()),'degenerateTriangles':int(degenerate.sum()),'closedConsistentlyOrientedEdges':bool((counts==2).all() and (winding==0).all() and not degenerate.any()),'signedVolumeM3Diagnostic':volume,'selfIntersectionTested':False,'solidOwnershipProven':False,'qualification':'Exact-coordinate topology only. Signed volume of an open or self-intersecting surface is not a physical volume. No geometry cleanup, coordinate rounding or source edits.'}
def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease)
 old=read(OLD/'result.json');context_result=read(CONTEXT/'result.json')
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for r in [old,context_result]:assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 rows=read(OLD/'selection.json.gz')['rows'];assert {r['uid'] for r in rows}=={'landsd/337075:0','landsd/337079:0'}
 rows.append(next(r for r in read(CONTEXT/'physical-selection.json.gz')['rows'] if r['uid']=='landsd/265848:0'))
 decoder=module('hsbc_assembly_decoder','xl-second-pass.py');decoder.LOCAL=LOCAL
 out=[];refs=[ref(Path(__file__)),ref(OLD/'result.json'),ref(OLD/'selection.json.gz'),ref(OLD/'interfaces.json.gz'),ref(CONTEXT/'result.json'),ref(CONTEXT/'physical-selection.json.gz')]
 for row in rows:
  raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==row['sourceSHA256'];refs.append(ref(ROOT/row['candidate']['path']))
  asset=LOCAL/'assets'/(row['sourceSHA256']+'.glb.gz');asset.parent.mkdir(parents=True,exist_ok=True);asset.write_bytes(raw)
  tri=decoder.glb_triangles(row)
  out.append({'uid':row['uid'],'sourceSHA256':row['sourceSHA256'],'modelId':row['modelId'],'worldBounds':row['native']['model']['worldBounds'],'topology':topology(tri),'geometryPreserved':True})
 save(DOC/'topology.json',{'rows':out,'installationApproved':False,'modelGeometryChanges':0})
 refs.append(ref(DOC/'topology.json'));payload={'uids':[r['uid'] for r in out],'evidenceRefs':refs};stage='exact-original-assembly-solid-topology-diagnostic-v1';jid=jobs.enqueue(BATCH,stage,payload);job=jobs.claim(BATCH,lease['owner'],[stage],lease_seconds=1800);assert job and job['id']==jid
 result={**payload,'jobId':jid,'batch':BATCH,'rows':out,'newlyInstalled':0,'publication':False,'modelGeometryChanges':0,'scriptExternalAICalls':0,'installationApproved':False,'qualification':'Exact original topology evidence before any bounded architectural/solid-overlap interpretation. No physical support exceptions, suppression, geometry changes or acceptance. Old interface failures are retained.'}
 with connect() as c:
  c.row_factory=dict_row;c.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(c,lease)
  for item in refs:assert ref(ROOT/item['path'])==item
  assert c.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jid,job['owner'],job['token'])).rowcount==1
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',result)
 save(DOC/'result.json',result);save(DOC/'neon-sync.json',{'jobId':jid,'resultVerified':True});print(json.dumps({'jobId':jid,'topology':[{'uid':r['uid'],**r['topology']} for r in out],'neonVerified':True}),flush=True)
if __name__=='__main__':
 if '--owned' in sys.argv:owned()
 else:
  assert not DOC.exists() and not LOCAL.exists()
  claim=reservations.claim('codex-hsbc-topology-'+str(uuid.uuid4()),['source-context:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'],claim
  save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)))
  subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
