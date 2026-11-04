"""Private stage of the complete untouched Heya source; no terrain or live write."""
import json,uuid,subprocess,sys,os,shutil,importlib.util
from pathlib import Path
from run import ROOT,HERE,read,save,reservations,connect
from run import digest
from government_owned_identity import verify_files
from heya_aqua_complete_current_role_fixture_20261011 import FOLDERS,load
from heya_aqua_complete_current_role_policy_v2_20261011 import compose,CURRENT,T as UID,P
DOCS={k:ROOT/'docs/astra-city/government-import'/v for k,v in FOLDERS.items()}
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
from dependency_preflight import from_catalogues
BASE=ROOT/'docs/astra-city/government-import';ROLE=BASE/'government-xl-heya-aqua-whole-current-role-acceptance-v2-20261011'
SOURCE_CERT=BASE/'government-xl-heya-aqua-current-complete-source-root-closure-v1-20261011/root-closed-scope.json'
BATCH='government-xl-heya-aqua-184286-unchanged-private-stage-v1-20261011';DOC=BASE/BATCH;STAGE=HERE/'accepted'/BATCH;LEASE=HERE/'local'/BATCH/'reservation.json'
BROWSER=HERE/'xl-terrain-recovery-20261010-multi-native-solid-browser-v5.mjs'
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def recheck(local):
 receipt=read(ROLE/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for pin in receipt['evidenceRefs']:assert ref(ROOT/pin['path'])==pin
 assert digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())==CURRENT
 data=load();row=read(DOCS['identity']/'selection.json.gz')['rows'][0]
 context=read(DOCS['identity']/'context.json.gz')['rows'][0]
 fresh=verify_files(row,context,local/'unmocked-current-owned-identity');assert fresh==data['identity'] and fresh['passed']
 role=json.loads(json.dumps(compose(**data)));assert role==read(ROLE/'complete-current-role.json.gz')
 assert role['stagingReady'] and role['scriptChecksPassed']and role['reasons']==[]and not role['installationApproved']
 entry=read(ROLE/'private-stage-entry.json');expected=json.loads(json.dumps(row['candidate']['entry']))
 support=read(DOCS['identity']/'installed-support-entry.json')
 assert ref(ROOT/support['catalogue']['path'])==support['catalogue'] and ref(ROOT/support['asset']['path'])==support['asset']
 expected['supportDependencies']=[dict(uid=P,buildingCSUID=support['entry']['buildingCSUID'],state='installed',sourceSHA256=support['entry']['sha256'])]
 expected.update(placementReviewed=True,publicationApproved=False,priority='approved-private-stage-only');assert expected==entry
 closed=read(SOURCE_CERT);assert closed['independentlyVerified']is True and closed['currentManifestSHA256']==CURRENT
 assert row['uid']==UID
 return role,entry,row

