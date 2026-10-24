"""Private exact three-tower/installed-podium preview; all approvals stay false."""
import copy,os,subprocess,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations,connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';P='government-xl-parc-palais-three-';BATCH=P+'recovered-assembly-preview-v2-20261024'
SOURCES={'landsd/238669:0':'ff0f3b80ffb448a3c2a800e723dcd905b71bef82d68ebd527fe5347e0ccc1bb0','landsd/238671:0':'e5cb9cd513a1fb3882a9f21e07d7b1ba8a151a360d9c996fd2fb5349ca7253d4','landsd/238856:0':'e9d01d1a9b88d9ee1494ef64997ed633e1bfc574344a666e23cae4f5904319ef'}
PARENT='landsd/266063:0';INVENTORY='government-xl-after-harbour-metropolis-current-inventory-v1-20261024'
def main():
 out=BASE/BATCH;local=HERE/'local'/BATCH;assert not out.exists()and not local.exists();refs=[Path(__file__)];pins={}
 def take(batch,path):
  if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
  assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 prior_name=P+'unapproved-supported-preview-v1-20261024';prior=take(prior_name,BASE/prior_name/'result.json');assert prior['previewOnly']and prior['sourceSHA256ByUid']==SOURCES and not prior['installationApproved']
 runtime=P+'runtime-v1-20261024';selection=take(runtime,BASE/runtime/'selection.json.gz');assert{r['uid']:r['sourceSHA256']for r in selection['rows']}==SOURCES
 scopeName=P+'model-scope-v1-20261024';scope=take(scopeName,BASE/scopeName/'summary.json');inventory=take(INVENTORY,BASE/INVENTORY/'complete-bounds.json.gz')
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256']==scope['currentManifestSHA256']==pins[INVENTORY][str(manifest.relative_to(ROOT))];refs.append(manifest)
 installed={}
 for url in read(manifest)['officialModelCatalogues']:
  path=ROOT/'3d-viewer'/url;assert digest(path.read_bytes())==pins[INVENTORY][str(path.relative_to(ROOT))];refs.append(path)
  for e in read(path)['models']:assert e['uid']not in installed;installed[e['uid']]=e
 assert len(installed)==len(inventory['rows'])==6896 and not set(SOURCES)&set(installed);parent=installed[PARENT]
 assert parent['sha256']==next(r['sourceSHA256']for r in inventory['rows']if r['uid']==PARENT)
 for r in scope['rows']:
  assert r['currentNativeActorsChecked']==len(installed)and r['sourceSHA256']==SOURCES[r['uid']]
  assert len(r['nearbyNativeActors'])==1 and r['nearbyNativeActors'][0]['uid']==PARENT and r['nearbyNativeActors'][0]['sourceSHA256']==parent['sha256']
  uid=r['uid'];name=P+uid.split('/')[1].replace(':','-')+'-support-v1-20261024';proof=take(name,BASE/name/'summary.json')
  assert proof['supportedUid']==uid and proof['installedSupportUid']==PARENT and proof['currentManifestSHA256']==selection['manifestSHA256']
  assert{r['mode']for r in proof['rows']}=={'original','literal','leftF32','balancedF32'}and all(r['unresolved']==r['finitePaths']for r in proof['rows'])
 entries=[];provenance=[]
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  for row in selection['rows']:
   uid=row['uid'];native=row['native'];sheet,sha=db.execute('SELECT i.sheet,r.result_sha FROM astra_modelling.native_stage_inputs i JOIN astra_modelling.native_stage_results r USING(cache_key) WHERE i.cache_key=%s',(native['cacheKey'],)).fetchone();assert sha==native['resultSha']
   tile=ROOT/'3d-viewer'/row['source']['tile'];assert digest(tile.read_bytes())==row['source']['tileSHA256']and next(f for f in read(tile)['buildings']if f['uid']==uid)==row['source']['building'];refs.append(tile)
   asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==SOURCES[uid];refs.append(asset);e=copy.deepcopy(row['candidate']['entry'])
   assert e['sha256']==SOURCES[uid]and e['rootTranslation']==[-834500,0,816500]and e.get('verticalPlacementOffsetHKPD',0)==0
   assert not any(e.get(k)for k in ['supportDependencies','retainedBasicSupportDependencies','suppressesBuildingUids','sourceWorldBounds','partialSource','embeddedModel','embeddedModels'])
   if'sourceTile'in e:assert e['sourceTile']==sheet
   e.update(asset='assets/'+SOURCES[uid]+'.glb.gz',sourceTile=sheet,priority='landmark',proceduralWindows=False,publicationApproved=False,placementReviewed=False,identityReviewApproved=False,sourceIdentityReviewed=False,supportDependencies=[dict(uid=PARENT,state='installed',buildingCSUID=parent['buildingCSUID'],sha256=parent['sha256'])]);entries.append(e);provenance.append(dict(uid=uid,sourceTile=sheet,cacheKey=native['cacheKey'],nativeResultSHA256=sha))
 resources=['building:'+u for u in sorted([*SOURCES,PARENT])];claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  for row in selection['rows']:
   path=local/'assets'/(SOURCES[row['uid']]+'.glb.gz');path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes((ROOT/row['candidate']['path']).read_bytes())
  save(local/'catalogue.json',dict(schemaVersion=1,kind='staged-official-model-catalogue',datasetId='landsd_rcd_1742809441342_98380',crs='EPSG:2326',verticalDatum='Hong Kong Principal Datum',rootTranslation=[-834500,0,816500],models=entries,counts=dict(packedModels=3)));save(local/'catalogue-index.json',dict(models=3,catalogues=['catalogue.json']));save(local/'source-tile-provenance.json',provenance);save(local/'source-forms.json',[r['source']['building']for r in selection['rows']]);save(local/'validation-forms.json',{r['uid']:r['source']for r in selection['rows']})
  config=dict(stage=str(local.relative_to(ROOT))+'/',catalogueURL='city/data/official-models/'+BATCH+'/catalogue.json',terrain=[],browserUids=list(SOURCES),fitBox=True,captureDirectionByModel={u:[1,1.8,-1]for u in SOURCES},retainedCaptureDirectionByModel={PARENT:[1,3,-1]},retainedBuildingUids=[],additionalRetainedUids=[PARENT],jointUids=list(SOURCES),nativeSupportUidsByModel={u:[PARENT]for u in SOURCES});tool=HERE/'ronsdale_three_live_browser_v9_20261024.mjs';refs.append(tool);cfg=local/'preflight-config.json';save(cfg,dict(**config,doc=str(out.relative_to(ROOT))+'/'));subprocess.run(['node',str(tool),'preflight',str(cfg.relative_to(ROOT))],cwd=ROOT,check=True)
  for width in [1280,390]:
   assert reservations.owns(lease)and reservations.heartbeat(lease)['ok'];cfg=local/('browser-config-'+str(width)+'.json');save(cfg,dict(**config,viewportWidths=[width],failureTestUids=[],doc=str((out/str(width)).relative_to(ROOT))+'/'));out.mkdir(parents=True,exist_ok=True)
   with(out/('browser-'+str(width)+'.log')).open('w')as log:code=subprocess.run(['node',str(tool),'staged',str(cfg.relative_to(ROOT))],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,timeout=1800,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'}).returncode
   save(out/('command-'+str(width)+'.json'),dict(exitCode=code));assert code==0;report=read(out/str(width)/'staged-browser.json');assert report['passed']and not report['errors'];assert len([v for v in report['views']if'time'in v])==6;old=report.get('retainedNativeOwnViews',[]);assert len(old)==2 and all(r['uid']==PARENT and r['sourceSHA256']==parent['sha256']for r in old)
  assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.extend(p for p in local.rglob('*')if p.is_file());result=dict(uids=list(SOURCES),sourceSHA256ByUid=SOURCES,retainedNativeUids=[PARENT],proposedInstalledSupportUid=PARENT,proposedInstalledSupportSHA256=parent['sha256'],currentNativeActors=len(installed),previewOnly=True,physicalAcceptance=False,identityAccepted=False,visualAcceptance=False,installationApproved=False,sourceGeometryChanges=0,sourcePoseChanges=0,terrainEdits=False,qualification='Recovered-assembly view run with all three sources available before every own export. Independent per-source failed-download/retry evidence is pinned from the original preview run; this second view-only run does not substitute for it. Unchanged installed podium and all approval flagsfalse. Complete source/retained exports, recovery and joint activation remain subject to actual inspection. No production source, support, identity or publication metadata changed.')
  module('parc_three_private_preview_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'unapproved-three-original-and-complete-scoped-installed-support-preview',refs,result)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
