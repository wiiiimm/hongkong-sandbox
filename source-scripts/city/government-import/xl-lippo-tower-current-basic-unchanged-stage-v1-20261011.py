"""DRAFT stage: unchanged Lippo Tower, unchanged terrain and visible BASIC carrier.
Only preparation/browser routing is performed; live publication is root-owned.
"""
import importlib.util,json,os,subprocess,sys,shutil,uuid
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from dependency_preflight import from_catalogues
import lippo_tower_current_basic_complete_role_current_bound_v2_20261011 as bound
BATCH='government-xl-lippo-tower-current-basic-unchanged-stage-v1-20261011';DOC=bound.BASE/BATCH;STAGE=HERE/'accepted'/BATCH
LEASE=HERE/'local'/BATCH/'install-reservation.json';ROLE=bound.BASE/'government-xl-lippo-tower-only-current-complete-role-acceptance-v2-20261011'
BROWSER=HERE/'xl-lippo-current-basic-solid-browser-v1-20261011.mjs';UID='landsd/239465:0';CARRIER='landsd/231645:0';RETAINED=['landsd/21915:0']
def ref(p):return dict(path=str(Path(p).relative_to(ROOT)),sha256=digest(Path(p).read_bytes()))
def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def recheck(local):
 receipt=read(ROLE/'result.json');bound.receipt_pins(receipt)
 with connect() as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 role,entry=bound.verify_files(local)
 saved=read(ROLE/'acceptance.json')
 # Additional separately executed support/budget/loader fields are pinned by
 # the receipt; the whole mathematical/current role must replay exactly.
 assert {k:saved[k] for k in role}==role and role['reasons']==[] and role['scriptChecksPassed'] and role['acceptanceReadyForStaging']
 assert role['installationApproved'] is False and role['wholeBasicReaccepted'] is False and role['originalGovernmentPodiumUsedAsRuntimeSupport'] is False
 assert entry==read(ROLE/'staged-entry.json')
 report=read(ROLE/'production-support-budget-loader.json');assert report['checksPassed']==19 and report['ordinaryBudgetLimitsUnchanged'] and report['currentManifest']==role['currentManifest']
 return role,entry
def retained_snapshot():
 result={}
 for url in read(ROOT/'3d-viewer/city/data/manifest.json')['officialModelCatalogues']:
  p=ROOT/'3d-viewer'/url
  for e in read(p)['models']:
   if e['uid'] in RETAINED:
    assert e['uid'] not in result;asset=p.parent/e['asset'];assert digest(asset.read_bytes())==e['sha256'];result[e['uid']]=dict(entry=e,asset=ref(asset),catalogue=ref(p))
 assert set(result)==set(RETAINED);return result
