"""DRAFT serialization-only completed evidence recovery; never rerun geometry."""
from pathlib import Path
import importlib.util,json,subprocess,sys,uuid
from run import ROOT,HERE,read,save,digest,connect,reservations
B=ROOT/'docs/astra-city/government-import';OLD=B/'government-xl-upton-podium12728-12662-complete-original-foreign-conflict-attribution-v1-20261011';BATCH='government-xl-upton-podium12728-12662-frozen-json-key-readback-recovery-v1-20261011';DOC=B/BATCH;LOCAL=HERE/'local'/BATCH;JID='faaad91cebbb0d67b52b7e4c9c9ba7f00089673c7a4f11d91a65cfaf164fc5bb';UIDS=['landsd/12728:0','landsd/12662:0','landsd/338946:0'];MANIFEST_SHA='947f0a3b3a1d7167a9f98074af35d4030ff0245e121ee682eed4f9ab9baedfa6'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def state():
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');return c.execute('SELECT row_to_json(t) FROM astra_modelling.model_reviews t WHERE uid=ANY(%s) ORDER BY uid,snapshot_id',(UIDS,)).fetchall()
def main():
 if '--owned'not in sys.argv:
  assert not DOC.exists()and not LOCAL.exists();claim=reservations.claim('upton-json-evidence-recovery-'+str(uuid.uuid4()),['building:'+u for u in UIDS],batch=BATCH,ttl=1800);assert claim['ok'],claim;save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)))
  code=subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--ttl','1800','--',sys.executable,__file__,'--owned'],cwd=ROOT).returncode;assert code==0,code;return
 assert not DOC.exists();lease=read(LOCAL/'reservation.json');assert reservations.owns(lease);before=state();manifest=ROOT/'3d-viewer/city/data/manifest.json';assert ref(manifest)['sha256']==MANIFEST_SHA;diag=read(OLD/'diagnostic.json.gz');raw=read(OLD/'raw-complete-neon-readback-after-freezer-assertion.json');assert raw['jobId']==JID and raw['status']=='complete'
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');row=c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(JID,)).fetchone()
 assert row==('complete',raw['result']);old=row[1];assert old['summary']==diag['summary'] and old['summary']['dimensions']=={'1':23}
 # Reconstruct the sole pre-serialization mismatch. No contact math is performed.
 before_json=dict(old);before_json['summary']=dict(old['summary']);before_json['summary']['dimensions']={int(k):v for k,v in old['summary']['dimensions'].items()};assert before_json!=old and json.loads(json.dumps(before_json))==old
 assert len(old['evidenceRefs'])==18
 for e in old['evidenceRefs']:assert ref(ROOT/e['path'])==e
 assert json.loads(json.dumps(before,default=str))==diag['protectedReviewRowsBeforeAfter'];current=B/'government-xl-upton338946-podium12728-current-unchanged-owned-identity-v1-20261011/result.json';r=read(current)
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for e in r['evidenceRefs']:assert ref(ROOT/e['path'])==e
 save(DOC/'original-completed-neon-result.json',old)
 validation=dict(originalJobId=JID,originalNeonStatus='complete',exactOriginalCompletedResultEqual=True,all18OriginalRefsMatch=True,originalFreezerAssertionFailurePreserved=True,soleMismatch='Counter integer dimension key1 round-trips as JSON object string key1',reconstructedPythonPreJSONDiffers=True,jsonRoundTripExactlyEqualsOriginalDB=True,numericReplay=False,geometryChanges=0,oldProducerOrJobOrResultsChanged=False,allPriorIdentityAndProperCrossingFailuresPreserved=True)
 save(DOC/'serialization-validation.json',validation);spec=importlib.util.spec_from_file_location('reviewed_source_freezer',HERE/'parkview_block17_freeze_current_source_evidence_20261011.py');f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f);paths={Path(__file__),OLD/'diagnostic.json.gz',OLD/'raw-complete-neon-readback-after-freezer-assertion.json',current,manifest};f.local_imports(Path(__file__),paths);paths.update(ROOT/e['path']for e in old['evidenceRefs'])
 report=dict(uids=UIDS,sourceOnly=True,originalCompletedJobId=JID,serializationRecoveryOnly=True,numericalReplay=False,identityAccepted=False,physicalAccepted=False,manifestSHA256=MANIFEST_SHA,summary=diag['summary'],protectedReviewWrites=0,qualification='Exact completed DB result and original source diagnostic readback finalized after sole Python integer-key versus JSONB string-key assertion mismatch. Historical execution failure and original job remain unchanged; no geometry or contact rerun, ownership/identity/solid/support/current credit. All23 proper surface crossings and podium identity negatives stay open.')
 result=f.F.freeze(BATCH,'json-key-normalized-original-completed-readback-no-numeric-replay',sorted(paths),report)
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(result['jobId'],)).fetchone()==('complete',result);assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(JID,)).fetchone()==row
 for e in result['evidenceRefs']:assert ref(ROOT/e['path'])==e
 assert state()==before and reservations.owns(lease)and ref(manifest)['sha256']==MANIFEST_SHA;print(json.dumps(dict(jobId=result['jobId'],originalJobId=JID,allRefs=len(result['evidenceRefs']),numericReplay=False,summary=diag['summary'])),flush=True)
if __name__=='__main__':main()
