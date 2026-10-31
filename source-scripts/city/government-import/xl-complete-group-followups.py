"""Persist the complete XL group scan and new per-source evidence in Neon.

No installations, model-review approvals, permanent rejections or blanket retries.
"""
import json,uuid
from pathlib import Path
from collections import Counter
from run import ROOT,HERE,read,save,digest,reservations,connect,jobs,Jsonb,dict_row
BATCH='government-xl-322-complete-group-source-followups-20261008'
BASE=ROOT/'docs/astra-city/government-import'
DOC=BASE/BATCH
SCAN=BASE/'government-xl-322-complete-footprint-group-scan-v2-20261008'
COUNT=BASE/'government-xl-complete-market-installed-20261008/full-xl-current-count.json'
PRIOR=BASE/'government-xl-held-second-pass-dispositions-20261008/dispositions.json.gz'
ROOF=BASE/'government-xl-22-component-roof-coverage-20261008'
RECOVERY=BASE/'government-xl-two-lantau-complete-footprint-group-scan-20261008'
PIER=BASE/'government-xl-central-pier-eight-member-recovered-20261008'
APEX=BASE/'government-xl-apex-complete-original-tin-diagnostic-20261008'
SIU=BASE/'government-xl-siu-ho-wan-complete-source-local-20261008'
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}
def main():
 assert not DOC.exists()
 folders=[SCAN,ROOF,RECOVERY,PIER,APEX,SIU];reports={}
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in folders:
   r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
   assert not r['publication'] and r['newlyInstalled']==0
   for item in r['evidenceRefs']:assert ref(ROOT/item['path'])==item
   reports[folder.name]=r
 count=read(COUNT);assert count['counts']=={'total':521,'installedVerified':199,'remaining':322}
 assert digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())==count['manifestSHA256']
 original={r['sourceKey']:r for r in read(PRIOR)['rows']};scan={r['sourceKey']:r for r in read(SCAN/'outcomes.json.gz')['rows']}
 assert len(scan)==322
 roofs={r['uid']:r for r in read(ROOF/'measurements.json.gz')['rows']}
 recovered={r['uid']:r for r in read(RECOVERY/'outcomes.json.gz')['rows']}
 rows=[]
 for inventory in count['rows']:
  if inventory['installedVerified']:continue
  key=inventory['sourceKey'];old=original[key];diagnostic=scan[key];uid=old['uid'];sha=old['sourceSHA256']
  assert sha==inventory['indexedSourceSHA256']==diagnostic['sourceSHA256']
  reasons=list(old['reasons']);work=[{'jobId':reports[SCAN.name]['jobId'],'result':diagnostic['state'],'reasons':diagnostic.get('reasons',[])}]
  next_step=old['nextStep'];human=False
  if uid in roofs:
   upper=roofs[uid];assert upper['sourceSHA256']==sha
   work.append({'jobId':reports[ROOF.name]['jobId'],'componentAssessments':[{k:c[k] for k in ['uid','assessment']} for c in upper['components']]})
   next_step='Retain current upper/unknown-height components. Establish complete original component ownership and support, then rerun source-specific physical/runtime/browser gates. Projection or height-plane coverage grants no suppression.'
  if uid in recovered:
   r=recovered[uid];assert r['sourceSHA256']==sha
   work.append({'jobId':reports[RECOVERY.name]['jobId'],'result':r['state'],'reasons':r.get('reasons',[])})
  elif diagnostic['state']=='source-cache-missing':
   if uid=='landsd/213352:0':
    assert reports[PIER.name]['errors'][uid]=='source-model-missing-in-current-revision'
    reasons.append('pinned-government-source-member-absent-from-current-archive')
    work.append({'jobId':reports[PIER.name]['jobId'],'result':'source-model-missing-in-current-revision'})
    next_step='Restore the exact archived pinned source bytes or establish an independently verified government successor; retain the current model and all historical checks.'
   elif uid is None:
    reasons.append('no-exact-current-official-or-viewer-georef-route')
    next_step='New authoritative GeoRef/component identity is required; do not repeat the completed zero-result exact official/viewer lookup or invent a route.'
  if uid=='landsd/227942:0':
   r=reports[APEX.name];assert r['sourceSHA256']==sha and not r['strictRimContactObserved']
   reasons.append('unchanged-original-tin-strict-rim-gap-over-0.1m')
   work.append({'jobId':r['jobId'],'minLowGapM':r['clearance']['minLowGap'],'strictContactObserved':False})
   next_step='Changed authoritative source/contact evidence or a demonstrated validation correction; original TIN and existing nested terrain both retain the 0.111m strict rim gap. Do not repeat unchanged terrain or waive the 0.1m limit.'
  if uid=='landsd/120104:0':
   r=reports[SIU.name];assert r['sourceSHA256s'][uid]==sha and not r['scriptChecksPassed']
   reasons.append('runtime-source-metadata-omitted-from-prepared-entry')
   reasons.append('metadata-restoration-pending-explicit-approval-after-auto-review-rejection')
   work.append({'jobId':r['jobId'],'result':'complete-group-identity-passes-runtime-source-record-mismatch','foundationTested':False})
   human=True
   next_step='Explicit approval pending for restoring omitted metadata from the single exact government record. Automatic review rejected that restoration because cached matches are empty and centroid differs by 52m. No bypass or installation; if approved, rerun every physical/runtime gate.'
  row={'uid':uid,'sourceKey':key,'sourceSHA256':sha,'modelId':old['modelId'],'previousDispositionJobId':old['jobId'],
       'previousReasons':old['reasons'],'reasons':sorted(set(reasons)),'completedWork':work,'nextStep':next_step,
       'humanStatus':'held-human-decision' if human else 'held-unknown','needsHumanDecision':human,'needsAIProcessing':None,'needsComputeProcessing':None,
       'retainCurrentModel':True,'revisitLater':True,'permanentRejection':False,'installed':False,'newlyInstalled':0}
  rows.append(row)
 assert len(rows)==322 and sum(r['needsHumanDecision'] for r in rows)==1
 save(DOC/'dispositions.json.gz',{'rows':rows,'counts':dict(Counter(r['humanStatus'] for r in rows)),'qualification':'Latest supplementary evidence only; older technical failures remain. No diagnostics earn installation credit.'})
 refs=[ref(p) for p in [Path(__file__),COUNT,PRIOR,DOC/'dispositions.json.gz']]+[ref(f/'result.json') for f in folders]
 claim=reservations.claim('codex-xl-group-followups-'+str(uuid.uuid4()),['source-followups:'+BATCH],batch=BATCH,ttl=1800);assert claim['ok'],claim
 lease=claim['reservation'];job=None
 try:
  payload={'evidenceRefs':refs,'sourceKeys':[r['sourceKey'] for r in rows]};stage='xl-complete-group-source-specific-followups-v1';jid=jobs.enqueue(BATCH,stage,payload);job=jobs.claim(BATCH,lease['owner'],[stage],lease_seconds=1800);assert job and job['id']==jid
  result={**payload,'jobId':jid,'batch':BATCH,'rows':rows,'counts':count['counts'],'newlyInstalled':0,'publication':False,'modelGeometryChanges':0,'scriptExternalAICalls':0,'permanentRejections':0,'activeWorkers':0,'qualification':'322 source-bound resumable followups with prior reasons and verified new group/upper-coverage/recovery/contact evidence. Siu Ho Wan metadata restoration is pending explicit approval after automatic review rejection; it is not installation approval. All other unresolved cases retain unknown processing requirements, without inferring AI necessity.'}
  with connect() as c:
   c.row_factory=dict_row;c.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(c,lease)
   for item in refs:assert ref(ROOT/item['path'])==item
   assert c.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jid,job['owner'],job['token'])).rowcount==1
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',result)
  save(DOC/'result.json',result);save(DOC/'neon-sync.json',{'jobId':jid,'resultVerified':True});print(json.dumps({'jobId':jid,'sources':len(rows),'neonVerified':True}),flush=True)
 except Exception as e:
  if job:assert jobs.finish(job,error=str(e))
  raise
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
