"""Reuse completed retained exports only under exact public/runtime replay bindings."""
from pathlib import Path
import copy,shutil
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
P='government-xl-west-kowloon-north-pair-after-ocean-';BASE=ROOT/'docs/astra-city/government-import';OLD=P+'original-installed-v2-20261028';ARCHIVE=P+'completed-v2-browser-evidence-v1-20261028'
def assert_exact_hash_map(expected,actual):
 assert expected and set(expected)==set(actual),'Incomplete exact public replay'
 assert all(actual[k]==v for k,v in expected.items()),'Public replay bytes differ'

def archive_refs():
 receipt,pins=authenticate(BASE/ARCHIVE);assert receipt['missingJointViews']and receipt['completedRetainedExports']==268 and not receipt['installationApproved']
 for path,sha in pins.items():assert digest((ROOT/path).read_bytes())==sha,path
 return [BASE/ARCHIVE/'result.json',Path(__file__)]

def verify_republished_inputs():
 archive_refs();oldplan=read(ROOT/'docs/astra-city/model-integration-20260909'/OLD/'publication-plan.json');expected=oldplan['after'];assert all(k.startswith('3d-viewer/')for k in expected);actual={k:digest((ROOT/k).read_bytes())for k in expected};assert_exact_hash_map(expected,actual)
 history=read(BASE/OLD/'historical-input-context.json');count=0
 for ref in history['originalEvidenceRefs']:
  path=ref['path']
  if path.startswith('3d-viewer/')and path not in expected:assert digest((ROOT/path).read_bytes())==ref['sha256'],path;count+=1
 return dict(publicFiles=expected,unchangedRecordedViewerInputs=count,archiveResult=str((BASE/ARCHIVE/'result.json').relative_to(ROOT)))

def joint_config(cfg,sources):
 cfg=copy.deepcopy(cfg);cfg.update(additionalRetainedUids=[],nativeSupportUidsByModel={},failureTestUids=[],jointUids=sorted(sources),fitJointCamera=True,fitJointCameraMobile=True)
 return cfg

def combine(width,fresh,out):
 binding=verify_republished_inputs();assert fresh['passed']and not fresh['errors'];assert len([v for v in fresh['views']if 'time'in v])==4 and len(fresh.get('jointViews',[]))>=2
 olddir=BASE/OLD/('viewport-'+str(width));old=read(olddir/'live-browser.json');assert old['passed']and not old['errors']and len(old['retainedNativeOwnViews'])==134;assert not old.get('jointViews');assert len([v for v in old['views']if 'time'in v])==4
 assert {(v['uid'],v['width'],v['time'])for v in fresh['views']if 'time'in v}=={(uid,width,time)for uid in ['landsd/182397:0','landsd/309340:0']for time in ['15:00','22:00']}
 assert not fresh.get('retainedNativeOwnViews');part=copy.deepcopy(fresh);part['retainedNativeOwnViews']=copy.deepcopy(old['retainedNativeOwnViews'])
 for item in part['retainedNativeOwnViews']:
  src=olddir/item['file'];dest=out/item['file'];assert src.exists()and not dest.exists();dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dest);assert digest(dest.read_bytes())==digest(src.read_bytes())
 part['reusedRetainedEvidence']=dict(viewport=width,originalReport=dict(path=str((olddir/'live-browser.json').relative_to(ROOT)),sha256=digest((olddir/'live-browser.json').read_bytes())),exports=134,exactCurrentReplay=binding,freshSourceAndJointChecks=True,qualification='Retained exports are completed V2 actual live checks, reused only after exact republished public/runtime input equality. Source and previously missing joint checks are fresh. No failed check removed.')
 save(out/'completed-v2-report.json',old);save(out/'combined-live-browser.json',part);return part
