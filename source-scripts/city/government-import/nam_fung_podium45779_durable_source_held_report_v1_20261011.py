"""Exact UID/source-revision held report; no review-table or pointer writes."""
from pathlib import Path
import importlib.util,json,subprocess,sys,uuid
from run import ROOT,HERE,read,save,digest,connect,reservations
B=ROOT/'docs/astra-city/government-import';BATCH='government-xl-nam-fung-podium45779-durable-source-held-report-v1-20261011';DOC=B/BATCH;LOCAL=HERE/'local'/BATCH
UID='landsd/45779:0';PAIR=[UID,'landsd/79099:0'];SHA='28e868670016b935355c29b991ac1d7fc3703f1579d98b3ce79403b605716de5';HELD=B/'government-xl-nam-fung79099-podium45779-scoped-source-hold-v1-20261011'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def state():
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');return c.execute('SELECT row_to_json(t) FROM astra_modelling.model_reviews t WHERE uid=ANY(%s) ORDER BY uid,snapshot_id',(PAIR,)).fetchall()
def main():
 if '--owned'not in sys.argv:
  assert not DOC.exists()and not LOCAL.exists();claim=reservations.claim('nam-fung-held-report-'+str(uuid.uuid4()),['building:'+u for u in PAIR],batch=BATCH,ttl=1800);assert claim['ok'],claim;save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)))
  code=subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--ttl','1800','--',sys.executable,__file__,'--owned'],cwd=ROOT).returncode;assert code==0,code;return
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease)and not DOC.exists();before=state();note=read(HELD/'held.json');assert note['podiumCurrentIdentityPassed']is False and note['sourceGeometryChanges']==0
 for e in note['evidenceRefs']:assert ref(ROOT/e['path'])==e
 receipt_paths=[ROOT/e['path']for e in note['evidenceRefs']if e['path'].endswith('/result.json')];assert len(receipt_paths)==4
 for p in receipt_paths:
  r=read(p)
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  for e in r['evidenceRefs']:assert ref(ROOT/e['path'])==e
 identity=read(B/'government-xl-nam-fung-podium45779-current-unchanged-owned-identity-v1-20261011/selection.json.gz')['rows'][0];assert identity['uid']==UID and identity['sourceSHA256']==SHA
 paths={Path(__file__),HELD/'held.json',HELD/'HELD.md'}|set(receipt_paths)|{ROOT/e['path']for e in note['evidenceRefs']};paths.add(ROOT/identity['candidate']['path']);assert ref(ROOT/identity['candidate']['path'])['sha256']==SHA
 spec=importlib.util.spec_from_file_location('reviewed_source_freezer',HERE/'parkview_block17_freeze_current_source_evidence_20261011.py');f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f);f.local_imports(Path(__file__),paths)
 report=dict(uids=[UID],sourceSHA256=SHA,sourceRevision=dict(modelId=identity['modelId'],buildingCSUID=identity['source']['building']['buildingCSUID'],sourceSHA256=SHA,sourceCacheKey=identity['native']['cacheKey'],sourceResultSHA256=identity['native']['resultSha']),sourceOnly=True,currentHeldReason='original-podium-mainbody-identity-missing-and-excess-unresolved',workStatus='held',inProcess=False,identityAccepted=False,physicalAccepted=False,sourceHeld=True,completeOriginalPodiumFacesRetained=1461,completePairOriginalFacesRetained=14522,exactBlockedReason=note['reason'],requiredChangedEvidence=note['requiredChangedInput'],nextStep='Obtain authoritative full original shared-podium/as-built/component or versionedGIS extent evidence accounting BOTH mainbody0 excess565.3278316588411m2/extent11.49293812130819m and missingtarget717.8065694567479m2. Official renumber45779→45741 at stableCSUID alone does not resolve identity; no unchanged-policy/contact rerun.',causalJobIds=[read(p)['jobId']for p in receipt_paths if 'attribution' in str(p)or 'epoch-context' in str(p)],modelReviewWrites=0,pointerWrites=0,installationApproved=False,permanentRejection=False,qualification='Durable UID/source-revision indexed immutable jobs held report only. No model_reviews rows currently exist for the pair; absence is not an installed or approved state. Local prior note remains unchanged. All source geometry and protected review history preserved.',protectedReviewRowsBeforeAfter=before)
 save(DOC/'held-report.json',report);result=f.F.freeze(BATCH,'exact-uid-source-revision-held-report-no-review-write',sorted(paths),report)
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(result['jobId'],)).fetchone()==('complete',result)
 for e in result['evidenceRefs']:assert ref(ROOT/e['path'])==e
 assert state()==before and reservations.owns(lease);print(json.dumps(dict(jobId=result['jobId'],uid=UID,sourceSHA256=SHA,allRefs=len(result['evidenceRefs']),modelReviewWrites=0,protectedRowsUnchanged=True)),flush=True)
if __name__=='__main__':main()
