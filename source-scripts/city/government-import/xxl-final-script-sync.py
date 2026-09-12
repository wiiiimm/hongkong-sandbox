"""Finalize the ten-model XXL scripted pass and persist its human states to Neon."""
from collections import Counter
import importlib.util, json, subprocess, sys, uuid
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
spec=importlib.util.spec_from_file_location('second',Path(__file__).with_name('xxl-second-pass.py'));s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)
ROOT,HERE=s.ROOT,s.HERE;DOC=s.DOC/'final-script-pass';LOCAL=s.LOCAL/'final-script-sync';BATCH='government-xxl-final-script-pass-20260913';STAGE='deterministic-geometry-terminal-routing-v1';read,save,h,rel=s.read,s.save,s.h,s.rel
sys.path.insert(0,str(HERE.parent/'model-review-ledger'));import ledger


def start():
 rows=read(DOC/'results.json.gz')['rows'];uids=sorted(r['uid'] for r in rows if r['uid']!='landsd/262871:0')
 claim=s.reservations.claim('codex-xxl-final-script-sync-'+str(uuid.uuid4()),['building:'+u for u in uids],batch=BATCH);assert claim['ok']
 save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)))
 s.call([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--',sys.executable,__file__,'owned'])


def owned():
 receipt=LOCAL/'reservation.json';assert s.reservations.owns(read(receipt));source=read(DOC/'results.json.gz');rows=[]
 for original in source['rows']:
  row={k:original[k] for k in ('modelId','uid','name','sourceSHA256','sourceSheet','scriptedWorkComplete','identityScriptAccepted','foundationScriptAccepted','reasons','requiresAI','requiresUserDecision','aiCalls','modelGeometryChanges')}
  if row['uid']=='landsd/262871:0':
   acceptance=DOC/'v-walk/installed-acceptance.json';assert acceptance.exists()
   row.update(humanStatus='installed',actionableState='installed-verified',needsMoreCompute=False,nextStep=None,installedEvidence={'path':rel(acceptance),'sha256':h(acceptance)})
  else:
   reasons=row['reasons'];assert reasons
   if reasons==['source-assembly-suppression-map-unresolved']:
    next_step='Architectural/source-component review is needed to decide a safe suppression map; retain the current fallback.'
   elif reasons==['below-grade-source-surfaces-require-exception-or-terrain-resolution']:
    next_step='A source-preserving foundation exception or native terrain correction must be proven; retain the current fallback.'
   else:
    next_step='Both a safe source-component suppression map and a source-preserving foundation/terrain resolution are required; retain the current fallback.'
   row.update(humanStatus='held-unknown',actionableState='held-after-complete-script-pass',needsMoreCompute=False,nextStep=next_step)
  rows.append(row)
 assert len(rows)==10 and sum(r['humanStatus']=='installed' for r in rows)==1 and all(r['scriptedWorkComplete'] for r in rows)
 counts={key:sum(r['humanStatus']==key for r in rows) for key in ('installed','to-do','held-human','held-ai','held-unknown','in-process')}
 reason_counts=dict(Counter(reason for row in rows for reason in row['reasons']))
 evidence=[HERE/'xxl-final-script-pass.py',HERE/'xxl-stage-v-walk.py',HERE/'xxl-v-walk-support.mjs',HERE/'xxl-v-walk-dependencies.py',HERE/'xxl-v-walk-import.py',DOC/'results.json.gz',DOC/'v-walk/native-support.json',DOC/'v-walk/staged-browser.json',DOC/'v-walk/live-browser.json',DOC/'v-walk/installed-acceptance.json']
 evidence_hashes={rel(p):h(p) for p in evidence}
 report={'batch':BATCH,'stage':STAGE,'models':10,'humanCounts':counts,'reasonCounts':reason_counts,'rows':rows,'evidenceHashes':evidence_hashes,'aiCalls':0,'modelGeometryChanges':0,'publication':True,'qualification':'All ten previously uninstalled XXL sources completed deterministic identifier, projection/assembly, vertical-neighbour, connected below-grade-face and sequential runtime checks. V Walk additionally passed dependency, staged/live browser and installation gates. Later gates were intentionally skipped for sources that failed an earlier gate.'}
 payload={'models':10,'sourceEvidenceSHA256':h(DOC/'results.json.gz'),'installed':1,'held':9}
 existing=read(DOC/'final-results.json.gz') if (DOC/'final-results.json.gz').exists() else None
 if existing and existing.get('batch')==BATCH and existing.get('jobId'):
  job_id=existing['jobId']
  with s.connect() as connection:
   connection.execute('SET TRANSACTION READ ONLY');stored=connection.execute("SELECT result FROM astra_modelling.jobs WHERE id=%s AND status='complete'",(job_id,)).fetchone()
  assert stored;report=stored[0]
 else:
  job_id=s.jobs.enqueue(BATCH,STAGE,payload);job=s.jobs.claim(BATCH,read(receipt)['owner'],[STAGE],lease_seconds=600);assert job and job['id']==job_id
  report['jobId']=job_id;save(DOC/'final-results.json.gz',report);report['evidence']={'path':rel(DOC/'final-results.json.gz'),'sha256':h(DOC/'final-results.json.gz')};assert s.jobs.finish(job,result=report)
 pointer_path=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';pointer=read(pointer_path);previous_snapshot=pointer['snapshotId'];inventory=read(ROOT/pointer['inventory']);parts={part['uid']:part for part in inventory['parts']};full={r['uid']:r for r in source['rows']};held=[r for r in rows if r['humanStatus']=='held-unknown']
 for row in held:
  if row['uid'] in parts:continue
  target=full[row['uid']]['identity']['target'];parts[row['uid']]={'uid':row['uid'],'name':row['name'] or target.get('name'),'landmarkIds':[],'objectId':target['objectId'],'csuid':target['buildingCSUID'],'candidate':{'sha256':row['sourceSHA256']},'sourceProgress':'prepared-for-review','classification':'scripted-xxl-held-after-complete-pass','knownHold':True}
 ordered=sorted(parts.values(),key=lambda row:row['uid']);snapshot=s.digest(s.jobs.encode([ordered,h(DOC/'results.json.gz')]).encode())[:16];inventory_path=pointer_path.parent/f'source-review-inventory-{snapshot}.json';save(inventory_path,{**inventory,'snapshotId':snapshot,'derivedFrom':previous_snapshot,'parts':ordered});ledger.seed(inventory_path,inherit=previous_snapshot)
 commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();effort={'method':'scripted','ai_model':None,'reasoning_effort':'not-applicable','issue':'HKS-203','run_id':BATCH,'job_id':job_id,'output_ref':rel(DOC/'final-results.json.gz')};entries=[]
 for row in held:
  observation='All configured deterministic XXL checks are complete; current fallback retained. '+row['nextStep']+' Reasons: '+', '.join(row['reasons'])
  entries.append((row['uid'],'held',DOC/'final-results.json.gz',observation,commit))
 ledger.record_many(snapshot,receipt,entries,effort=effort,request_id=BATCH+'-'+job_id[:16])
 assert read(pointer_path)==pointer;save(pointer_path,{**pointer,'snapshotId':snapshot,'inventory':rel(inventory_path),'previousSnapshots':[*pointer.get('previousSnapshots',[]),previous_snapshot]})
 with s.connect() as connection:
  connection.execute('SET TRANSACTION READ ONLY');stored=connection.execute("SELECT result FROM astra_modelling.jobs WHERE id=%s AND status='complete'",(job_id,)).fetchone()[0];states=dict(connection.execute('SELECT uid,review_state FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=ANY(%s)',(snapshot,[r['uid'] for r in held])))
 assert stored==report and states=={r['uid']:'held' for r in held}
 save(DOC/'neon-sync.json',{'jobId':job_id,'snapshot':snapshot,'rows':10,'installed':1,'held':9,'inProcess':0,'exactJobResultMatch':True,'heldReviewStatesMatch':True,'aiCalls':0})
 save(DOC/'final-summary.json',{k:v for k,v in report.items() if k!='rows'})
 print(json.dumps({'jobId':job_id,'snapshot':snapshot,'humanCounts':counts,'reasonCounts':reason_counts,'aiCalls':0}),flush=True)


if __name__=='__main__':owned() if len(sys.argv)>1 else start()
