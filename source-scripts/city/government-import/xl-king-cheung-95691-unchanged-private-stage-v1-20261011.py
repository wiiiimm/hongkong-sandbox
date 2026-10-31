"""Private stage of the complete untouched King source; no terrain or live write."""
import json,uuid,subprocess,sys,os,shutil,importlib.util
from pathlib import Path
from run import ROOT,HERE,read,save,reservations,connect
from king_cheung_whole_current_role_bound_v2_20261011 import verify_files,DOCS,UID,ref
from dependency_preflight import from_catalogues
BASE=ROOT/'docs/astra-city/government-import';ROLE=BASE/'government-xl-king-cheung-95691-whole-current-role-acceptance-v3-20261011'
SOURCE_CERT=BASE/'government-xl-king-cheung-current-complete-source-root-closure-v1-20261011/root-closed-scope.json'
BATCH='government-xl-king-cheung-95691-unchanged-private-stage-v1-20261011';DOC=BASE/BATCH;STAGE=HERE/'accepted'/BATCH;LEASE=HERE/'local'/BATCH/'reservation.json'
BROWSER=HERE/'xl-terrain-recovery-20261010-multi-native-solid-browser-v5.mjs'
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def recheck():
 receipt=read(ROLE/'result.json')
 with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for pin in receipt['evidenceRefs']:assert ref(ROOT/pin['path'])==pin
 role,entry=verify_files();assert role==read(ROLE/'acceptance.json') and entry==read(ROLE/'staged-original-entry.json')
 assert role['acceptanceReadyForStaging'] and role['scriptChecksPassed'] and role['reasons']==[] and not role['installationApproved']
 closed=read(SOURCE_CERT);assert closed['independentlyVerified'] is True and closed['currentManifestSHA256']==role['currentManifest']['sha256']
 row=read(DOCS['identity']/'selection.json.gz')['rows'][0];assert row['uid']==UID
 return role,entry,row

def owned():
 def owns():assert reservations.owns(read(LEASE))
 def call(cmd):subprocess.run(cmd,cwd=ROOT,check=True,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'});owns()
 owns();role,entry,row=recheck();save(DOC/'typed-role-publication-recheck.json',role)
 assert not entry['supportDependencies'] and not entry.get('suppressesBuildingUids') and not entry.get('footprintScope')
 asset=STAGE/entry['asset'];asset.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/row['candidate']['path'],asset);assert ref(asset)['sha256']==entry['sha256']
 catalogue=read(HERE/'local'/DOCS['physical'].name/'catalogue.json');catalogue.update(models=[entry],counts={'packedModels':1},area='King Cheung complete unchanged original; unchanged current terrain')
 save(STAGE/'catalogue.json',catalogue);save(STAGE/'catalogue-index.json',dict(models=1,catalogues=['catalogue.json']));save(STAGE/'source-forms.json',[row['source']['building']])
 destination='city/data/official-models/'+BATCH+'/catalogue.json';save(STAGE/'plan.json',dict(areas=[dict(area=catalogue['area'],catalogue=ref(STAGE/'catalogue.json')['path'],destination=destination)],topLevelTerrainPatches=[]))
 deps=from_catalogues(ROOT/'3d-viewer/city/data/manifest.json',[STAGE/'catalogue.json']);assert len(deps['rows'])==1 and not deps['rows'][0]['blockers'];save(DOC/'dependencies.json',deps)
 data=read(DOCS['input']/'complete-four-stream-ground-inputs.json.gz');import numpy as np
 bounds=[]
 for s in data['completeWorldStreams'].values():
  w=np.asarray(s['completeWorldTriangles']);bounds.append([w.min((0,1)),w.max((0,1))])
 capture=[np.min([b[0]for b in bounds]+[entry['worldBounds'][0]],axis=0).tolist(),np.max([b[1]for b in bounds]+[entry['worldBounds'][1]],axis=0).tolist()]
 config=dict(stage=str(STAGE.relative_to(ROOT))+'/',doc=str(DOC.relative_to(ROOT))+'/',catalogueURL=destination,terrain=[],fitBox=True,captureDirectionByModel={UID:[.6,.8,.6]},captureBoundsByModel={UID:capture},browserUids=[UID],failureTestUids=[UID],nativeSupportUidsByModel={UID:[]},mandatoryActualStructuralSupportUidsByModel={UID:[]},retainedOwnCameraOnlyUIDs=[]);save(STAGE/'browser-config.json',config)
 paths=[Path(__file__),SOURCE_CERT,ROLE/'result.json',ROLE/'acceptance.json',ROLE/'staged-original-entry.json',DOC/'typed-role-publication-recheck.json',DOC/'dependencies.json',STAGE/'catalogue.json',STAGE/'plan.json',STAGE/'browser-config.json',BROWSER];evidence=[ref(p)for p in paths]
 decision=dict(batch=BATCH,uids=[UID],sourceSHA256s={UID:entry['sha256']},manifestSHA256=role['currentManifest']['sha256'],checksPassed=True,publication=False,newlyInstalled=0,modelGeometryChanges=0,terrainGeometryChanges=0,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,evidenceRefs=evidence);save(DOC/'stage.json',decision)
 call([sys.executable,str(HERE.parent/'model-integration-20260909/publish.py'),ref(STAGE/'plan.json')['path'],'--receipt',str(LEASE),'--phase',BATCH]);call(['node',str(BROWSER),'staged',ref(STAGE/'browser-config.json')['path']]);report=module('king_browser_validator',HERE/'integrate.py').browser_verified(DOC/'staged-browser.json',{UID})
 views=[v for v in report['views']if 'time'in v];assert len(views)==4 and {(v['uid'],v['width'],v['time'])for v in views}=={(UID,w,t)for w in [1280,390]for t in ['15:00','22:00']}
 assert {v['uid']for v in report['views']if v.get('fallbackRetained')}=={UID}
 for pin in evidence:assert ref(ROOT/pin['path'])==pin
 final,finalentry,_=recheck();assert final==role and finalentry==entry;decision.update(stagedBrowser=ref(DOC/'staged-browser.json'),passed=True,failures=[],livePublicationRequired=True);save(DOC/'acceptance.json',decision);print(json.dumps(dict(stagedBrowserPassed=True,uids=[UID],publication=False,newlyInstalled=0)),flush=True)
def main():
 if '--owned'in sys.argv:
  from publication_lock import locked_publication
  with locked_publication(ROOT):owned()
  return
 assert not DOC.exists()and not STAGE.exists();forms=read(DOCS['input']/'complete-current-actual-source-and-ground.json.gz')['completeCurrentForms'];keys=sorted({'building:'+b['uid']for b in forms}|{'building:'+UID})
 claim=reservations.claim('king-private-stage-'+str(uuid.uuid4()),keys,batch=BATCH,ttl=3600);assert claim['ok'];save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
