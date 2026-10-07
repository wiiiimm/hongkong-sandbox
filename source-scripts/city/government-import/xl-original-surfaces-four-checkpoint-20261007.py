"""Fence completed original-terrain attempts and exact component results in Neon."""
import json
import uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations,jobs,connect,Jsonb,dict_row
BATCH='government-xl-original-surfaces-four-checkpoint-20261007'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
BASE=DOC.parent
SCOPE=['landsd/252988:0','landsd/91827:0','landsd/265848:0','landsd/228219:0','landsd/104302:0']
PHASES=[*(f'government-xl-original-dtm-next-four-current-cell-20261007-{n}-0' for n in [252988,91827,265848,228219]),
 *(f'government-xl-original-dtm-next-four-retained-cell-20261007-{n}-0' for n in [252988,265848,228219]),
 'government-xl-original-dtm-combined-complete-20261007-91827-0',
 'government-xl-original-dtm-combined-retained-complete-20261007-252988-0',
 *(f'government-xl-current-retained-basic-parent-20261007-{n}-0' for n in [228219,265848]),
 *(f'government-xl-current-retained-complete-basic-parent-20261007-{n}-0' for n in [228219,265848]),
 'government-xl-original-dtm-diagnosed-facet-20261007-91827-0',
 'government-xl-original-dtm-diagnosed-bounded-facet-20261007-91827-0',
 'government-xl-festival-dtm-basic-parent-20261007',
 'government-xl-festival-exact-original-component-interface-20261007',
 'government-xl-festival-two-originals-full-physical-20261007']

def ref(path):return {'path':str(path.relative_to(ROOT)),'sha256':digest(path.read_bytes())}


def main():
 assert not DOC.exists()
 claim=reservations.claim('codex-original-surfaces-checkpoint-'+str(uuid.uuid4()),['building:'+u for u in SCOPE],batch=BATCH);assert claim['ok'];lease=claim['reservation']
 try:
  completed=[];refs=[]
  for name in PHASES:
   folder=BASE/name;result=read(folder/'result.json');sync=read(folder/'neon-sync.json')
   assert sync['resultVerified'] and sync['jobId']==result['jobId']
   assert not result['publication'] and not result['newlyInstalled']
   assert result['modelGeometryChanges']==result['scriptExternalAICalls']==0
   assert result['activeWorkers']==result['queuedFollowups']==0
   for evidence in result['evidenceRefs']:assert ref(ROOT/evidence['path'])==evidence
   assert not reservations.owns(read(HERE/'local'/name/'reservation.json'))
   completed.append(result);refs.extend([ref(folder/'result.json'),ref(folder/'neon-sync.json')])
  preview=HERE/'local/government-xl-three-original-surfaces-preview-20261007/result.json'
  record=read(preview);assert record['diagnosticOnly'] and not record['publication'] and not record['newlyInstalled']
  assert ref(ROOT/record['inputs']['path'])==record['inputs']
  save(DOC/'three-original-surfaces-preview.json',record)
  save(DOC/'completed-sequence.json',{'rows':[{'batch':r['batch'],'jobId':r['jobId'],'uid':r.get('uid'),'uids':r.get('uids'),
   'sourceSHA256':r.get('sourceSHA256'),'reasons':r.get('reasons'),'scriptChecksPassed':r.get('scriptChecksPassed')} for r in completed],
   'newlyInstalled':0,'modelGeometryChanges':0,'scriptExternalAICalls':0})
  refs.extend([ref(DOC/'three-original-surfaces-preview.json'),ref(DOC/'completed-sequence.json')])
  pointer=read(ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json')
  cohort={r['uid'] for r in read(BASE/'government-xl-remaining-20260923/selection.json.gz')['rows']};assert len(cohort)==352
  with connect() as con:
   con.execute('SET TRANSACTION READ ONLY')
   for result in completed:assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(result['jobId'],)).fetchone()==('complete',result)
   reviews=dict(con.execute('SELECT uid,review_state FROM astra_modelling.model_reviews WHERE snapshot_id=%s',(pointer['snapshotId'],)))
  installed=sum(reviews.get(u)=='installed-verified' for u in cohort);assert installed==87
  assert all(reviews.get(u)!='installed-verified' for u in SCOPE)
  stage='original-surfaces-complete-checkpoint-v1';payload={'evidenceRefs':refs,'runner':ref(Path(__file__)),'reviewSnapshot':pointer['snapshotId']}
  jid=jobs.enqueue(BATCH,stage,payload);job=jobs.claim(BATCH,lease['owner'],[stage],lease_seconds=1800);assert job and job['id']==jid
  result={**payload,'batch':BATCH,'jobId':jid,'phaseCount':len(completed),'phaseJobIds':[r['jobId'] for r in completed],
   'scope':SCOPE,'newlyInstalled':0,'publication':False,'modelGeometryChanges':0,'scriptExternalAICalls':0,
   'XL':{'total':352,'installed':installed,'held':352-installed,'newInstalledFrom44Baseline':installed-44,'remainingTo100New':144-installed},
   'cases':[
    {'uid':'landsd/252988:0','hold':'Seven actual contact samples still fail; original 5m DTM is higher at all seven. Original retained source 118475 remains safe.'},
    {'uid':'landsd/265848:0','hold':'Own original source and retained 229310 pass; two overlapping basic towers regress. Complete parent-footprint terrain fixes towers but breaks source coverage/contact/foundation.'},
    {'uid':'landsd/228219:0','hold':'Own original source and retained 72357 pass; four basic overlapping neighbors remain. Complete parent-footprint terrain fixes neighbors but buries source faces.'},
    {'uid':'landsd/91827:0','hold':'Diagnosed original DTM facets fix full source contact/foundation; parent preservation fixes nine basic neighbors. Remaining original Festival component 104302 is not installed.'},
    {'uid':'landsd/104302:0','hold':'Exact original source recovered locally. Joint positive identity/foundation and all neighbors pass; 619 of 1224 strict support samples unresolved.'}],
   'qualification':'All completed phases were read back from Neon. These diagnostics grant zero installation credit. No architectural AI or original geometry changes. Continue the active 100-new-XL target.'}
  with connect() as con:
   con.row_factory=dict_row;con.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(con,lease)
   assert con.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jid,job['owner'],job['token'])).rowcount==1
  with connect() as con:
   con.execute('SET TRANSACTION READ ONLY');assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',result)
  save(DOC/'result.json',result);save(DOC/'neon-sync.json',{'jobId':jid,'resultVerified':True})
  print(json.dumps({'jobId':jid,'phaseCount':len(completed),'XL':result['XL'],'neonVerified':True}),flush=True)
 finally:reservations.release(lease)

if __name__=='__main__':main()
