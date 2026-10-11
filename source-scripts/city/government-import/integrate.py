"""Integrate the scripted original-source subset after complete staged/live runtime evidence."""
import gzip,hashlib,importlib.util,json,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];BATCH='government-200-20260911'
sys.path.insert(0,str(HERE.parent/'shared-modelling'));from db import connect
import jobs,reservations
sys.path.insert(0,str(HERE.parent/'model-review-ledger'));import ledger
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb
read=lambda p:json.loads(gzip.decompress(p.read_bytes()) if str(p).endswith('.gz') else p.read_bytes())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_suffix(p.suffix+'.tmp');tmp.write_text(json.dumps(d,indent=2)+'\n');tmp.replace(p)
def command(args):subprocess.run(args,cwd=ROOT,check=True)
def browser_verified(path,ids):
 report=read(path);assert report.get('passed') and not report['errors'],'Browser verification incomplete'
 expected={(uid,width,time) for uid in ids for width in (1280,390) for time in ('15:00','22:00')}
 actual={(v['uid'],v['width'],v['time']) for v in report['views'] if 'time' in v}
 assert actual==expected,'Missing native browser view'
 assert {v['uid'] for v in report['views'] if v.get('fallbackRetained')}==set(ids),'Missing fallback/retry proof'
 for v in report['views']:
  if 'time' in v:assert v['active'] and v['visible'] and v['pick']==v['uid'] and v['collision']==v['uid'] and not v['overflow']
 return report

