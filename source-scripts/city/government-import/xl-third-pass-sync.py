"""Persist refined local-compute blockers from the XL third-pass terrain attempts."""
import importlib.util,json,subprocess,sys,uuid
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));spec=importlib.util.spec_from_file_location('second',Path(__file__).with_name('xl-second-pass.py'));s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)
ROOT,HERE=s.ROOT,s.HERE;read,save,h,rel=s.read,s.save,s.h,s.rel
DOC=s.DOC/'third-pass';LOCAL=s.LOCAL/'third-pass-sync';BATCH='government-xl-50-third-pass-20260914';STAGE='deterministic-xl-terrain-and-support-checkpoint-v1'
TARGETS={
 'landsd/31275:0':('terrain-harbourfront','parent-water-mask-boundary','Build a shoreline-aware source terrain patch that preserves the parent water mask, then repeat neighbour and browser gates.'),
 'landsd/230643:0':('terrain-v-city','incomplete-source-roof-support-and-neighbour-regression','Resolve the ten retained tower supports or construct a smaller terrain patch that does not regress their bases, then repeat browser gates.'),
 'landsd/147024:0':('terrain-chung-kin','source-terrain-parent-hole-unfilled','Extend deterministic parent-hole filling within the bounded source patch, then repeat neighbour and browser gates.'),
 'landsd/265311:0':('terrain-spectra-3','native-overlap-evidence-drift','Regenerate and freeze the native-overlap evidence against the unchanged source, then repeat terrain and browser gates.'),
}
sys.path.insert(0,str(HERE.parent/'model-review-ledger'));import ledger
def start():
 claim=s.reservations.claim('codex-xl-third-pass-sync-'+str(uuid.uuid4()),['building:'+uid for uid in TARGETS],batch=BATCH);assert claim['ok'];save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)));s.call([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--',sys.executable,__file__,'owned'])
def owned():
 receipt=LOCAL/'reservation.json';assert s.reservations.owns(read(receipt));pointer=read(ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json');snapshot=pointer['snapshotId'];evidence={};rows=[]
 for uid,(key,reason,next_step) in TARGETS.items():
  path=DOC/key/'result.json';result=read(path);assert result['uid']==uid and not result['passed'] and result['aiCalls']==0;evidence[rel(path)]=h(path);rows.append({'uid':uid,'humanStatus':'held-unknown','actionableState':'held-for-local-scripted-processing','holdOwner':'local-scripted-processing','reason':reason,'nextStep':next_step,'evidence':{'path':rel(path),'sha256':h(path)},'requiresAI':False,'requiresUserDecision':False,'needsMoreCompute':True,'aiCalls':0,'modelGeometryChanges':0})
 uids=[r['uid'] for r in read(s.DOC/'final-script-pass/final-results.json.gz')['rows']]
 with s.connect() as connection:
  connection.execute('SET TRANSACTION READ ONLY');states=dict(connection.execute('SELECT uid,review_state FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=ANY(%s)',(snapshot,uids)))
 counts={'installed':sum(v=='installed-verified' for v in states.values()),'to-do':0,'held-human':0,'held-ai':0,'held-unknown':sum(v=='held' for v in states.values()),'in-process':0};assert len(states)==50 and counts=={'installed':5,'to-do':0,'held-human':0,'held-ai':0,'held-unknown':45,'in-process':0}
 payload={'models':50,'installed':5,'heldLocalProcessing':45,'refinedThisPass':len(rows),'aiCalls':0};job_id=s.jobs.enqueue(BATCH,STAGE,payload);job=s.jobs.claim(BATCH,read(receipt)['owner'],[STAGE],lease_seconds=600);assert job and job['id']==job_id
 report={'batch':BATCH,'stage':STAGE,'jobId':job_id,'snapshot':snapshot,'humanCounts':counts,'refinedRows':rows,'evidenceHashes':evidence,'aiCalls':0,'modelGeometryChanges':0,'publication':False};save(DOC/'checkpoint.json',report);report['evidence']={'path':rel(DOC/'checkpoint.json'),'sha256':h(DOC/'checkpoint.json')};assert s.jobs.finish(job,result=report)
 commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();effort={'method':'scripted','ai_model':None,'reasoning_effort':'not-applicable','issue':'HKS-203','run_id':BATCH,'job_id':job_id,'output_ref':rel(DOC/'checkpoint.json')};entries=[(row['uid'],'held',ROOT/row['evidence']['path'],f"Local third-pass checks complete. Reason: {row['reason']}. {row['nextStep']} No AI modelling or model geometry edits.",commit) for row in rows];ledger.record_many(snapshot,receipt,entries,effort=effort,request_id=BATCH+'-'+job_id[:16])
 with s.connect() as connection:
  connection.execute('SET TRANSACTION READ ONLY');stored=connection.execute("SELECT result FROM astra_modelling.jobs WHERE id=%s AND status='complete'",(job_id,)).fetchone()[0];latest=dict(connection.execute('SELECT DISTINCT ON(uid) uid,review_state FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=ANY(%s) ORDER BY uid,updated_at DESC',(snapshot,list(TARGETS))))
 assert stored==report and latest=={uid:'held' for uid in TARGETS};save(DOC/'neon-sync.json',{'jobId':job_id,'snapshot':snapshot,'humanCounts':counts,'refinedUids':list(TARGETS),'aiCalls':0});print(json.dumps(read(DOC/'neon-sync.json')))
if __name__=='__main__':owned() if len(sys.argv)>1 else start()
