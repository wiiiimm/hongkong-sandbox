"""Private Evangel stage: unchanged original, qualified changed terrain; no live apply."""
import json,uuid,subprocess,sys,os,shutil,importlib.util
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,reservations,connect
from evangel_college_whole_current_role_bound_20261011 import verify_files,DOCS,UID,ref
from dependency_preflight import from_catalogues
BASE=ROOT/'docs/astra-city/government-import'
ROLE=BASE/'government-xl-evangel-college-91306-whole-current-role-acceptance-v1-20261011'
SOURCE_CERT=BASE/'government-xl-evangel-current-complete-source-root-closure-v1-20261011/root-closed-scope.json'
BATCH='government-xl-evangel-college-91306-unchanged-private-stage-v3-20261011'
DOC=BASE/BATCH;STAGE=HERE/'accepted'/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
BROWSER=HERE/'xl-terrain-recovery-20261010-multi-native-solid-browser-v5.mjs'
PATCH_SHA='af270461066bc5c174bc46222650fa05716b4229316b97847e7958e5948f0f90'
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def recheck(local):
 receipt=read(ROLE/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for pin in receipt['evidenceRefs']:assert ref(ROOT/pin['path'])==pin
 role,entry=verify_files(local);role=json.loads(json.dumps(role));assert role==read(ROLE/'acceptance.json')and entry==read(ROLE/'staged-original-entry.json')
 assert role['acceptanceReadyForStaging']and role['scriptChecksPassed']and role['reasons']==[]and not role['installationApproved']
 closed=read(SOURCE_CERT);assert closed['independentlyVerified']is True and closed['currentManifestSHA256']==role['currentManifest']['sha256']
 rows=read(DOCS['physical']/'selection.json.gz')['rows'];assert len(rows)==1 and rows[0]['uid']==UID
 return role,entry,rows[0]
def owned():
 def owns():assert reservations.owns(read(LEASE))
 def call(cmd):
  subprocess.run(cmd,cwd=ROOT,check=True,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'});owns()
 owns();role,entry,row=recheck(LOCAL/'initial-role-recheck');save(DOC/'typed-role-publication-recheck.json',role)
 assert not entry['supportDependencies']and not entry.get('suppressesBuildingUids')and not entry.get('footprintScope')
 asset=STAGE/entry['asset'];asset.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/row['candidate']['path'],asset);assert ref(asset)['sha256']==entry['sha256']
 catalogue=read(HERE/'local'/DOCS['physical'].name/'catalogue.json');catalogue.update(models=[entry],counts={'packedModels':1},area='Evangel College complete unchanged original and independently qualified changed terrain')
 save(STAGE/'catalogue.json',catalogue);save(STAGE/'catalogue-index.json',dict(models=1,catalogues=['catalogue.json']));save(STAGE/'source-forms.json',[row['source']['building']])
 candidates=read(DOCS['physical']/'terrain-candidates.json');assert len(candidates)==1;c=candidates[0]
 assert c['uids']==[UID]and c['sha256']==PATCH_SHA and c['triangles']==7579 and not c.get('replaces')and not c.get('replacesMany')and ref(ROOT/c['path'])['sha256']==PATCH_SHA
 patch=STAGE/Path(c['path']).name;shutil.copyfile(ROOT/c['path'],patch);assert ref(patch)['sha256']==PATCH_SHA;p=read(patch)
 assert p.get('nativeMesh')and not p.get('patches')and len(p['nativeMesh']['index'])//3==7579
 assert p['meta']['parentTerrain']=='city/data/terrain.json'and p['meta']['parentSha256']==ref(ROOT/'3d-viewer/city/data/terrain.json')['sha256']
 terrain=dict(source=ref(patch)['path'],sha256=PATCH_SHA,destination='city/data/terrain-government-xl-evangel-college-installed-v1-20261011.json',resolution=p['cell'],area=catalogue['area'])
 destination='city/data/official-models/'+BATCH+'/catalogue.json'
 save(STAGE/'plan.json',dict(areas=[dict(area=catalogue['area'],catalogue=ref(STAGE/'catalogue.json')['path'],destination=destination)],topLevelTerrainPatches=[terrain]))
 deps=from_catalogues(ROOT/'3d-viewer/city/data/manifest.json',[STAGE/'catalogue.json']);assert len(deps['rows'])==1 and not deps['rows'][0]['blockers'];save(DOC/'dependencies.json',deps)
 data=read(DOCS['source']/'complete-four-stream-ground-inputs.json.gz');bounds=[]
 for s in data['completeWorldStreams'].values():
  w=np.asarray(s['completeWorldTriangles']);bounds.append([w.min((0,1)),w.max((0,1))])
 capture=[np.min([b[0]for b in bounds]+[entry['worldBounds'][0]],axis=0).tolist(),np.max([b[1]for b in bounds]+[entry['worldBounds'][1]],axis=0).tolist()]
 config=dict(stage=str(STAGE.relative_to(ROOT))+'/',doc=str(DOC.relative_to(ROOT))+'/',catalogueURL=destination,terrain=[terrain],fitBox=True,captureDirectionByModel={UID:[.6,.8,.6]},captureBoundsByModel={UID:capture},browserUids=[UID],failureTestUids=[UID],nativeSupportUidsByModel={UID:[]},mandatoryActualStructuralSupportUidsByModel={UID:[]},retainedOwnCameraOnlyUIDs=[]);save(STAGE/'browser-config.json',config)
 failure=BASE/'government-xl-evangel-college-91306-private-stage-v1-serialization-failure-archive-20261011';diagnosis=BASE/'government-xl-evangel-college-91306-private-stage-v1-serialization-diagnosis-20261011'
 lifecycle=BASE/'government-xl-evangel-college-91306-private-stage-v2-lifecycle-failure-archive-20261011'
 paths=[lifecycle/n for n in ['worker-before-termination.json','exact-lease-cleanup.json','partial-output-census-after-termination.json','reservation-before-cleanup.json','evangel-private-stage-v2-20261011.log','xl-evangel-college-91306-unchanged-private-stage-v2-20261011.py']]+[failure/n for n in ['xl-evangel-college-91306-unchanged-private-stage-v1-20261011.py','evangel-private-stage-v1-20261011.log','failure.json']]+[diagnosis/n for n in ['exact-difference.json','evangel-private-stage-v1-exact-role-diagnosis-20261011.py','evangel-private-stage-v1-exact-role-diagnosis-20261011.log']]+[Path(__file__),SOURCE_CERT,ROLE/'result.json',ROLE/'acceptance.json',ROLE/'staged-original-entry.json',DOCS['physical']/'terrain-candidates.json',ROOT/c['path'],DOC/'typed-role-publication-recheck.json',DOC/'dependencies.json',STAGE/'catalogue.json',STAGE/'catalogue-index.json',STAGE/'source-forms.json',STAGE/'plan.json',STAGE/'browser-config.json',patch,BROWSER];evidence=[ref(q)for q in paths]
 decision=dict(batch=BATCH,uids=[UID],sourceSHA256s={UID:entry['sha256']},manifestSHA256=role['currentManifest']['sha256'],checksPassed=True,publication=False,newlyInstalled=0,modelGeometryChanges=0,terrainProposalGeometryChanged=True,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,evidenceRefs=evidence);save(DOC/'stage.json',decision)
 call([sys.executable,str(HERE.parent/'model-integration-20260909/publish.py'),ref(STAGE/'plan.json')['path'],'--receipt',str(LEASE),'--phase',BATCH])
 call(['node',str(BROWSER),'staged',ref(STAGE/'browser-config.json')['path']]);report=module('evangel_browser_validator',HERE/'integrate.py').browser_verified(DOC/'staged-browser.json',{UID})
 views=[v for v in report['views']if 'time'in v];assert len(views)==4 and {(v['uid'],v['width'],v['time'])for v in views}=={(UID,w,t)for w in [1280,390]for t in ['15:00','22:00']}
 assert {v['uid']for v in report['views']if v.get('fallbackRetained')}=={UID}and not report.get('retainedNativeOwnViews')
 for pin in evidence:assert ref(ROOT/pin['path'])==pin
 final,finalentry,_=recheck(LOCAL/'final-role-recheck');assert final==role and finalentry==entry;owns()
 decision.update(stagedBrowser=ref(DOC/'staged-browser.json'),passed=True,failures=[],livePublicationRequired=True);save(DOC/'acceptance.json',decision);print(json.dumps(dict(stagedBrowserPassed=True,uids=[UID],publication=False,newlyInstalled=0)),flush=True)
def main():
 if '--owned'in sys.argv:
  from publication_lock import locked_publication
  with locked_publication(ROOT):owned()
  return
 assert not DOC.exists()and not STAGE.exists()
 forms=read(BASE/'government-xl-evangel-college-91306-authentic-tin-candidate-input-v1-20261011/complete-protected-current-forms.json.gz')['rows'];assert len(forms)==17 and len({r['building']['uid']for r in forms})==17
 keys=sorted({('building:'if r['building']['uid'].startswith('landsd/')else'foreign-form:')+r['building']['uid']for r in forms}|{'terrain-patch:'+UID})
 claim=reservations.claim('evangel-private-stage-'+str(uuid.uuid4()),keys,batch=BATCH,ttl=3600);assert claim['ok'];save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
 subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
