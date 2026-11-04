"""Fence complete common terrain attempts and the already credited installations."""
import uuid
from pathlib import Path
from run import ROOT,read,save,digest,reservations,jobs,connect,Jsonb,dict_row
DIR=ROOT/'source-scripts/city/government-import';BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-completed-common-terrain-checkpoint-20261007'
SEQUENCES=['government-xl-two-common-tin-followthrough-20261007','government-xl-two-ground-tin-followthrough-20261007','government-xl-two-additional-common-tin-followthrough-20261007','government-xl-science-common-original-followthrough-20261007','government-xl-orchards-complete-contact-followthrough-20261007']
WEST=['government-xl-west-kowloon-bus-common-original-20261007','government-xl-west-kowloon-bus-common-preserved-20261007','government-xl-west-kowloon-bus-common-runtime-floor-20261007']
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}
def main():
 doc=BASE/BATCH;assert not doc.exists();phases=[];uids=set();refs=[ref(Path(__file__))];latest={};sequence=[]
 for name in SEQUENCES:
  p=BASE/name/'commands.json';d=read(p);assert d['activeWorkers']==d['queuedFollowups']==d['scriptExternalAICalls']==d['modelGeometryChanges']==0;refs.append(ref(p));sequence.append(d)
  for row in d['rows']:
   uids.add(row['uid']);latest[row['uid']]={'uid':row['uid'],'name':row['name'],'installed':row['installed'],'reasons':row['steps'][-1]['result'].get('reasons',[]) if row['steps'][-1]['result'] else ['source-identity-unrelated-overlap-see-fenced-construction-failure']}
   for step in row['steps']:
    if step['result']:phases.append(BASE/step['batch'])
    else:
     failed=BASE/(step['batch']+'-prepared')/'construction-failure.json';assert failed.exists();refs.append(ref(failed))
 phases.extend(BASE/name for name in WEST)
 with connect() as con:
  con.execute('SET TRANSACTION READ ONLY')
  for p in phases:
   r=read(p/'result.json');sync=read(p/'neon-sync.json');assert sync['resultVerified'] and sync['jobId']==r['jobId']
   assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
   for e in r['evidenceRefs']:assert ref(ROOT/e['path'])==e
   refs.extend([ref(p/'result.json'),ref(p/'neon-sync.json')])
 west=read(BASE/WEST[-1]/'result.json');uid=west['uid'];uids.add(uid);latest[uid]={'uid':uid,'name':'West Kowloon Station Bus Terminus','installed':False,'reasons':west['reasons']}
 pointer=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';snapshot=read(pointer)['snapshotId'];manifest=ROOT/'3d-viewer/city/data/manifest.json';refs.extend([ref(pointer),ref(manifest)])
 xl={r['uid'] for r in read(BASE/'government-xl-remaining-20260923/selection.json.gz')['rows']};assert len(xl)==352
 deployed={m['uid']:m for u in read(manifest)['officialModelCatalogues'] for m in read(ROOT/'3d-viewer'/u)['models'] if m['uid'] in xl}
 with connect() as con:
  con.execute('SET TRANSACTION READ ONLY');verified=con.execute('SELECT uid,review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=ANY(%s)',(snapshot,list(deployed))).fetchall()
 assert {u for u,state,sha in verified if state=='installed-verified' and deployed[u]['sha256']==sha}==set(deployed)
 assert len(deployed)==91
 for uid,r in latest.items():assert r['installed']==(uid in deployed)
 save(doc/'phases.json',{'phases':[str(p.relative_to(ROOT)) for p in phases],'latest':list(latest.values()),'publication':False,'newlyInstalled':0});refs.append(ref(doc/'phases.json'))
 claim=reservations.claim('codex-complete-common-terrain-'+str(uuid.uuid4()),['building:'+u for u in sorted(uids)],batch=BATCH);assert claim['ok'];lease=claim['reservation']
 try:
  payload={'uids':sorted(uids),'evidenceRefs':refs};stage='completed-common-original-terrain-checkpoint-v1';jid=jobs.enqueue(BATCH,stage,payload);job=jobs.claim(BATCH,lease['owner'],[stage],lease_seconds=1800);assert job and job['id']==jid
  result={**payload,'jobId':jid,'batch':BATCH,'rows':list(latest.values()),'xlInstalled':91,'xlNotInstalled':261,'newXLFromBaseline':47,'furtherInstallationsRequired':53,'newlyInstalled':0,'publication':False,'modelGeometryChanges':0,'scriptExternalAICalls':0,'activeWorkers':0,'qualification':'Completed physical/identity failures and already credited installs. Goal remains active. Current original sources/limits unchanged; no checkpoint installation credit.'}
  with connect() as con:
   con.row_factory=dict_row;con.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(con,lease)
   for e in refs:assert ref(ROOT/e['path'])==e
   assert con.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jid,job['owner'],job['token'])).rowcount==1
  with connect() as con:
   con.execute('SET TRANSACTION READ ONLY');assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',result)
  save(doc/'result.json',result);save(doc/'neon-sync.json',{'jobId':jid,'resultVerified':True});print({'jobId':jid,'phases':len(phases),'installed':91,'held':261},flush=True)
 finally:reservations.release(lease)
if __name__=='__main__':main()
