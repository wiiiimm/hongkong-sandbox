"""Staged original-source visual/runtime diagnostics; no live publication."""
from pathlib import Path
import copy,os,subprocess,json,sys,uuid
from run import ROOT,HERE,read,save,digest,reservations,connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-ronsdale-three-staged-browser-v1-20261022';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
NODE='/home/williamli/.nvm/versions/node/v24.18.0/bin/node'
def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease)and not DOC.exists();refs=[Path(__file__)];pins={}
 def take(n,p):
  _,ps=authenticate(BASE/n);k=str(p.relative_to(ROOT));assert digest(p.read_bytes())==ps[k];pins[k]=ps[k];refs.extend([BASE/n/'result.json',p]);return read(p)
 sn='government-xl-ronsdale-three-source-runtime-v1-20261022';rows=take(sn,BASE/sn/'selection.json.gz')['rows'];uids=[r['uid']for r in rows];assert set(uids)=={'landsd/256898:0','landsd/256702:0','landsd/233771:0'};entries=[]
 for row in rows:
  uid=row['uid'];form=row['source'];tp=ROOT/'3d-viewer'/form['tile'];assert digest(tp.read_bytes())==form['tileSHA256'];refs.append(tp)
  with connect()as db:
   db.execute('SET TRANSACTION READ ONLY');native=db.execute('SELECT i.sheet,r.result_sha FROM astra_modelling.native_stage_inputs i JOIN astra_modelling.native_stage_results r USING(cache_key) WHERE i.cache_key=%s',(row['native']['cacheKey'],)).fetchone()
  assert native and native[1]==row['native']['resultSha']
  entry=copy.deepcopy(row['candidate']['entry']);
  if uid in {'landsd/256898:0','landsd/256702:0'}:
   podium=next(r for r in rows if r['uid']=='landsd/233771:0');entry['supportDependencies']=[dict(uid=podium['uid'],state='installed',buildingCSUID=podium['source']['building']['buildingCSUID'],sha256=podium['sourceSHA256'])]
  entry['sourceTile']=native[0];entry.update(priority='landmark',proceduralWindows=False,publicationApproved=False,placementReviewed=False);ap=ROOT/row['candidate']['path'];assert digest(ap.read_bytes())==row['sourceSHA256'];refs.append(ap);entry['asset']='assets/'+row['sourceSHA256']+'.glb.gz';dest=LOCAL/entry['asset'];dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(ap.read_bytes());entries.append(entry)
 save(LOCAL/'catalogue.json',dict(schemaVersion=1,kind='staged-official-model-catalogue',datasetId='landsd_rcd_1742809441342_98380',crs='EPSG:2326',verticalDatum='Hong Kong Principal Datum',rootTranslation=[-834500,0,816500],models=entries,counts=dict(packedModels=3)))
 save(LOCAL/'catalogue-index.json',dict(models=3,catalogues=['catalogue.json']));save(LOCAL/'source-forms.json',[r['source']['building']for r in rows]);save(LOCAL/'validation-forms.json',{r['uid']:r['source']for r in rows})
 cn='government-xl-ronsdale-local-inset-v2-20261022';candidate=take(cn,BASE/cn/'terrain-candidates.json')[0];p=ROOT/candidate['path'];assert digest(p.read_bytes())==candidate['sha256'];refs.append(p)
 terrain=[dict(source=candidate['path'],destination='city/data/government-native-ronsdale-private-browser-v1-20261022.json',sha256=candidate['sha256'],resolution=read(p)['cell'],area='Private Illumination original diagnostic')]
 tool=HERE/'ronsdale_three_staged_browser_v1_20261022.mjs';refs.append(tool)
 preflight=subprocess.run([NODE,'--input-type=module','-e',"import{readFileSync}from'node:fs';import{prepareModelCatalogue}from'./3d-viewer/city/official-model-assets.js';const p=process.argv[1];prepareModelCatalogue(JSON.parse(readFileSync(p)),'http://127.0.0.1:4176/test/catalogue.json');",str(LOCAL/'catalogue.json')],cwd=ROOT,check=True)
 config=dict(stage=str(LOCAL.relative_to(ROOT))+'/',catalogueURL='city/data/official-models/'+BATCH+'/catalogue.json',terrain=terrain,browserUids=uids,failureTestUids=[],fitBox=True,captureDirectionByModel={u:[-.3,.7,-1]for u in uids},retainedBuildingUids=['landsd/256900:0','landsd/307560:0'],jointUids=uids,nativeSupportUidsByModel={'landsd/256898:0':['landsd/233771:0'],'landsd/256702:0':['landsd/233771:0']})
 an='government-xl-ronsdale-three-source-acceptance-v1-20261022';accepted=take(an,BASE/an/'ROOT-PHYSICAL-REVIEW.json');assert accepted['identityAccepted']and accepted['sourceSpecificPhysicalInterpretationAccepted']and accepted['completeNeighbourInterpretationAccepted']
 en='government-xl-ronsdale-canopy-estimate-private-v1-20261022';est=take(en,BASE/en/'estimated-bases.json')['buildings'][0];tile=ROOT/'3d-viewer/city/data/tiles/1_0.json';b=next(x for x in read(tile)['buildings']if x['uid']==est['uid']);assert b['base']==est['previousBase']and b['height']==est['height']and b['baseSource']=='terrain-estimated'and b['heightSource']=='estimated'and b['baseHeightHKPD']is None and b['topHeightHKPD']is None;refs.append(tile)
 config['estimatedBaseUpdates']=[dict(uid=b['uid'],objectId=b['objectId'],buildingCSUID=b['buildingCSUID'],previousBase=b['base'],base=est['proposedBase'],height=b['height'],tile='city/data/tiles/1_0.json',tileSHA256=digest(tile.read_bytes()))]
 for width in [1280,390]:
  assert reservations.owns(lease);cfg={**config,'viewportWidths':[width],'failureTestUids':uids if width==390 else [],'doc':str((DOC/str(width)).relative_to(ROOT))+'/'};p=LOCAL/f'browser-config-{width}.json';save(p,cfg);DOC.mkdir(parents=True,exist_ok=True)
  with(DOC/f'browser-{width}.log').open('w')as log:proc=subprocess.run([NODE,str(tool),'staged',str(p.relative_to(ROOT))],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'},timeout=1200)
  save(DOC/f'command-{width}.json',dict(exitCode=proc.returncode));assert proc.returncode==0
  report=read(DOC/str(width)/'staged-browser.json');assert report['passed']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h
 refs.extend(p for p in LOCAL.rglob('*')if p.is_file()and p.name!='reservation.json')
 r=module('china_staged_browser_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'private-original-desktop-mobile-visual-diagnostic',list(dict.fromkeys(refs)),dict(uids=uids,installationApproved=False,visualAcceptance=False,sourceGeometryChanges=0));print(r['jobId'],flush=True)
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists()and not LOCAL.exists();c=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['building:landsd/256898:0','building:landsd/256702:0','building:landsd/233771:0','building:landsd/256900:0','building:landsd/307560:0'],batch=BATCH,ttl=3600);assert c['ok'];lease=c['reservation'];p=LOCAL/'reservation.json';save(p,json.loads(json.dumps(lease,default=str)))
 try:subprocess.run([sys.executable,str(HERE/'harbourfront_reserved_runner_v1_20261021.py'),str(p),sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
