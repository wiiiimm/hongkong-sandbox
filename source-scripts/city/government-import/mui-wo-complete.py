"""Record the installed/held Mui Wo outcomes, refresh progress, and sync Neon; no AI."""
import gzip,hashlib,importlib.util,json,subprocess,sys
from pathlib import Path
from PIL import Image,ImageStat
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];sys.path.insert(0,str(HERE.parent/'shared-modelling'))
from db import connect
import jobs,reservations
from psycopg.rows import dict_row
spec=importlib.util.spec_from_file_location('ledger',HERE.parent/'model-review-ledger/ledger.py');ledger=importlib.util.module_from_spec(spec);spec.loader.exec_module(ledger)
BATCH='government-mui-wo-23-20260914';BASE=ROOT/'docs/astra-city/government-import'/BATCH;DOC=BASE/'resolution';LOCAL=HERE/'local'/BATCH;STAGE=HERE/'accepted'/'government-mui-wo-7-20260914'
def read(p):
 raw=Path(p).read_bytes();return json.loads(gzip.decompress(raw) if str(p).endswith('.gz') else raw)
def save(p,v):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);raw=(jobs.encode(v)+'\n').encode();p.write_bytes(gzip.compress(raw,mtime=0) if str(p).endswith('.gz') else raw)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rel(p):return str(Path(p).relative_to(ROOT))
def verify_images(mode):
 browser=read(DOC/(mode+'-browser.json'));assert browser['passed'] and browser['errors']==[];images=[]
 for view in browser['views']:
  if 'file' not in view:continue
  path=DOC/view['file']
  with Image.open(path) as im:im.load();assert im.size==(view['width'],900);std=ImageStat.Stat(im.convert('RGB')).stddev;assert max(std)>1
  assert abs(view['ground']-view['groundSampler'])<=.004
  images.append({'path':rel(path),'sha256':sha(path),'width':view['width'],'height':900,'channelStddev':std})
 assert len(images)==28;report={'images':images,'decoded':len(images),'browserReportSHA256':sha(DOC/(mode+'-browser.json')),'aiImageReview':False};save(DOC/(mode+'-image-verification.json'),report);return report

