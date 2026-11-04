"""Recover the final retained view under the same exact private scene inputs.
Focused evidence only; this is not a full-assembly browser acceptance.
"""
from pathlib import Path
import copy,json,subprocess,os,uuid
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-fu-tor-loy-olympic-mobile-focused-v1-20261023'
PARENT='government-xl-fu-tor-loy-five-source-staged-browser-v2-20261023'
FAILED='government-xl-fu-tor-loy-staged-v2-mobile-failure-context-v1-20261023'
def main():
 doc=BASE/BATCH;local=HERE/'local'/BATCH;assert not doc.exists();refs=[Path(__file__)]
 _,pins=authenticate(BASE/FAILED);refs.append(BASE/FAILED/'result.json')
 path=HERE/'local'/PARENT/'browser-config-390.json';assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];refs.append(path);cfg=copy.deepcopy(read(path))
 manifest=ROOT/'3d-viewer/city/data/manifest.json';cap='government-xl-fu-tor-loy-five-originals-current-v1-20261023-runtime';_,cp=authenticate(BASE/cap);sp=BASE/cap/'selection.json.gz';assert digest(sp.read_bytes())==cp[str(sp.relative_to(ROOT))] and digest(manifest.read_bytes())==read(sp)['manifestSHA256'];refs.extend([manifest,BASE/cap/'result.json',sp])
 for p,h in pins.items():
  if p.startswith(str((HERE/'local'/PARENT).relative_to(ROOT))+'/'):
   q=ROOT/p;assert digest(q.read_bytes())==h;refs.append(q)
 cfg.update(additionalRetainedUids=['landsd/81242:0'],viewportWidths=[390],failureTestUids=[],retainedOnly=True,jointUids=[],doc=str((doc/'390').relative_to(ROOT))+'/')
 configpath=local/'focused-config.json';save(configpath,cfg);refs.append(configpath)
 keys=['building:'+r['uid']for r in read(sp)['rows']]+['building:landsd/81242:0','terrain:city/data/terrain.json']
 claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),keys,batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];save(local/'reservation.json',json.loads(json.dumps(lease,default=str)))
 try:
  tool=HERE/'ronsdale_three_live_browser_v8_20261023.mjs';doc.mkdir();refs.append(tool)
  with (doc/'browser.log').open('w')as log:
   command=['node',str(tool),'staged',str(configpath.relative_to(ROOT))];proc=subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'},timeout=1200)
  save(doc/'command.json',dict(command=command,exitCode=proc.returncode));assert proc.returncode==0
  report=read(doc/'390/staged-browser.json');assert report['passed']and not report['errors']and report['focusedRetainedOnly']and not report['views']
  views=report['retainedNativeOwnViews'];assert len(views)==2 and {(r['uid'],r['time'])for r in views}=={('landsd/81242:0',t)for t in ['15:00','22:00']}
  assert all(r['active']and r['visible']and r['fullyFramed']and not r['overflow']and not r['fallbackFaces']and all(r['meshVisibility'])and not any(r['wireframeFlags'])for r in views)
  assert reservations.owns(lease)and digest(manifest.read_bytes())==read(sp)['manifestSHA256']
  result=dict(uids=['landsd/81242:0'],focusedRetainedOnly=True,observedTimes=['15:00','22:00'],currentManifestSHA256=digest(manifest.read_bytes()),sourceGeometryChanges=0,installationApproved=False,fullAssemblyAccepted=False,qualification='Focused fresh current mobile day/night original capture only. Same exact private catalogue/source/terrain and unchanged normal budgets. Selection cleared before an atomic active-visible verification/render, eliminating the split snapshot race. This report cannot stand alone as full FuTor source/browser approval.')
  module('fu_tor_retained_focus_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'focused-current-mobile-original-retained-views',refs,result);print(result,flush=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
