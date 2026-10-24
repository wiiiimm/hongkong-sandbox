"""Record bounded official 3DSD metadata findings; no source substitution."""
import json,struct,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations,connect,jobs,Jsonb,dict_row
BATCH='government-xl-structured-source-research-20261008';DOC=ROOT/'docs/astra-city/government-import'/BATCH
ORIGINALS={'3332115002':('landsd/227942:0','B333211500201063C0','83cc3270d1de801eace0d72a63dfc470df8e2862b8d6399f0422e0a4ceb8ed0c',13370),'3460819976':('landsd/265848:0','B346081997602063C0','848eb61d88b19162d2166127f3c04c4f920f986c55106ffbb121b110ef0973cd',15336),'3462420011':('landsd/337075:0','B346242001101063C0','041565a12440846dd7e5d9a1e31263177c5b07c29f288d8bc3b0d17fb89e1537',8396)}
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}
def main():
 assert not (DOC/'result.json').exists()
 metadata=read(DOC/'metadata.json');files={f['path']:f for f in metadata['files']};rows=[]
 refs=[ref(p) for p in [Path(__file__),HERE/'xl-structured-government-source-research.py',DOC/'metadata.json',DOC/'building-tileset.json',DOC/'provenance.json']]
 for f in metadata['files']:
  p=ROOT/f['cache'];assert ref(p)['sha256']==f['sha256'];refs.append(ref(p))
 for leaf in metadata['leaves']:
  names=leaf['batchTable']['extensions']['3DTILES_batch_table_hierarchy']['classes'][0]['instances']['names'];names=sorted(set(n for n in names if n!='RootNode'));assert len(names)==1
  variant=names[0];source=ORIGINALS.get(variant[1:11]);assert source
  data=(ROOT/files[leaf['path']]['cache']).read_bytes();_,version,n,fj,fb,bj,bb=struct.unpack_from('<4s6I',data);assert version==1 and n==len(data)
  start=28+fj+fb+bj+bb;length,kind=struct.unpack_from('<II',data,start+12);assert kind==0x4e4f534a
  gltf=json.loads(data[start+20:start+20+length]);triangles=0
  for mesh in gltf['meshes']:
   for p in mesh['primitives']:
    assert p.get('mode',4)==4;count=gltf['accessors'][p['indices']]['count'];assert count%3==0;triangles+=count//3
  uid,model,sha,original_triangles=source
  rows.append({'uid':uid,'sourceSHA256':sha,'pinnedDetailedModelId':model,'pinnedDetailedTriangles':original_triangles,'structuredModelId':variant,'structuredTriangles':triangles,'structuredTileSHA256':files[leaf['path']]['sha256'],'tilePath':leaf['path'],'sameGeoRefPrefix':variant[1:11]==model[1:11],'sameModelVariant':variant==model,'sceneHierarchyScope':'one identified model plus RootNode; no neighbouring component ownership established','identityAccepted':False,'installationApproved':False,'humanStatus':'held-unknown','retainCurrentModel':True,'permanentRejection':False,'nextStep':'Retain detailed original and existing contact/component failures. This different government variant is not an identity/pose/support substitute; authoritative cross-component and vertical-datum evidence is still required.'})
 assert len(rows)==3 and all(not r['sameModelVariant'] for r in rows)
 save(DOC/'findings.json',{'rows':rows,'boundedCompletedProbe':{'files':len(metadata['files']),'bytes':metadata['totalBytes']},'initialProbe':'Stopped at 60 requests before producing a report; 6262656 bytes retained in local cache. Narrower completed traversal uses only terminal B3DM payloads.','publication':False,'newlyInstalled':0,'modelGeometryChanges':0});refs.append(ref(DOC/'findings.json'))
 claim=reservations.claim('codex-structured-source-'+str(uuid.uuid4()),['source-context:'+BATCH],batch=BATCH);assert claim['ok'],claim;lease=claim['reservation'];job=None
 try:
  payload={'uids':[r['uid'] for r in rows],'evidenceRefs':refs};stage='bounded-official-structured-source-metadata-v1';jid=jobs.enqueue(BATCH,stage,payload);job=jobs.claim(BATCH,lease['owner'],[stage],lease_seconds=1800);assert job and job['id']==jid
  result={**payload,'jobId':jid,'batch':BATCH,'rows':rows,'newlyInstalled':0,'publication':False,'modelGeometryChanges':0,'scriptExternalAICalls':0,'sourceEvidenceInterpretationUsedAI':True,'aiGeometryModelling':False,'qualification':'Different structured government model variants supply per-model identifiers, not a proven assembly ownership graph. Original sources, poses, limits and acceptance are unchanged. Simplified shape/datum equivalence has not been established.'}
  with connect() as c:
   c.row_factory=dict_row;c.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(c,lease)
   for item in refs:assert ref(ROOT/item['path'])==item
   assert c.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jid,job['owner'],job['token'])).rowcount==1
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',result)
  save(DOC/'result.json',result);save(DOC/'neon-sync.json',{'jobId':jid,'resultVerified':True});print(json.dumps({'jobId':jid,'rows':len(rows),'neonVerified':True}),flush=True)
 except Exception as e:
  if job:assert jobs.finish(job,error=str(e))
  raise
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
