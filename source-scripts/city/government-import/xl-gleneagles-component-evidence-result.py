"""Persist actual source capture interpretation and complete failed-point distances."""
import uuid,json
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations,jobs,connect,Jsonb,dict_row
BATCH='government-xl-gleneagles-component-evidence-result-20261008';DOC=ROOT/'docs/astra-city/government-import'/BATCH
CAPTURE=ROOT/'docs/astra-city/government-import/government-xl-gleneagles-original-component-capture-20261008'
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}
def main():
 assert not DOC.exists();prior=read(CAPTURE/'result.json');distances=read(CAPTURE/'interface-distances.json.gz')
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(prior['jobId'],)).fetchone()==('complete',prior)
 for v in prior['evidenceRefs']:assert ref(ROOT/v['path'])==v
 refs=[ref(Path(__file__)),ref(CAPTURE/'result.json'),ref(CAPTURE/'195849-0.png'),ref(CAPTURE/'interface-distances.json.gz')]+[{'path':p,'sha256':h} for p,h in distances['inputHashes'].items()];refs=list({v['path']:v for v in refs}.values())
 rows=[]
 for r in distances['rows']:
  assert r['maximumNearestDistanceM']<.05 and r['distanceBuckets']['within1mm']==0
  rows.append({k:v for k,v in r.items() if k!='samples'})
 interpretation={'reviewer':'Codex','sourceEvidenceInterpretationUsedAI':True,'captureActuallyInspected':True,'observation':'Three original native components form a coherent low podium with two curved upper tower masses. The unresolved red rim samples concentrate along their exterior junctions. Complete triangle distances put all156 samples within4.8cm of an original podium face, but none within1mm; nearest faces include both vertical and nonvertical surfaces. The image and proximity do not prove structural continuity, correct terrain, complete foundations or acceptable source placement.','nextEvidence':'Investigate the distinct original boundary surfaces and structural contact route; do not repeat recovery or vertical-ray checks. Preserve existing strict seam limits and separate podium terrain/neighbour holds.','geometryEdits':0,'installationApproved':False,'permanentRejection':False}
 payload={'rows':rows,'interpretation':interpretation,'captureJobId':prior['jobId'],'evidenceRefs':refs};claim=reservations.claim('codex-gleneagles-evidence-'+str(uuid.uuid4()),['source-context:'+BATCH],batch=BATCH);assert claim['ok'],claim;lease=claim['reservation'];job=None
 try:
  stage='original-component-capture-and-full-face-distance-evidence-v1';jid=jobs.enqueue(BATCH,stage,payload);job=jobs.claim(BATCH,lease['owner'],[stage],lease_seconds=1800);assert job and job['id']==jid
  result={**payload,'batch':BATCH,'jobId':jid,'newlyInstalled':0,'publication':False,'modelGeometryChanges':0,'scriptExternalAICalls':0,'aiGeometryModelling':False,'qualification':'Original source interpretation and numerical proximity are diagnostics, not support acceptance. All156 original failed samples and every incident/nearest triangle remain saved. No tolerance, position, source, runtime or review modifications.'}
  with connect() as c:
   c.row_factory=dict_row;c.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(c,lease)
   for v in refs:assert ref(ROOT/v['path'])==v
   assert c.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jid,job['owner'],job['token'])).rowcount==1
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',result)
  save(DOC/'result.json',result);save(DOC/'neon-sync.json',{'jobId':jid,'resultVerified':True});print(json.dumps({'jobId':jid,'neonVerified':True,'unresolvedSamples':sum(r['unresolvedSamples'] for r in rows)}),flush=True)
 except Exception as e:
  if job:assert jobs.finish(job,error=str(e))
  raise
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
