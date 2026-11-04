"""Authorised canonical supervised run and established source-only freeze, no review writes."""
from pathlib import Path
import sys,subprocess,json,uuid,importlib.util
from run import ROOT,HERE,read,save,digest,connect,reservations
B=ROOT/'docs/astra-city/government-import';BATCH='government-xl-nam-fung-podium45779-causal-identity-workflow-v1-20261011';LOCAL=HERE/'local'/BATCH;UIDS=['landsd/45779:0','landsd/79099:0']
RUNS=[('nam_fung_podium45779_complete_original_body_identity_attribution_v1_20261011.py','5a7ed5d45419badc2aa5d64b84dcb04225358bfee0f63337dfeb218a7e7c7ef3','government-xl-nam-fung-podium45779-complete-original-body-identity-attribution-v1-20261011','diagnostic.json.gz'),('nam_fung_podium45779_bounded_official_identity_epoch_context_v1_20261011.py','ff89ce5c95ae3585235f565bd5964ecb8851e379791cf0c28aafd39751302dad','government-xl-nam-fung-podium45779-bounded-official-identity-epoch-context-v1-20261011','context.json')]
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def state():
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');return c.execute('SELECT row_to_json(t) FROM astra_modelling.model_reviews t WHERE uid=ANY(%s) ORDER BY uid,snapshot_id',(UIDS,)).fetchall()
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 if '--owned'not in sys.argv:
  assert not LOCAL.exists();claim=reservations.claim('nam-fung-identity-causal-'+str(uuid.uuid4()),['building:'+u for u in UIDS],batch=BATCH,ttl=1800);assert claim['ok'],claim;save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)));status=subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--ttl','1800','--',sys.executable,__file__,'--owned'],cwd=ROOT).returncode;assert status==0,status;return
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease);before=state();manifest=ROOT/'3d-viewer/city/data/manifest.json';raw=manifest.read_bytes();assert digest(raw)=='947f0a3b3a1d7167a9f98074af35d4030ff0245e121ee682eed4f9ab9baedfa6'
 walker=module('existing_reviewed_source_closure',HERE/'parkview_block17_freeze_current_source_evidence_20261011.py');results=[]
 for script,sha,batch,filename in RUNS:
  p=HERE/script;assert ref(p)['sha256']==sha and reservations.owns(lease);assert not(B/batch).exists();subprocess.run([sys.executable,str(p)],cwd=ROOT,check=True);assert state()==before and manifest.read_bytes()==raw and reservations.owns(lease)
  doc=B/batch;d=read(doc/filename);assert d['sourceOnly']and not d['currentAcceptance'];paths={q for q in doc.rglob('*')if q.is_file()};walker.local_imports(p,paths);walker.local_imports(Path(__file__),paths);walker.declared_refs(d,paths);paths.add(B/'government-xl-nam-fung-podium45779-identity-component-epoch-method-v1-20261011/METHOD.md')
  save(doc/'protected-state-and-lease-fences.json',dict(reviewRowsBeforeAfter=before,currentManifestSHA256=digest(raw),canonicalLease=ref(LOCAL/'reservation.json'),sourceOnly=True,reviewWrites=0,pointerWrites=0))
  if filename=='diagnostic.json.gz':assert d['sourceWholeFaces']==1461 and d['sourceBodies']==4 and len(d['completeBodyAttributions'])==4 and sum(r['completeOriginalFaceCount']for r in d['completeBodyAttributions'])==1461
  r=walker.F.freeze(batch,'nam-fung-source-only-causal-identity-no-acceptance',sorted(paths),dict(uids=UIDS,sourceOnly=True,currentAcceptance=False,identityAccepted=False,supportCredit=False,modelReviewWrites=0,pointerWrites=0,qualification=d['qualification']))
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  for e in r['evidenceRefs']:assert ref(ROOT/e['path'])==e
  assert state()==before and manifest.read_bytes()==raw and reservations.owns(lease);results.append(dict(batch=batch,jobId=r['jobId'],allRefsVerified=len(r['evidenceRefs'])))
 save(LOCAL/'completed-jobs.json',dict(jobs=results,protectedRowsUnchanged=True,currentManifestUnchanged=True,sourceGeometryChanges=0));print(json.dumps(results),flush=True)
if __name__=='__main__':main()
