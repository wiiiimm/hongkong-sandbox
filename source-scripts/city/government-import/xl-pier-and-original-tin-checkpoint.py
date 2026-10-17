"""Fence completed Pier acceptance and distinct original terrain diagnostics; no new credit."""
import json,uuid
from pathlib import Path
from run import ROOT,read,save,digest,reservations,jobs,connect,Jsonb,dict_row
DIR=ROOT/'source-scripts/city/government-import';BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-pier-and-original-tin-checkpoint-20261007'
PHASES=['government-xl-central-pier-current-original-physical-20261007','government-xl-central-pier-retained-original-physical-20261007','government-xl-central-pier-original-current-ground-20261007','government-xl-central-pier-regional-contact-followthrough-20261007','government-xl-central-pier-successor-installed-v2-20261007']
PREVIEWS=['government-xl-raw-original-tin-20-preview-20261007','government-xl-raw-original-tin-13-preview-20261007']
DIAGNOSTICS=['government-xl-cullinan5-upper-layer-surface-20261007','government-xl-ocean-centre-upper-layer-surface-20261007','government-xl-hoi-tai-basic-floor-support-20261007','government-xl-imperial-basic-floor-support-20261007']
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}
def main():
 doc=BASE/BATCH;assert not doc.exists();refs=[];phases=[];uids={'landsd/122298:0'};previews=[];diagnostics=[]
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for n in PHASES:
   p=BASE/n;r=read(p/'result.json');sync=read(p/'neon-sync.json');assert sync['resultVerified'] and sync['jobId']==r['jobId']
   assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
   for e in r['evidenceRefs']:assert ref(ROOT/e['path'])==e
   refs.extend([ref(p/'result.json'),ref(p/'neon-sync.json')]);phases.append({'batch':n,'jobId':r['jobId'],'reasons':r.get('reasons',[]),'scriptChecksPassed':r.get('scriptChecksPassed'),'alreadyInstalled':r.get('installedUids',[])})
 for n in PREVIEWS:
  p=BASE/n/'result.json';r=read(p);assert r['diagnosticOnly'] and not r['publication'] and r['newlyInstalled']==r['modelGeometryChanges']==r['scriptExternalAICalls']==0
  for path,sha in r['inputHashes'].items():assert ref(ROOT/path)['sha256']==sha
  refs.append(ref(p));uids.update(row['uid'] for row in r['rows']);previews.append({'batch':n,'rows':r['rows'],'historicalManifestChanges':r['historicalManifestChanges']})
 for n in DIAGNOSTICS:
  p=DIR/'local'/n/'result.json';r=read(p);assert r['diagnosticOnly'] and not r['publication'] and r['newlyInstalled']==r['modelGeometryChanges']==r['scriptExternalAICalls']==0
  for path,sha in r['inputHashes'].items():assert ref(ROOT/path)['sha256']==sha
  target=doc/(n+'.json');save(target,r);refs.append(ref(target));uids.add(r['uid']);uids.update(row.get('uid') for row in r['rows'] if row.get('uid'));uids.add(r.get('supportUid',r['uid']));diagnostics.append({'batch':n,'uid':r['uid'],'evidence':ref(target)})
 refs.append(ref(Path(__file__)));manifest=ROOT/'3d-viewer/city/data/manifest.json';pointer=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';refs.extend([ref(manifest),ref(pointer)])
 claim=reservations.claim('codex-xl-pier-checkpoint-'+str(uuid.uuid4()),['building:'+u for u in sorted(uids)],batch=BATCH);assert claim['ok'];lease=claim['reservation']
 try:
  installed=read(BASE/PHASES[-1]/'result.json');assert installed['installedUids']==['landsd/122298:0'] and installed['passed'];assert installed['snapshotId']==read(pointer)['snapshotId']
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s',(installed['snapshotId'],'landsd/122298:0')).fetchone()==('installed-verified',installed['sourceSHA256'])
  save(doc/'phases.json',{'phases':phases,'previews':previews,'diagnostics':diagnostics,'publication':False,'newlyInstalled':0});refs.append(ref(doc/'phases.json'))
  stage='completed-pier-and-raw-original-tin-checkpoint-v1';payload={'uids':sorted(uids),'evidenceRefs':refs};jid=jobs.enqueue(BATCH,stage,payload);job=jobs.claim(BATCH,lease['owner'],[stage],lease_seconds=1800);assert job and job['id']==jid
  result={**payload,'jobId':jid,'batch':BATCH,'newlyInstalled':0,'publication':False,'alreadyInstalled':['landsd/122298:0'],'pointwisePositive':[r['uid'] for p in previews for r in p['rows'] if r['pointwisePositive']],'modelGeometryChanges':0,'scriptExternalAICalls':0,'activeWorkers':0,'queuedFollowups':0,'qualification':'Historical completed jobs and new bounded diagnostics only. Original terrain TIN pointwise positives still need fresh full coherent terrain/foundation/neighbour/browser acceptance. No additional installation or review credit.'}
  with connect() as c:
   c.row_factory=dict_row;c.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(c,lease)
   for e in refs:assert ref(ROOT/e['path'])==e
   assert c.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jid,job['owner'],job['token'])).rowcount==1
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',result)
  save(doc/'result.json',result);save(doc/'neon-sync.json',{'jobId':jid,'resultVerified':True});print(json.dumps({'jobId':jid,'positives':result['pointwisePositive'],'newlyInstalled':0}),flush=True)
 finally:reservations.release(lease)
if __name__=='__main__':main()
