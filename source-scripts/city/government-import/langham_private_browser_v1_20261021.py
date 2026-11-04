"""Private unchanged two-source assembly browser diagnostics; no publication."""
from pathlib import Path
import copy,json,os,subprocess,sys,uuid
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-langham-private-browser-v1-20261021';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
CAP=BASE/'government-xl-langham-assembly-capture-v1-20261021';PATCH=BASE/'government-xl-grandiose-private-terrain-v9-20261021';POD='landsd/224399:0'
def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease)and not DOC.exists();refs=[Path(__file__)];pins={};used={}
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  for folder in [CAP]:
   r=read(folder/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json');pins[folder]={e['path']:e['sha256']for e in r['evidenceRefs']}
 def take(folder,p):
  key=str(p.relative_to(ROOT));assert digest(p.read_bytes())==pins[folder][key];used[key]=pins[folder][key];refs.append(p);return read(p)
 allrows=take(CAP,CAP/'selection.json.gz')['rows'];mall=next(r for r in allrows if r['uid']==POD);rows=[r for r in allrows if r['uid']=='landsd/79318:0'];uids=[r['uid']for r in rows];assert len(uids)==1;models=[];forms={}
 for r in rows:
  tile=ROOT/'3d-viewer'/r['source']['tile'];b=next(b for b in read(tile)['buildings']if b['uid']==r['uid']);assert b==r['source']['building'];refs.append(tile);forms[r['uid']]=r['source']
  with connect()as db:
   db.execute('SET TRANSACTION READ ONLY');record=db.execute('SELECT i.sheet,r.result_sha FROM astra_modelling.native_stage_inputs i JOIN astra_modelling.native_stage_results r USING(cache_key) WHERE i.cache_key=%s',(r['native']['cacheKey'],)).fetchone()
  assert record and record[1]==r['native']['resultSha']
  e=copy.deepcopy(r['candidate']['entry']);e.update(sourceTile=record[0],priority='landmark',label=b.get('name')or r['uid'],proceduralWindows=False,publicationApproved=False,placementReviewed=False)
  e['supportDependencies']=[]if r['uid']==POD else[dict(uid=POD,csuid=mall['candidate']['entry']['buildingCSUID'],sha256=mall['sourceSHA256'],state='installed')]
  asset=ROOT/r['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==r['sourceSHA256'];refs.append(asset);e['asset']='assets/'+r['sourceSHA256']+'.glb.gz';dest=LOCAL/e['asset'];dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw);models.append(e)
 save(LOCAL/'catalogue.json',dict(schemaVersion=1,kind='staged-official-model-catalogue',datasetId='landsd_rcd_1742809441342_98380',crs='EPSG:2326',verticalDatum='Hong Kong Principal Datum',rootTranslation=[-834500,0,816500],models=models,counts=dict(packedModels=1)))
 save(LOCAL/'catalogue-index.json',dict(models=1,catalogues=['catalogue.json']));save(LOCAL/'source-forms.json',[forms[u]['building']for u in uids]);save(LOCAL/'validation-forms.json',forms)
 terrain=[];save(DOC/'terrain-candidates.json',[]);tool=HERE.parent/'building-batch/validate_candidates.mjs';refs.append(tool)
 cmd=['node',str(tool),'--candidates',str(LOCAL.relative_to(ROOT)),'--source-forms',str((LOCAL/'validation-forms.json').relative_to(ROOT)),'--out',str((DOC/'validation.json').relative_to(ROOT))]
 with(DOC/'loader.log').open('w')as log:proc=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,timeout=600)
 v=read(DOC/'validation.json');assert proc.returncode==0 and v['loaderAccepted']==1 and not v['exceptions']
 config=dict(stage=str(LOCAL.relative_to(ROOT))+'/',catalogueURL='city/data/official-models/'+BATCH+'/catalogue.json',terrain=[],browserUids=uids,failureTestUids=uids,nativeSupportUidsByModel={u:[POD] for u in uids},fitBox=True,captureDirectionByModel={u:[1,0.7,1] for u in uids},localJointViews=[dict(id='original-tower-podium-contact',uids=[POD,uids[0]],target=[938.5,20.864,-3343.1],camera=[958,30,-3330])])
 browser=HERE/'manhattan_collision_witness_browser_v1_20261021.mjs';refs.append(browser)
 for width in [1280,390]:
  assert reservations.owns(lease);cfg={**config,'viewportWidths':[width],'doc':str((DOC/str(width)).relative_to(ROOT))+'/'};path=LOCAL/f'browser-config-{width}.json';save(path,cfg)
  with(DOC/f'browser-{width}.log').open('w')as log:proc=subprocess.run(['node',str(browser),'staged',str(path.relative_to(ROOT))],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'},timeout=1800)
  save(DOC/f'command-{width}.json',dict(exitCode=proc.returncode));assert proc.returncode==0
  report=read(DOC/str(width)/'staged-browser.json');assert report['passed']and len([v for v in report['views']if 'time'in v])==2
 for p,h in used.items():assert digest((ROOT/p).read_bytes())==h
 for p,h in v['hashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 refs.extend(p for p in LOCAL.rglob('*')if p.is_file()and p.name!='reservation.json')
 module('yoho_browser_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'private-two-source-desktop-mobile-and-local-contact-browser',list(dict.fromkeys(refs)),dict(uids=uids,installationApproved=False,visualAcceptance=False,geometryChanges=0))
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists()and not LOCAL.exists();claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];p=LOCAL/'reservation.json';save(p,json.loads(json.dumps(lease,default=str)))
 try:subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(p),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