def main():
 doc=ROOT/'docs/astra-city/government-import'/BATCH/'acceptance';local=HERE/'local'/BATCH;stage=HERE/'accepted'/BATCH;receipt_path=local/'acceptance-reservation.json';receipt=read(receipt_path)
 assert reservations.owns(receipt),'Current source reservation required'
 decision=read(doc/'decision.json');catalogue=read(stage/'catalogue.json');ids={m['uid'] for m in catalogue['models']}
 assert ids=={r['uid'] for r in decision['rows'] if r['action']=='stage-original-import'}
 assert sha(stage/'catalogue.json')==decision['catalogueSHA256'] and sha(stage/'plan.json')==decision['planSHA256']
 assert sha(HERE/'acceptance-policy.py')==decision['policySHA256'] and sha(doc/'metrics.json')==decision['metricsSHA256']
 for rel,digest in decision['inputHashes'].items():assert sha(ROOT/rel)==digest,'Staged source/terrain input changed'
 browser_verified(doc/'staged-browser.json',ids)
 pointer_path=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';previous=read(pointer_path);inventory=read(ROOT/previous['inventory'])
 source=read(doc.parent/'selection.json.gz');sources={r['uid']:r for r in source['rows']}
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  live=dict(c.execute('SELECT DISTINCT ON(uid) uid,review_state FROM astra_modelling.model_reviews WHERE uid=ANY(%s) ORDER BY uid,updated_at DESC',(sorted(ids),)).fetchall())
 assert not any(s in ('held','source-unavailable','identity-unresolved','installed-verified') for s in live.values()),'Review state changed; re-evaluate explicitly'
 parts={p['uid']:p for p in inventory['parts']}
 for m in catalogue['models']:
  parts[m['uid']]={'uid':m['uid'],'name':m.get('label'),'landmarkIds':[],'objectId':m['objectId'],'csuid':m['buildingCSUID'],'candidate':{'sha256':m['sha256']},'sourceProgress':'prepared-for-review','classification':'script-verified-original-government-import','knownHold':False}
 new_parts=sorted(parts.values(),key=lambda p:p['uid']);snapshot=hashlib.sha256(jobs.encode([new_parts,decision['policy'],decision['policySHA256']]).encode()).hexdigest()[:16]
 inv_path=pointer_path.parent/f'source-review-inventory-{snapshot}.json';save(inv_path,{**inventory,'snapshotId':snapshot,'derivedFrom':previous['snapshotId'],'parts':new_parts,'qualification':'Original government parts accepted by source/placement/runtime script contract; no architectural reconstruction or complete landmark claim.'})
 ledger.seed(inv_path,inherit=previous['snapshotId'])
 approval={'policy':decision['policy'],'decision':{'path':str((doc/'decision.json').relative_to(ROOT)),'sha256':sha(doc/'decision.json')},'stagedBrowser':{'path':str((doc/'staged-browser.json').relative_to(ROOT)),'sha256':sha(doc/'staged-browser.json')},'models':[{'uid':m['uid'],'sha256':m['sha256']} for m in catalogue['models']],'aiCalls':0,'architecturalReconstruction':False,'wholeLandmarkComplete':False}
 save(doc/'approval.json',approval)
 effort={'method':'scripted','ai_model':None,'reasoning_effort':'not-applicable','issue':'HKS-203','run_id':snapshot,'output_ref':str((doc/'approval.json').relative_to(ROOT))}
 commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
 observation='Script-verified import of unchanged original government source. Exact identity/source hash; conservative drawn-terrain/contact and mobile budget gates; desktop/mobile native loading, picking, collision, day/night and fallback/retry passed. No AI architectural review or whole-landmark completion.'
 ledger.record_many(snapshot,receipt_path,[(uid,'approved-for-integration',doc/'approval.json',observation,commit) for uid in sorted(ids)],effort=effort,request_id='government-direct-approve-'+snapshot)
 publication=[sys.executable,str(HERE.parent/'model-integration-20260909/publish.py'),str((stage/'plan.json').relative_to(ROOT)),'--receipt',str(receipt_path),'--phase','government-direct-20260911']
 command(publication)
 manifest=ROOT/'3d-viewer/city/data/manifest.json';before=manifest.read_bytes();(local/'manifest-before-publication.json').write_bytes(before)
 command(publication+['--apply'])
 try:
  command(['node',str(HERE/'browser-acceptance.mjs'),'live']);browser_verified(doc/'live-browser.json',ids)
 except BaseException:
  # Restore the routing manifest. New immutable assets stay unreferenced for diagnosis.
  manifest.write_bytes(before)
  raise
 approval['installedBrowser']={'path':str((doc/'live-browser.json').relative_to(ROOT)),'sha256':sha(doc/'live-browser.json')};approval['manifestSHA256']=sha(manifest);save(doc/'installed-acceptance.json',approval)
 ledger.record_many(snapshot,receipt_path,[(uid,'installed-verified',doc/'installed-acceptance.json',observation,commit) for uid in sorted(ids)],effort=effort,request_id='government-direct-installed-'+snapshot)
 assert read(pointer_path)==previous,'Current review pointer changed during integration'
 save(pointer_path,{'snapshotId':snapshot,'inventory':str(inv_path.relative_to(ROOT)),'previousSnapshots':[*previous.get('previousSnapshots',[]),previous['snapshotId']],'qualification':previous['qualification']})
 command([sys.executable,str(HERE.parent/'building-progress/export.py'),'--refresh']);command(['node',str(ROOT/'3d-viewer/scripts/build_progress.mjs')])
 result={'policy':decision['policy'],'batch':BATCH,'snapshotId':snapshot,'installed':len(ids),'remainingFromBatch':200-len(ids),'rows':[{**r,'action':'installed-verified' if r['uid'] in ids else r['action']} for r in decision['rows']],'originalPending':139,'evidence':str((doc/'installed-acceptance.json').relative_to(ROOT)),'evidenceSHA256':sha(doc/'installed-acceptance.json'),'aiCalls':0,'geometryChanges':0,'wholeLandmarkComplete':False}
 job_id=jobs.enqueue(BATCH+'-acceptance','original-government-import-v1',{'decisionSHA256':sha(doc/'decision.json'),'snapshot':snapshot});job=jobs.claim(BATCH+'-acceptance',receipt['owner'],['original-government-import-v1'],lease_seconds=600);assert job and job['id']==job_id
 with connect() as c:
  c.row_factory=dict_row;c.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));group=reservations._current(c,receipt)
  assert group and {'building:'+r['uid'] for r in decision['rows']}<=set(group['resources'])
  assert c.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),job_id,job['owner'],job['token'])).rowcount==1
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT result FROM astra_modelling.jobs WHERE id=%s',(job_id,)).fetchone()[0]==result
  states=c.execute('SELECT uid,review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=ANY(%s)',(snapshot,sorted(ids))).fetchall();assert {u for u,s,h in states if s=='installed-verified'}==ids
 save(doc/'integration.json',{**result,'jobId':job_id,'neonVerified':True,'progress':read(ROOT/'3d-viewer/city/data/building-progress.json')})
 print(json.dumps({'installed':len(ids),'remaining':200-len(ids),'snapshot':snapshot,'neonVerified':True,'aiCalls':0}))
if __name__=='__main__':main()