def main():
 receipt_path=LOCAL/'publication-reservation.json';receipt=read(receipt_path);assert reservations.owns(receipt)
 live_images=verify_images('live');staged_images=read(DOC/'staged-image-verification.json');decision=read(DOC/'decision.json');resolution=read(DOC/'source-resolution.json');metrics=read(DOC/'staged-metrics.json');validation=read(DOC/'staged-validation.json');neighbours=read(DOC/'neighbour-checks.json');native_neighbours=read(DOC/'native-neighbour-checks.json');catalogue=read(STAGE/'catalogue.json');ids={m['uid'] for m in catalogue['models']};assert ids==set(decision['accepted']) and len(ids)==7
 assert validation['exceptions']==0 and validation['concerns']=={} and all(not p['blockedBy'] for p in neighbours['patches']) and native_neighbours['blocked']==[]
 manifest=read(ROOT/'3d-viewer/city/data/manifest.json');assert 'city/data/official-models/government-mui-wo-20260914/catalogue.json' in manifest['officialModelCatalogues'] and 'city/data/terrain-government-mui-wo-east-20260914.json' in {p['url'] for p in manifest['terrainPatches']}
 source=read(BASE/'check-selection.json.gz');by_source={r['uid']:r for r in source['rows']};by_metric={r['uid']:r for r in metrics['rows']};outcomes=[]
 for row in resolution['rows']:
  uid=row['uid'];installed=uid in ids;reasons=[] if installed else sorted(set(row['reasons'] or ['automatic-integration-proof-incomplete']))
  outcomes.append({**row,'state':'installed-verified' if installed else 'held','humanStatus':'installed' if installed else 'held-unknown','reasons':reasons,'nextDependency':None if installed else 'local-compute/source-terrain','nextStep':None if installed else 'Second-pass source terrain/contact investigation; current basic model retained','published':installed,'aiCalls':0})
 assert len(outcomes)==23 and sum(r['humanStatus']=='installed' for r in outcomes)==7 and sum(r['humanStatus']=='held-unknown' for r in outcomes)==16 and not any(r['humanStatus']=='in-process' for r in outcomes)
 report={'batch':BATCH,'modelsProcessed':23,'newlyInstalled':7,'humanCounts':{'installed':7,'to-do':0,'held-human':0,'held-ai':0,'held-unknown':16,'in-process':0},'reasonCounts':dict(sorted(__import__('collections').Counter(reason for r in outcomes for reason in r['reasons']).items())),'rows':outcomes,'aiCalls':0,'modelGeometryChanges':0,'terrainPatches':2,'qualification':'Exact government sources processed with local scripts. Seven installed after source identity, terrain, runtime, neighbour and live browser checks. Sixteen retain their current basic models with measured source-terrain/contact holds.'}
 save(DOC/'final-results.json.gz',report)
 approval={'policy':'original-government-import-v1 + exact-identity-unique-viewer-match','models':[{'uid':m['uid'],'sha256':m['sha256']} for m in catalogue['models']],'decisionSHA256':sha(DOC/'decision.json'),'metricsSHA256':sha(DOC/'staged-metrics.json'),'validationSHA256':sha(DOC/'staged-validation.json'),'neighboursSHA256':sha(DOC/'neighbour-checks.json'),'nativeNeighboursSHA256':sha(DOC/'native-neighbour-checks.json'),'stagedBrowserSHA256':sha(DOC/'staged-browser.json'),'stagedImagesSHA256':sha(DOC/'staged-image-verification.json'),'liveBrowserSHA256':sha(DOC/'live-browser.json'),'liveImagesSHA256':sha(DOC/'live-image-verification.json'),'manifestSHA256':sha(ROOT/'3d-viewer/city/data/manifest.json'),'aiCalls':0,'architectureReconstruction':False};save(DOC/'installed-acceptance.json',approval)
 pointer=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';previous=read(pointer);inventory=read(ROOT/previous['inventory']);parts={p['uid']:p for p in inventory['parts']}
 for r in source['rows']:
  uid=r['uid'];e=r['candidate']['entry'];prior=parts.get(uid,{})
  parts[uid]={'uid':uid,'name':e.get('label'),'landmarkIds':prior.get('landmarkIds',[]),'objectId':e['objectId'],'csuid':e['buildingCSUID'],'candidate':{'sha256':e['sha256']},'sourceProgress':'prepared-for-review','classification':'script-verified-original-government-import' if uid in ids else 'script-blocked-original-government-import','knownHold':uid not in ids}
 new_parts=sorted(parts.values(),key=lambda p:p['uid']);snapshot=hashlib.sha256(jobs.encode([new_parts,approval['manifestSHA256'],report['humanCounts']]).encode()).hexdigest()[:16];inventory_path=pointer.parent/f'source-review-inventory-{snapshot}.json';save(inventory_path,{**inventory,'snapshotId':snapshot,'derivedFrom':previous['snapshotId'],'parts':new_parts,'qualification':'Mui Wo exact-source pass appended seven installed records and sixteen measured local-compute terrain holds; no whole-region completion claim.'});ledger.seed(inventory_path,inherit=previous['snapshotId'])
 commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();effort={'method':'scripted','ai_model':None,'reasoning_effort':'not-applicable','issue':'HKS-203','run_id':snapshot,'output_ref':rel(DOC/'final-results.json.gz')};entries=[]
 for r in outcomes:
  if r['humanStatus']=='installed':observation='Exact unchanged government source installed after identity, native terrain/contact, runtime, neighbour, desktop/mobile day/night, fallback and retry checks. No AI modelling.';evidence=DOC/'installed-acceptance.json'
  else:observation='Local scripted pass completed; current basic model retained. Second-pass source terrain/contact work remains. Reasons: '+', '.join(r['reasons']);evidence=DOC/'final-results.json.gz'
  entries.append((r['uid'],r['state'],evidence,observation,commit))
 ledger.record_many(snapshot,receipt_path,entries,effort=effort,request_id='government-mui-wo-final-'+snapshot)
 save(pointer,{'snapshotId':snapshot,'inventory':rel(inventory_path),'previousSnapshots':[*previous.get('previousSnapshots',[]),previous['snapshotId']],'qualification':previous['qualification']})
 subprocess.run([sys.executable,str(HERE.parent/'building-progress/export.py'),'--refresh'],cwd=ROOT,check=True);subprocess.run(['node',str(ROOT/'3d-viewer/scripts/build_progress.mjs')],cwd=ROOT,check=True)
 job_id=jobs.enqueue(BATCH,'government-mui-wo-terminal-v1',{'snapshot':snapshot,'finalResultsSHA256':sha(DOC/'final-results.json.gz'),'manifestSHA256':approval['manifestSHA256']});job=jobs.claim(BATCH,receipt['owner'],['government-mui-wo-terminal-v1'],lease_seconds=600);assert job and job['id']==job_id
 result={**report,'snapshotId':snapshot,'evidence':{'path':rel(DOC/'final-results.json.gz'),'sha256':sha(DOC/'final-results.json.gz')}};assert jobs.finish(job,result=result)
 with connect() as con:
  con.row_factory=dict_row;stored=con.execute('SELECT result FROM astra_modelling.jobs WHERE id=%s',(job_id,)).fetchone()['result'];actual={row['uid']:row['review_state'] for row in con.execute('SELECT uid,review_state FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=ANY(%s)',(snapshot,[r['uid'] for r in outcomes])).fetchall()}
 assert stored==result and all(actual[r['uid']]==r['state'] for r in outcomes)
 save(DOC/'neon-sync.json',{'jobId':job_id,'snapshotId':snapshot,'verifiedRows':23,'exactResultMatch':True,'reviewStatesVerified':True,'humanCounts':report['humanCounts']})
 save(DOC/'summary.json',{k:v for k,v in report.items() if k!='rows'}|{'jobId':job_id,'snapshotId':snapshot,'progress':read(ROOT/'3d-viewer/city/data/building-progress.json')})
 released=reservations.release(receipt);assert released['ok'];print(json.dumps({'newlyInstalled':7,'held':16,'inProcess':0,'neonVerified':True,'snapshot':snapshot,'screenshots':len(live_images['images']),'aiCalls':0}))
if __name__=='__main__':main()
