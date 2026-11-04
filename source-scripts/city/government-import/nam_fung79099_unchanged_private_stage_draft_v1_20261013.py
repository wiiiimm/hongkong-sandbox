"""ROOT-run only: unchanged Nam private stage, real retained BASIC availability."""
import argparse,json,os,shutil,subprocess,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect,reservations
import nam_fung79099_current_install_qualification_receipt_recovery_draft_v1_20261012 as R
from dependency_preflight import from_catalogues
BATCH='government-xl-nam-fung79099-unchanged-private-stage-v1-20261013';DOC=R.Q.B/BATCH;STAGE=HERE/'accepted'/BATCH;LEASE=HERE/'local'/BATCH/'reservation.json';PROPOSAL=R.Q.B/'government-xl-nam-fung79099-unchanged-private-stage-proposal-v1-20261013';BROWSER=HERE/'nam_fung79099_private_stage_actual_basic_browser_draft_v1_20261013.mjs'
UID=R.Q.UID;P=R.Q.CARRIER

def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def recheck(a):
 pins=read(PROPOSAL/'executable-pins.json');assert ref(Path(__file__))==pins['caller']
 for e in pins['inputs']:assert ref(ROOT/e['path'])==e
 _,data,_,outcome=R.inputs();receipt=read(R.DOC/'result.json');assert ref(R.DOC/'result.json')['sha256']==a.expected_result_sha and receipt['acceptanceReadyForStaging']and receipt['scriptChecksPassed']and not receipt['installationApproved']
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for e in receipt['evidenceRefs']:assert ref(ROOT/e['path'])==e
 cert=ROOT/a.source_certificate;assert ref(cert)['sha256']==a.expected_source_certificate_sha and isinstance(read(cert),dict)and read(cert)
 entry=read(R.Q.DOC/'proposed-staged-entry.json');assert entry['sha256']==R.Q.Q.SOURCE and entry['triangles']==13061 and entry['supportDependencies']==[R.Q.DEPENDENCY]and entry['publicationApproved']and entry['sourceIdentityReviewed']and not entry['proceduralWindows']and not entry.get('suppressesBuildingUids')and not entry.get('footprintScope')and not entry.get('verticalPlacementOffsetHKPD')
 row=read(R.Q.DOC/'selection.json.gz')['rows'][0];assert row['candidate']['entry']['worldBounds']==entry['worldBounds']and entry['rootTranslation']==[-834500,0,816500];assert ref(ROOT/row['candidate']['path'])['sha256']==entry['sha256'];assert outcome['acceptanceReadyForStaging']and not outcome['remainingActualBlockers']
 forms=read(R.Q.Q.CAP/'complete-current-forms.json.gz')['rows'];carrier=next(r['building']for r in forms if r['building']['uid']==P);assert carrier['buildingCSUID']==R.Q.DEPENDENCY['csuid']and carrier['tile']=='1_-1';assert len(forms)==15
 return receipt,outcome,entry,row,data[6],carrier,cert