def owned():
 def owns():assert reservations.owns(read(LEASE))
 def call(cmd):subprocess.run(cmd,cwd=ROOT,check=True,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'});owns()
 owns();role,entry,row=recheck(HERE/'local'/BATCH/'initial-recheck');save(DOC/'typed-role-publication-recheck.json',role)
 assert len(entry['supportDependencies'])==1 and entry['supportDependencies'][0]['uid']==P and not entry.get('suppressesBuildingUids') and not entry.get('footprintScope')
 asset=STAGE/entry['asset'];asset.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/row['candidate']['path'],asset);assert ref(asset)['sha256']==entry['sha256']
 catalogue=read(HERE/'local'/DOCS['physical'].name/'catalogue.json');catalogue.update(models=[entry],counts={'packedModels':1},area='Heya Aqua complete unchanged original; unchanged current terrain')
 save(STAGE/'catalogue.json',catalogue);save(STAGE/'catalogue-index.json',dict(models=1,catalogues=['catalogue.json']));save(STAGE/'source-forms.json',[row['source']['building']])
 destination='city/data/official-models/'+BATCH+'/catalogue.json';save(STAGE/'plan.json',dict(areas=[dict(area=catalogue['area'],catalogue=ref(STAGE/'catalogue.json')['path'],destination=destination)],topLevelTerrainPatches=[]))
 deps=from_catalogues(ROOT/'3d-viewer/city/data/manifest.json',[STAGE/'catalogue.json']);assert len(deps['rows'])==1 and not deps['rows'][0]['blockers'];save(DOC/'dependencies.json',deps)
 data=read(DOCS['actual']/'complete-two-actor-four-stream-ground-inputs.json.gz')['rows'][UID];import numpy as np
 bounds=[]
 for s in data['completeWorldStreams'].values():
  w=np.asarray(s['completeWorldTriangles']);bounds.append([w.min((0,1)),w.max((0,1))])
 capture=[np.min([b[0]for b in bounds]+[entry['worldBounds'][0]],axis=0).tolist(),np.max([b[1]for b in bounds]+[entry['worldBounds'][1]],axis=0).tolist()]
 config=dict(stage=str(STAGE.relative_to(ROOT))+'/',doc=str(DOC.relative_to(ROOT))+'/',catalogueURL=destination,terrain=[],fitBox=True,captureDirectionByModel={UID:[.6,.8,.6]},captureBoundsByModel={UID:capture},browserUids=[UID],failureTestUids=[UID],nativeSupportUidsByModel={UID:[P]},mandatoryActualStructuralSupportUidsByModel={UID:[]},retainedOwnCameraOnlyUIDs=[P]);save(STAGE/'browser-config.json',config)
 paths=[Path(__file__),SOURCE_CERT,ROLE/'result.json',ROLE/'complete-current-role.json.gz',ROLE/'private-stage-entry.json',DOC/'typed-role-publication-recheck.json',DOC/'dependencies.json',STAGE/'catalogue.json',STAGE/'plan.json',STAGE/'browser-config.json',BROWSER];evidence=[ref(p)for p in paths]
 decision=dict(batch=BATCH,uids=[UID],sourceSHA256s={UID:entry['sha256']},manifestSHA256=CURRENT,checksPassed=True,publication=False,newlyInstalled=0,modelGeometryChanges=0,terrainGeometryChanges=0,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,evidenceRefs=evidence);save(DOC/'stage.json',decision)
 call([sys.executable,str(HERE.parent/'model-integration-20260909/publish.py'),ref(STAGE/'plan.json')['path'],'--receipt',str(LEASE),'--phase',BATCH]);call(['node',str(BROWSER),'staged',ref(STAGE/'browser-config.json')['path']]);report=module('heya_browser_validator',HERE/'integrate.py').browser_verified(DOC/'staged-browser.json',{UID})
 views=[v for v in report['views']if 'time'in v];assert len(views)==4 and {(v['uid'],v['width'],v['time'])for v in views}=={(UID,w,t)for w in [1280,390]for t in ['15:00','22:00']}
 retained=report['retainedNativeOwnViews'];assert len(retained)==4 and {(v['uid'],v['width'],v['time'])for v in retained}=={(P,w,t)for w in [1280,390]for t in ['15:00','22:00']}
 support=read(DOCS['identity']/'installed-support-entry.json')['entry']
 assert all(v['sourceSHA256']==support['sha256']and v['originalTriangles']==3844 and v['active']and v['visible']and v['fullyFramed']and v['fallbackFaces']==0 for v in retained)
 assert {v['uid']for v in report['views']if v.get('fallbackRetained')}=={UID}
 for pin in evidence:assert ref(ROOT/pin['path'])==pin
 final,finalentry,_=recheck(HERE/'local'/BATCH/'final-recheck');assert final==role and finalentry==entry;decision.update(stagedBrowser=ref(DOC/'staged-browser.json'),passed=True,failures=[],livePublicationRequired=True);save(DOC/'acceptance.json',decision);print(json.dumps(dict(stagedBrowserPassed=True,uids=[UID],publication=False,newlyInstalled=0)),flush=True)
def main():
 if '--owned'in sys.argv:
  from publication_lock import locked_publication
  with locked_publication(ROOT):owned()
  return
 assert not DOC.exists()and not STAGE.exists();forms=read(DOCS['actual']/'capture-inputs.json.gz')['completeCurrentForms'];keys=sorted({'building:'+b['uid']for b in forms}|{'building:'+UID})
 claim=reservations.claim('heya-private-stage-'+str(uuid.uuid4()),keys,batch=BATCH,ttl=3600);assert claim['ok'];save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
