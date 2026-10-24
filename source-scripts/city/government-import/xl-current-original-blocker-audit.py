"""Reconcile all current XL failures with exact source-bound completed work.

This creates resumable evidence records, not permanent rejection, review approval,
model changes or a blanket assertion that more AI/compute can resolve a source.
"""
import importlib.util
import json
import uuid
from collections import Counter
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect,jobs,reservations,Jsonb,dict_row,NATIVE_RUN

BATCH='government-xl-current-320-source-blocker-audit-20261009'
BASE=ROOT/'docs/astra-city/government-import'
DOC=BASE/BATCH
COUNT=BASE/'government-xl-central-park-original-podium-installed-20261009/full-xl-current-count.json'
PRIOR=BASE/'government-xl-322-complete-group-source-followups-20261008/result.json'
ORIGINAL=BASE/'government-xl-held-second-pass-dispositions-20261008/dispositions.json.gz'
SCAN=BASE/'government-xl-321-direct-shared-osm-group-scan-20261009'
TEN=BASE/'government-xl-ten-retained-group-followthrough-20261009/result.json'
EXTRA=[
 'government-xl-china-merchants-wrapper-foundation-result-20261009',
 'government-xl-direct-osm-hoi-fu-native-parent-20261009-177604-0',
 'government-xl-direct-osm-manhattan-native-parent-v2-20261009-276331-0',
 'government-xl-direct-osm-group-pending-source-local-20261009-227593-0',
 'government-xl-seven-direct-shared-osm-component-identity-20261009',
 'government-xl-victoria-three-original-checked-20261009',
 'government-xl-victoria-three-original-shared-edges-20261009',
]