def owned():
 def owns():assert reservations.owns(read(LEASE))
 def call(cmd):subprocess.run(cmd,cwd=ROOT,check=True,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'});owns()
 owns();retained_before=retained_snapshot();role,entry=recheck(HERE/'local'/BATCH/'first-role-replay')
 inp=read(bound.INPUT/'input.json.gz');geo=read(bound.INPUT/'complete-current-geometry.json.gz');row=inp['rows'][0]
 assert row['uid']==UID and row['candidate']['entry']['sha256']==entry['sha256']
 asset=STAGE/entry['asset'];asset.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/row['candidate']['path'],asset);assert ref(asset)['sha256']==entry['sha256']
 catalogue=read(HERE/'local'/ROLE.name/'catalogue.json');assert catalogue['models']==[entry];save(STAGE/'catalogue.json',catalogue);save(STAGE/'catalogue-index.json',dict(models=1,catalogues=['catalogue.json']));save(STAGE/'source-forms.json',[row['source']['building']])
 destination='city/data/official-models/'+BATCH+'/catalogue.json';save(STAGE/'plan.json',dict(areas=[dict(area=catalogue['area'],catalogue=ref(STAGE/'catalogue.json')['path'],destination=destination)],topLevelTerrainPatches=[]))
 deps=from_catalogues(ROOT/'3d-viewer/city/data/manifest.json',[STAGE/'catalogue.json']);assert len(deps['rows'])==1 and not deps['rows'][0]['blockers'];save(DOC/'dependencies.json',deps)
 carrier=next(r for r in geo['completeCurrentBasicGeometry'] if r['uid']==CARRIER);p=np.asarray(carrier['position'],dtype='<f8').reshape(-1,3);ix=np.asarray(carrier['index'],dtype=np.int64).reshape(-1,3)
 expected=dict(uid=CARRIER,csuid=carrier['currentForm']['buildingCSUID'],completeTriangles=p[ix].reshape(-1,9).tolist())
 assert len(expected['completeTriangles'])==284
 sep=read(bound.SEPARATION/'diagnostic.json.gz');boxes=list(sep['completeOwnedWorldBounds'].values());lo=np.asarray([b[0] for b in boxes]).min(0).tolist();hi=np.asarray([b[1] for b in boxes]).max(0).tolist()
 config=dict(stage=str(STAGE.relative_to(ROOT))+'/',doc=str(DOC.relative_to(ROOT))+'/',catalogueURL=destination,terrain=[],fitBox=True,browserUids=[UID],failureTestUids=[UID],captureDirectionByModel={UID:[.6,.8,.6]},captureBoundsByModel={UID:[lo,hi]},retainedBuildingUidsByModel={UID:[CARRIER]},basicCarrierWitnessByModel={UID:expected},nativeSupportUidsByModel={UID:RETAINED},mandatoryActualStructuralSupportUidsByModel={UID:[]},retainedOwnCameraOnlyUIDs=RETAINED)
 save(STAGE/'browser-config.json',config);save(DOC/'typed-role-publication-recheck.json',role);save(DOC/'retained-native-before-stage.json',retained_before)
 paths=[Path(__file__),BROWSER,HERE/'lippo_current_basic_drawn_carrier_witness_v1_20261011.mjs',ROLE/'result.json',ROLE/'acceptance.json',ROLE/'production-support-budget-loader.json',DOC/'typed-role-publication-recheck.json',DOC/'retained-native-before-stage.json',DOC/'dependencies.json',STAGE/'catalogue.json',STAGE/'plan.json',STAGE/'browser-config.json'];evidence=[ref(p) for p in paths]
 decision=dict(batch=BATCH,uids=[UID],currentManifest=role['currentManifest'],publication=False,newlyInstalled=0,sourceGeometryChanges=0,terrainGeometryChanges=0,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,wholeBasicReaccepted=False,retainedNativeReaccepted=False,evidenceRefs=evidence)
 save(DOC/'stage.json',decision)
 call([sys.executable,str(HERE.parent/'model-integration-20260909/publish.py'),ref(STAGE/'plan.json')['path'],'--receipt',str(LEASE),'--phase',BATCH])
 call(['node',str(BROWSER),'staged',ref(STAGE/'browser-config.json')['path']])
 report=module('lippo_actual_stage_browser_validator',HERE/'integrate.py').browser_verified(DOC/'staged-browser.json',{UID});views=[r for r in report['views'] if 'time' in r]
 assert len(views)==4 and {(r['uid'],r['width'],r['time']) for r in views}=={(UID,w,t) for w in [1280,390] for t in ['15:00','22:00']}
 assert all(r['actualBasicCarrier']['completeDrawnFaces']==284 and r['actualBasicCarrier']['exactCurrentBasicGeometryVisible'] and r['actualBasicCarrier']['productionSupportAvailable'] and r['actualBasicCarrier']['wholeBasicReaccepted'] is False for r in views)
 own=report['retainedNativeOwnViews'];assert len(own)==4 and all(r['uid']=='landsd/21915:0' and r['active'] and r['visible'] and r['fullyFramed'] for r in own)
 assert {r['uid'] for r in report['views'] if r.get('fallbackRetained')}=={UID}
 for r in evidence:assert ref(ROOT/r['path'])==r
 final,final_entry=recheck(HERE/'local'/BATCH/'final-role-replay');assert final==role and final_entry==entry and retained_snapshot()==retained_before
 decision.update(passed=True,failures=[],stagedBrowser=ref(DOC/'staged-browser.json'),livePublicationRequired=True);save(DOC/'acceptance.json',decision);print(dict(stagedBrowserPassed=True,uids=[UID],publication=False),flush=True)
def main():
 if '--owned' in sys.argv:
  from publication_lock import locked_publication
  with locked_publication(ROOT):owned()
  return
 assert not DOC.exists() and not STAGE.exists();inp=read(bound.INPUT/'input.json.gz');keys={'building:'+r['building']['uid'] for r in inp['completeCurrentForms']}
 claim=reservations.claim('lippo-basic-unchanged-stage-'+str(uuid.uuid4()),sorted(keys),batch=BATCH,ttl=3600);assert claim['ok'];save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
 subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