def owned(a):
 receipt,outcome,entry,row,before,carrier,cert=recheck(a);lease=read(LEASE);assert reservations.owns(lease)
 def call(cmd):
  assert reservations.owns(lease);assert reservations.heartbeat(lease)['ok'];subprocess.run(cmd,cwd=ROOT,check=True,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'});assert reservations.owns(lease);recheck(a)
 asset=STAGE/entry['asset'];asset.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/row['candidate']['path'],asset);assert ref(asset)['sha256']==entry['sha256']
 catalogue=read(R.Q.LOCAL/'catalogue.json');catalogue.update(area='Nam Fung unchanged original tower; actual BASIC45779 fallback; unchanged terrain',kind='staged-official-model-catalogue',models=[entry],counts=dict(packedModels=1));save(STAGE/'catalogue.json',catalogue);save(STAGE/'catalogue-index.json',dict(models=1,catalogues=['catalogue.json']));save(STAGE/'source-forms.json',[row['source']['building']])
 destination='city/data/official-models/'+BATCH+'/catalogue.json';save(STAGE/'plan.json',dict(areas=[dict(area=catalogue['area'],catalogue=ref(STAGE/'catalogue.json')['path'],destination=destination)],topLevelTerrainPatches=[]));deps=from_catalogues(ROOT/'3d-viewer/city/data/manifest.json',[STAGE/'catalogue.json']);assert len(deps['rows'])==1 and not deps['rows'][0]['blockers'];save(DOC/'dependencies.json',deps)
 complete=read(R.Q.Q.CAP/'actual-render-geometry.json.gz')['rows'][0];bounds=[entry['worldBounds']]+[complete[k]for k in ['completeLiteralWorldBounds','completeExplicitLeftAssociatedFloat32ModelMatrixWorldBounds','completeExplicitBalancedFloat32ModelMatrixWorldBounds']];capture=[[min(b[0][k]for b in bounds)for k in range(3)],[max(b[1][k]for b in bounds)for k in range(3)]]
 config=dict(stage=str(STAGE.relative_to(ROOT))+'/',doc=str(DOC.relative_to(ROOT))+'/',catalogueURL=destination,terrain=[],fitBox=True,captureDirectionByModel={UID:[.6,.8,.6]},captureBoundsByModel={UID:capture},browserUids=[UID],failureTestUids=[UID],nativeSupportUidsByModel={UID:[]},mandatoryActualStructuralSupportUidsByModel={UID:[]},retainedBuildingUidsByModel={UID:[P]},namExactBasicSupport=dict(uid=P,csuid=carrier['buildingCSUID'],sourceForm=carrier));save(STAGE/'browser-config.json',config)
 save(DOC/'stage.json',dict(batch=BATCH,uids=[UID],currentManifest=outcome['currentManifest'],currentNativeCount=6649,completeQualificationReceipt=ref(R.DOC/'result.json'),sourceClosureCertificate=ref(cert),sourceGeometryChanges=0,terrainGeometryChanges=0,installationApproved=False,publication=False,newlyInstalled=0,basicCarrierNotNative=True))
 call([sys.executable,str(HERE.parent/'model-integration-20260909/publish.py'),ref(STAGE/'plan.json')['path'],'--receipt',str(LEASE),'--phase',BATCH]);call(['node',str(BROWSER),'staged',ref(STAGE/'browser-config.json')['path']]);report=R.Q.Q.module(HERE/'integrate.py','nam_stage_browser_validation').browser_verified(DOC/'staged-browser.json',{UID});views=[v for v in report['views']if 'time'in v];assert len(views)==4 and {(v['uid'],v['width'],v['time'])for v in views}=={(UID,w,t)for w in [1280,390]for t in ['15:00','22:00']}
 for v in views:
  s=v['namBasicSupport'];assert s['actualSupportAvailable']and s['tileWanted']and s['fallbackFaces']==432 and s['sourceForm']==carrier and not s['detailedActive'];assert s['buildingCSUID']==carrier['buildingCSUID']and s['tile']==carrier['tile'];assert v['retained'][P]['loaded']and not v['retained'][P]['detailedActive']and not v['retained'][P]['hidden']
 assert {v['uid']for v in report['views']if v.get('fallbackRetained')}=={UID};recheck(a);save(DOC/'acceptance.json',dict(batch=BATCH,uids=[UID],passed=True,failures=[],stagedBrowser=ref(DOC/'staged-browser.json'),completeQualificationReceipt=ref(R.DOC/'result.json'),sourceClosureCertificate=ref(cert),publication=False,newlyInstalled=0,sourceGeometryChanges=0,terrainGeometryChanges=0,basicCarrierNotNative=True,governmentPodiumInstalled=False,livePublicationRequired=True));print(json.dumps(dict(stagedBrowserPassed=True,uids=[UID],publication=False,newlyInstalled=0)))

def main():
 p=argparse.ArgumentParser();p.add_argument('--expected-result-sha',required=True);p.add_argument('--source-certificate',required=True);p.add_argument('--expected-source-certificate-sha',required=True);p.add_argument('--preflight-only',action='store_true');p.add_argument('--owned',action='store_true');a=p.parse_args();_,_,_,_,before,_,_=recheck(a)
 if a.preflight_only:print(json.dumps(dict(stageReadOnlyPreflightPassed=True,noWorker=True)));return
 if a.owned:
  from publication_lock import locked_publication
  with locked_publication(ROOT):owned(a)
  return
 assert not DOC.exists()and not STAGE.exists();claim=reservations.claim('nam-private-stage-'+str(uuid.uuid4()),['building:'+u for u in before['uids']],batch=BATCH,ttl=3600);assert claim['ok'];save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,*sys.argv[1:],'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
