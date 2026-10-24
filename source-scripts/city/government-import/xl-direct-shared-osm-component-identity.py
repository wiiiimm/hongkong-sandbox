"""Fresh identity diagnostics for seven direct shared-OSM originals; no metadata restoration or installation."""
import importlib.util,json,traceback,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations,connect,jobs,Jsonb,dict_row
from direct_shared_osm_geographic_identity import verify_files,UIDS,POLICY
BASE=ROOT/'docs/astra-city/government-import';SOURCE=BASE/'government-xl-direct-shared-osm-official-context-20261009'
BATCH='government-xl-seven-direct-shared-osm-component-identity-20261009';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}
def main():
 assert not DOC.exists();prior=read(SOURCE/'result.json')
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(prior['jobId'],)).fetchone()==('complete',prior)
 for v in prior['evidenceRefs']:assert ref(ROOT/v['path'])==v
 spec=importlib.util.spec_from_file_location('retained_identity_context',HERE/'xl-final-script-pass.py');final=importlib.util.module_from_spec(spec);spec.loader.exec_module(final)
 manifest=ROOT/'3d-viewer/city/data/manifest.json';manifestSHA=digest(manifest.read_bytes());results=[];refs=[ref(Path(__file__)),ref(HERE/'direct_shared_osm_geographic_identity.py'),ref(manifest),ref(SOURCE/'result.json'),ref(SOURCE/'physical-selection.json.gz'),ref(SOURCE/'context.json.gz'),ref(SOURCE/'official-context.json')]
 sources=[r for r in read(SOURCE/'physical-selection.json.gz')['rows'] if r['uid'] in UIDS];assert len(sources)==7
 for row in sources:
  uid=row['uid'];lo,hi=row['native']['model']['worldBounds'];forms=final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]);context={'uid':uid,'sourceSHA256':row['sourceSHA256'],'neighbourTileHashes':{url:digest((ROOT/'3d-viewer'/url).read_bytes()) for _,_,url in forms}}
  try:
   proof=verify_files(row,context,LOCAL/uid.replace('/','-').replace(':','-'));save(DOC/(uid.split('/')[1].replace(':','-')+'.json'),proof)
   result={'uid':uid,'sourceSHA256':row['sourceSHA256'],'passed':proof['passed'],'reasons':proof['reasons'],'completeGroupMeasures':proof['completeGroupMeasures'],'retainedGroupUids':[b['uid'] for b in proof['completeGroupForms'] if b['uid']!=uid],'suppressesBuildingUids':[],'installationApproved':False}
  except Exception as e:
   result={'uid':uid,'sourceSHA256':row['sourceSHA256'],'passed':False,'exception':str(e),'traceback':traceback.format_exc(),'installationApproved':False};save(DOC/(uid.split('/')[1].replace(':','-')+'-error.json'),result)
  results.append(result);print(json.dumps(result),flush=True);refs.append(ref(ROOT/row['candidate']['path']));refs += [ref(ROOT/'3d-viewer'/url) for _,_,url in forms]
 assert digest(manifest.read_bytes())==manifestSHA
 for p in DOC.iterdir():refs.append(ref(p))
 refs=list({r['path']:r for r in refs}.values());claim=reservations.claim('codex-retained-context-'+str(uuid.uuid4()),['source-context:'+BATCH],batch=BATCH);assert claim['ok'],claim;lease=claim['reservation'];job=None
 try:
  payload={'uids':sorted(UIDS),'manifestSHA256':manifestSHA,'evidenceRefs':refs};stage='direct-shared-osm-complete-geographic-identity-diagnostic-v1';jid=jobs.enqueue(BATCH,stage,payload);job=jobs.claim(BATCH,lease['owner'],[stage],lease_seconds=1800);assert job and job['id']==jid
  result={**payload,'jobId':jid,'batch':BATCH,'rows':results,'identityPassed':sum(r['passed'] for r in results),'newlyInstalled':0,'publication':False,'modelGeometryChanges':0,'metadataRestorations':0,'scriptExternalAICalls':0,'sourceEvidenceInterpretationUsedAI':True,'aiGeometryModelling':False,'qualification':'Original exported top/oblique captures inspected: all seven sources contain low podiums, not complete high towers. Preserve every other component. Direct shared OSM references are measured without changing parent IDs; not transitive relation groups. Existing unique official/viewer matches and complete prepared height metadata required unchanged. All other group components retained; no suppression or physical/runtime acceptance. Siu Ho Wan and all empty-match metadata-restoration cases excluded, no missing-match restoration or component suppression is permitted.'}
  with connect() as c:
   c.row_factory=dict_row;c.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(c,lease)
   for v in refs:assert ref(ROOT/v['path'])==v
   assert c.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jid,job['owner'],job['token'])).rowcount==1
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',result)
  save(DOC/'result.json',result);save(DOC/'neon-sync.json',{'jobId':jid,'resultVerified':True});print(json.dumps({'jobId':jid,'neonVerified':True,'identityPassed':result['identityPassed'],'newlyInstalled':0}),flush=True)
 except Exception as e:
  if job:assert jobs.finish(job,error=str(e))
  raise
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
