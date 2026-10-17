"""File per-source current blockers without confusing runtime fit with budget.

No new physical acceptance, review mutations, source changes or permanent rejection.
"""
import json,uuid
from pathlib import Path
from collections import Counter
from run import ROOT,HERE,read,save,digest,connect,reservations,jobs,Jsonb,dict_row,NATIVE_RUN
from source_blocker_reason_families import reason_families

BATCH='government-xl-current-320-blocker-families-20261009'
BASE=ROOT/'docs/astra-city/government-import'
DOC=BASE/BATCH
PRIOR=BASE/'government-xl-current-320-source-blocker-audit-20261009/result.json'

def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}
def canonical(value):return digest(jobs.encode(value).encode())
def main():
 assert not DOC.exists(),'Immutable phase: use a fresh stage for changed inputs'
 previous=read(PRIOR);assert previous['counts']=={'installedVerified':201,'remaining':320,'total':521}
 manifest=ROOT/'3d-viewer/city/data/manifest.json'
 assert digest(manifest.read_bytes())==previous['manifestSHA256']
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(previous['jobId'],)).fetchone()==('complete',previous)
 refs=[ref(p) for p in [PRIOR,Path(__file__),HERE/'source_blocker_reason_families.py',HERE/'test-source-blocker-reason-families.py',manifest]]
 rows=[]
 for old in previous['rows']:
  assert old['reasons'] and old['sourceSHA256'] and not old['installed'] and not old['inProcess']
  row={**old,'legacyReasonGroup':old['reasonGroup'],'reasonFamilies':reason_families(old['reasons']),
       'priorAuditJobId':previous['jobId'],'needsAIProcessing':old['needsAIProcessing'],
       'needsComputeProcessing':old['needsComputeProcessing']}
  row['reasonGroup']=row['reasonFamilies'][0] if len(row['reasonFamilies'])==1 else 'multiple-recorded-validation-failures'
  payload={'sourceKey':row['sourceKey'],'uid':row['uid'],'sourceSHA256':row['sourceSHA256'],
      'decisionSHA256':canonical(row),'evidenceRefs':refs}
  stage='current-original-source-validation-blocker-v1';jid=canonical([BATCH,stage,payload])
  row.update(jobId=jid,batch=BATCH,stage=stage)
  rows.append((payload,row))
 assert len(rows)==len({r['sourceKey'] for _,r in rows})==320
 claim=reservations.claim('codex-xl-blocker-dispositions-'+str(uuid.uuid4()),['xl-blocker-dispositions:'+NATIVE_RUN],batch=BATCH,ttl=1800);assert claim['ok'],claim;lease=claim['reservation']
 try:
  with connect() as c:
   c.row_factory=dict_row;c.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(c,lease)
   for item in refs:assert ref(ROOT/item['path'])==item
   for payload,row in rows:
    c.execute("INSERT INTO astra_modelling.jobs(id,batch,stage,payload,status,result) VALUES(%s,%s,%s,%s,'complete',%s)",(row['jobId'],BATCH,row['stage'],Jsonb(payload),Jsonb(row)))
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY')
   found=c.execute('SELECT id,status,result FROM astra_modelling.jobs WHERE id=ANY(%s)',([r['jobId'] for _,r in rows],)).fetchall()
   assert {j:canonical(r) for j,s,r in found if s=='complete'}=={r['jobId']:canonical(r) for _,r in rows}
  families=Counter(f for _,r in rows for f in r['reasonFamilies'])
  result={'rows':[r for _,r in rows],'counts':previous['counts'],'sourceDispositionsVerified':320,
    'reasonFamilies':dict(families),'familyCountsOverlap':True,
    'humanStates':dict(Counter(r['humanStatus'] for _,r in rows)),
    'snapshotId':previous['snapshotId'],'manifestSHA256':previous['manifestSHA256'],
    'physicalPositivesAwaitingPublication':0,'activeWorkers':0,'newlyInstalled':0,
    'publication':False,'modelGeometryChanges':0,'aiGeometryModelling':False,
    'permanentRejections':0,'evidenceRefs':refs,
    'qualification':'Individually queryable source-specific blockers with fresh Neon readback. Runtime footprint-fit is an identity failure, not a resource budget. Overlapping reason families expose all failed contracts. No source/review/physical evidence is changed; no AI or compute necessity is inferred.'}
  save(DOC/'dispositions.json.gz',result)
  payload={'report':ref(DOC/'dispositions.json.gz'),'evidenceRefs':refs};stage='all-current-original-source-blocker-families-v1';jid=canonical([BATCH,stage,payload])
  summary={k:v for k,v in result.items() if k!='rows'};summary.update(jobId=jid,batch=BATCH,stage=stage,report=payload['report'])
  with connect() as c:
   c.row_factory=dict_row;c.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(c,lease)
   for item in refs:assert ref(ROOT/item['path'])==item
   assert ref(DOC/'dispositions.json.gz')==payload['report']
   c.execute("INSERT INTO astra_modelling.jobs(id,batch,stage,payload,status,result) VALUES(%s,%s,%s,%s,'complete',%s)",(jid,BATCH,stage,Jsonb(payload),Jsonb(summary)))
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',summary)
  save(DOC/'result.json',summary);save(DOC/'neon-sync.json',{'jobId':jid,'resultVerified':True,'sourceDispositionsVerified':320})
  print(json.dumps({'jobId':jid,'reasonFamilies':dict(families),'humanStates':summary['humanStates'],'sourceDispositionsVerified':320}),flush=True)
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
