"""Private unchanged eight-source assembly browser diagnostics; no publication."""
from pathlib import Path
import copy,json,os,subprocess,sys,uuid
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-siu-hong-private-browser-v1-20261021';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
CAP=BASE/'government-xl-siu-hong-private-capture-v2-20261021';PATCH=BASE/'government-xl-siu-hong-private-terrain-v4-20261021';POD='landsd/233417:0'
def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease)and not DOC.exists();refs=[Path(__file__)];pins={};used={}
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  for folder in [CAP,PATCH]:
   r=read(folder/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json');pins[folder]={e['path']:e['sha256']for e in r['evidenceRefs']}
 def take(folder,p):
  key=str(p.relative_to(ROOT));assert digest(p.read_bytes())==pins[folder][key];used[key]=pins[folder][key];refs.append(p);return read(p)
 rows=take(CAP,CAP/'selection.json.gz')['rows'];uids=[r['uid']for r in rows];assert len(uids)==2;models=[];forms={}
 mall=next(r for r in rows if r['uid']==POD)
 for r in rows:
  tile=ROOT/'3d-viewer'/r['source']['tile'];b=next(b for b in read(tile)['buildings']if b['uid']==r['uid']);assert b==r['source']['building'];refs.append(tile);forms[r['uid']]=r['source']
  with connect()as db:
   db.execute('SET TRANSACTION READ ONLY');record=db.execute('SELECT i.sheet,r.result_sha FROM astra_modelling.native_stage_inputs i JOIN astra_modelling.native_stage_results r USING(cache_key) WHERE i.cache_key=%s',(r['native']['cacheKey'],)).fetchone()
  assert record and record[1]==r['native']['resultSha']
  e=copy.deepcopy(r['candidate']['entry']);e.update(sourceTile=record[0],priority='landmark',label=b.get('name')or r['uid'],proceduralWindows=False,publicationApproved=False,placementReviewed=False)
  e['supportDependencies']=[]if r['uid']==POD else[dict(uid=POD,csuid=mall['candidate']['entry']['buildingCSUID'],sha256=mall['sourceSHA256'],state='candidate')]
  asset=ROOT/r['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==r['sourceSHA256'];refs.append(asset);e['asset']='assets/'+r['sourceSHA256']+'.glb.gz';dest=LOCAL/e['asset'];dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw);models.append(e)
 save(LOCAL/'catalogue.json',dict(schemaVersion=1,kind='staged-official-model-catalogue',datasetId='landsd_rcd_1742809441342_98380',crs='EPSG:2326',verticalDatum='Hong Kong Principal Datum',rootTranslation=[-834500,0,816500],models=models,counts=dict(packedModels=2)))
 save(LOCAL/'catalogue-index.json',dict(models=2,catalogues=['catalogue.json']));save(LOCAL/'source-forms.json',[forms[u]['building']for u in uids]);save(LOCAL/'validation-forms.json',forms)
 candidate=take(PATCH,PATCH/'terrain-candidates.json')[0];path=ROOT/candidate['path'];assert digest(path.read_bytes())==candidate['sha256'];refs.append(path)
 terrain=[dict(source=candidate['path'],destination='city/data/government-native-siu-hong-private-v1-20261021.json',sha256=candidate['sha256'],resolution=read(path)['cell'],area='Private Siu Hong original assembly')]
 save(DOC/'terrain-candidates.json',[candidate]);scope=take(CAP,CAP/'input.json.gz')['conditionalScope'];scope['moduleSHA256']=digest((ROOT/'3d-viewer/city/official-model-direct-osm-group-data.js').read_bytes());save(LOCAL/'conditional-scope.json',scope);tool=HERE/'siu_hong_validate_private_scope_v1_20261021.mjs';refs.extend([tool,HERE.parent/'building-batch/validate_candidates_footprint_scope.mjs',ROOT/'3d-viewer/city/official-model-direct-osm-group-data.js'])
 cmd=['/home/williamli/.nvm/versions/node/v24.18.0/bin/node',str(tool),'--conditional-scope',str(LOCAL/'conditional-scope.json'),'--terrain-candidates',str((DOC/'terrain-candidates.json').relative_to(ROOT)),'--candidates',str(LOCAL.relative_to(ROOT)),'--source-forms',str((LOCAL/'validation-forms.json').relative_to(ROOT)),'--out',str((DOC/'validation.json').relative_to(ROOT))]
 with(DOC/'loader.log').open('w')as log:proc=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,timeout=600)
 v=read(DOC/'validation.json');assert proc.returncode==0 and v['loaderAccepted']==2 and not v['exceptions']
 config=dict(stage=str(LOCAL.relative_to(ROOT))+'/',catalogueURL='city/data/official-models/'+BATCH+'/catalogue.json',terrain=terrain,conditionalScope=scope,browserUids=uids,failureTestUids=uids,jointUidsByModel={u:[u]if u==POD else[POD,u]for u in uids},nativeSupportUidsByModel={u:[POD]for u in uids if u!=POD},fitBox=True,captureDirectionByModel={u:[.7,.6,-1]for u in uids},jointUids=uids)
 browser=HERE/'yoho_mall_i_settled_joint_browser_v1_20261020.mjs';refs.append(browser)
 for width in [1280,390]:
  assert reservations.owns(lease);cfg={**config,'viewportWidths':[width],'doc':str((DOC/str(width)).relative_to(ROOT))+'/'};path=LOCAL/f'browser-config-{width}.json';save(path,cfg)
  with(DOC/f'browser-{width}.log').open('w')as log:proc=subprocess.run(['/home/williamli/.nvm/versions/node/v24.18.0/bin/node',str(browser),'staged',str(path.relative_to(ROOT))],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'},timeout=1800)
  save(DOC/f'command-{width}.json',dict(exitCode=proc.returncode));assert proc.returncode==0
  report=read(DOC/str(width)/'staged-browser.json');assert report['passed']and len([v for v in report['views']if 'time'in v])==4
 for p,h in used.items():assert digest((ROOT/p).read_bytes())==h
 for p,h in v['hashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 refs.extend(p for p in LOCAL.rglob('*')if p.is_file()and p.name!='reservation.json')
 module('yoho_browser_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'private-eight-source-desktop-mobile-and-local-contact-browser',list(dict.fromkeys(refs)),dict(uids=uids,installationApproved=False,visualAcceptance=False,geometryChanges=0))
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists()and not LOCAL.exists();claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];p=LOCAL/'reservation.json';save(p,json.loads(json.dumps(lease,default=str)))
 try:subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(p),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