def ref(path):return {'path':str(path.relative_to(ROOT)),'sha256':digest(path.read_bytes())}
def canonical(value):return digest(jobs.encode(value).encode())
def main():
 assert not DOC.exists(),'Completed receipts are immutable'
 count=read(COUNT);assert count['counts']=={'installedVerified':201,'remaining':320,'total':521}
 manifest=ROOT/'3d-viewer/city/data/manifest.json';pointer=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json'
 assert digest(manifest.read_bytes())==count['manifestSHA256'] and read(pointer)['snapshotId']==count['snapshotId']
 prior=read(PRIOR);original={r['sourceKey']:r for r in read(ORIGINAL)['rows']}
 previous={r['sourceKey']:r for r in prior['rows']};scan_result=read(SCAN/'result.json')
 scans={r['sourceKey']:r for r in read(SCAN/'outcomes.json.gz')['rows']}
 ten=read(TEN);overrides={r['uid']:r for r in ten['rows']}
 extras=[read(BASE/n/'result.json') for n in EXTRA]
 reports=[prior,scan_result,ten,*extras]
 refs=[ref(p) for p in [Path(__file__),COUNT,PRIOR,ORIGINAL,SCAN/'result.json',SCAN/'outcomes.json.gz',TEN,manifest,pointer]]
 refs += [ref(BASE/n/'result.json') for n in EXTRA]
 remaining=[r for r in count['rows'] if not r['installedVerified']]
 assert len({r['sourceKey'] for r in remaining})==320
 # Exact historical source dispositions are independently checked, not rebound
 # to today's manifest or relabelled as fresh physical evaluations.
 previous_ids=sorted({previous[r['sourceKey']]['previousDispositionJobId'] for r in remaining})
 with connect() as c:
  c.execute('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY')
  for report in reports:
   assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(report['jobId'],)).fetchone()==('complete',report)
  saved={j:r for j,s,r in c.execute('SELECT id,status,result FROM astra_modelling.jobs WHERE id=ANY(%s)',(previous_ids,)) if s=='complete'}
  assert len(saved)==len(previous_ids)
  assert not c.execute("SELECT id FROM astra_modelling.jobs WHERE batch LIKE 'government-xl-%%' AND status IN ('pending','running')").fetchall(),'Active XL work must be consumed first'
  profiles=c.execute("SELECT cache_key,model_id,source_result_sha FROM astra_modelling.native_model_sizes WHERE run_id=%s AND size_group='xl'",(NATIVE_RUN,)).fetchall()
  assert len(profiles)==521
  profile_hash={k+'/'+m:s for k,m,s in profiles}
 spec=importlib.util.spec_from_file_location('blocker_reason_groups',HERE/'xl-disposition-audit.py');helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
 rows=[];frontier=[]
 for inventory in remaining:
  key=inventory['sourceKey'];old=previous[key];initial=original[key];scan=scans[key];uid=old['uid'];sha=old['sourceSHA256']
  assert sha==inventory['indexedSourceSHA256']==scan['sourceSHA256']==initial['sourceSHA256']
  assert profile_hash[key]==initial['nativeResultSHA256']==scan['nativeResultSHA256']
  historical=saved[old['previousDispositionJobId']]
  assert historical['sourceKey']==key and historical['sourceSHA256']==sha and historical['reasons']
  row={**old,'name':initial.get('name'),'historicalReasons':old['reasons'],
       'sourceStatus':'not-installable-with-current-verified-evidence',
       'currentSnapshotId':count['snapshotId'],'currentManifestSHA256':count['manifestSHA256'],
       'historicalFailuresAreFreshPhysicalChecks':False,'inProcess':False,
       'automaticRetryWithoutChangedEvidence':False,'revisitLater':True,
       'permanentRejection':False,'installed':False,'newlyInstalled':0,
       'modelGeometryChanges':0,'publication':False,
       'completedWork':[*old['completedWork'],{'jobId':scan_result['jobId'],
          'phase':'direct-shared-osm-group-scan','state':scan['state'],
          'reasons':scan.get('reasons',[]),'measurements':scan.get('measures') or scan.get('previousMeasurements'),
          'historicalMeasurementReused':bool(scan.get('unchangedMeasurementReused'))}]}
  if uid in overrides:
   latest=overrides[uid];assert latest['sourceSHA256']==sha
   row.update({k:v for k,v in latest.items() if k not in ['completedWork','sourceSHA256','uid']})
   row['completedWork'].append({'jobId':ten['jobId'],'phase':'complete-retained-group-followthrough','reasons':latest['reasons']})
  for report in extras:
   direct=report.get('sourceSHA256s',{}).get(uid)==sha or (report.get('uid')==uid and report.get('sourceSHA256')==sha)
   matching=[r for r in report.get('rows',[]) if r.get('uid')==uid and r.get('sourceSHA256')==sha]
   if not direct and not matching:continue
   detail={'jobId':report['jobId'],'phase':report.get('stage') or report['batch']}
   if direct:
    detail.update(reasons=report.get('reasons',[]),scriptChecksPassed=report.get('scriptChecksPassed'))
    if report.get('scriptChecksPassed') is True:frontier.append({'uid':uid,'jobId':report['jobId'],'reason':'positive physical proof needs publication follow-through'})
    if report.get('reasons') and not any('guard:' in r for r in report['reasons']):
     row['reasons']=report['reasons'];row['physicalJobId']=report['jobId']
     row['nextStep']='Resolve the recorded original-source clearance/foundation/support or neighbouring-building failures using changed authoritative evidence or a demonstrated checker correction; preserve all current buildings and rerun full gates. Repeating identical inputs grants no progress.'
   if matching:
    detail['sourceRows']=matching
    # A failed metadata/identity diagnostic remains supplementary; it never
    # erases earlier actual physical failures or grants metadata restoration.
   row['completedWork'].append(detail)
  assert row['reasons'],'Unexplained sources stay actionable'
  row['reasonGroup']=helper.reason_group(row['reasons'])
  row['blockedBy']='explicit-approval-required-after-automatic-review-rejection' if row['needsHumanDecision'] else 'recorded-source-specific-validation-or-authoritative-evidence'
  row['qualification']='Cannot install the tested original safely under current verified evidence and unchanged limits. This is not corruption, permanent impossibility, an AI modelling requirement, or a new acceptance decision. Historical evidence retains its original manifest/input bindings.'
  rows.append(row)
 assert not frontier,frontier
 report={'rows':rows,'counts':count['counts'],'humanStates':dict(Counter(r['humanStatus'] for r in rows)),
    'reasonGroups':dict(Counter(r['reasonGroup'] for r in rows)),
    'directGroupScanStates':dict(Counter(scans[r['sourceKey']]['state'] for r in rows)),
    'actionablePositivePhysicalChecks':frontier,'activeWorkers':0,'newlyInstalled':0,
    'publication':False,'modelGeometryChanges':0,'permanentRejections':0,
    'nativeRun':NATIVE_RUN,'snapshotId':count['snapshotId'],'manifestSHA256':count['manifestSHA256'],
    'qualification':'320 source-specific current inventory dispositions with independently read-back historical filings and later completed results. No terminal architectural impossibility is asserted; no changed source is silently treated as tested.'}
 save(DOC/'dispositions.json.gz',report)
 refs.append(ref(DOC/'dispositions.json.gz'))
 claim=reservations.claim('codex-xl-current-blockers-'+str(uuid.uuid4()),['xl-current-blocker-audit:'+NATIVE_RUN],batch=BATCH,ttl=1800);assert claim['ok'],claim
 lease=claim['reservation'];job=None
 try:
  payload={'evidenceRefs':refs,'sourceKeys':[r['sourceKey'] for r in rows],'manifestSHA256':count['manifestSHA256']}
  stage='current-xl-source-specific-blocker-audit-v1';jid=jobs.enqueue(BATCH,stage,payload);job=jobs.claim(BATCH,lease['owner'],[stage],lease_seconds=1800);assert job and job['id']==jid
  result={**report,**payload,'jobId':jid,'batch':BATCH,'stage':stage}
  with connect() as c:
   c.row_factory=dict_row;c.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(c,lease)
   for item in refs:assert ref(ROOT/item['path'])==item
   assert c.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jid,job['owner'],job['token'])).rowcount==1
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',result)
  save(DOC/'result.json',result);save(DOC/'neon-sync.json',{'jobId':jid,'resultVerified':True,'sources':320})
  print(json.dumps({k:result[k] for k in ['jobId','counts','humanStates','reasonGroups','directGroupScanStates','actionablePositivePhysicalChecks']}),flush=True)
 except Exception as error:
  if job:jobs.finish(job,error=str(error))
  raise
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
