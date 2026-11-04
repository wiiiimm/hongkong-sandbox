"""Additional unobscured original podium witness; no repeated native scope credit."""
import importlib.util,json,os,subprocess
from pathlib import Path
from run import ROOT,HERE,read,save,digest
BASE=ROOT/'docs/astra-city/government-import';STAGEBATCH='government-xl-man-fuk-ten-complete-typed-stage-v2-20261010';SOURCE=BASE/STAGEBATCH;BATCH='government-xl-man-fuk-podium-solid-followup-v1-20261010';DOC=BASE/BATCH;UID='landsd/266062:0'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def recheck():
 acceptance=read(SOURCE/'acceptance.json');assert acceptance['passed'] and acceptance['newlyInstalled']==0 and not acceptance['publication'] and acceptance['manifestSHA256']==digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())
 for r in acceptance['evidenceRefs']:assert ref(ROOT/r['path'])==r
 assert ref(SOURCE/'staged-browser.json')==acceptance['stagedBrowser'];assert len(acceptance['uids'])==10;assert len(read(SOURCE/'staged-browser.json')['retainedNativeOwnViews'])==4
 return acceptance
def main():
 assert not DOC.exists();acceptance=recheck();config=read(HERE/'accepted'/STAGEBATCH/'browser-config.json');config.update(doc=str(DOC.relative_to(ROOT))+'/',browserUids=[UID],failureTestUids=[UID],nativeSupportUidsByModel={UID:[]},captureBoundsByViewport={},captureBoundsByModel={UID:[[1874.578125,32.189998626708984,-3148.701171875],[2088.421875,48.04199981689453,-2926.80078125]]},captureDirectionByModel={UID:[.4,3,-.7]});save(DOC/'browser-config.json',config)
 subprocess.run(['node',str(HERE/'xl-terrain-recovery-20261010-multi-native-solid-browser-v5.mjs'),'staged',str((DOC/'browser-config.json').relative_to(ROOT))],cwd=ROOT,check=True,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'})
 s=importlib.util.spec_from_file_location('browser',HERE/'integrate.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);report=m.browser_verified(DOC/'staged-browser.json',{UID});assert not report.get('retainedNativeOwnViews') and len([v for v in report['views'] if 'time' in v])==4;assert recheck()==acceptance
 proof=dict(uids=acceptance['uids'],extraVisualWitnessUid=UID,baseCompleteStage=ref(SOURCE/'acceptance.json'),baseCompleteBrowser=ref(SOURCE/'staged-browser.json'),stagedBrowser=ref(DOC/'staged-browser.json'),browserConfig=ref(DOC/'browser-config.json'),allRetainedNativeOwnViewsRemainBoundToBaseStage=True,noNativeOrSupportProofOmitted=True,sourceGeometryChanges=0,publication=False,newlyInstalled=0,passed=True,evidenceRefs=[ref(p) for p in [Path(__file__),SOURCE/'acceptance.json',SOURCE/'staged-browser.json',DOC/'staged-browser.json',DOC/'browser-config.json',HERE/'xl-terrain-recovery-20261010-multi-native-solid-browser-v5.mjs']]);save(DOC/'acceptance.json',proof)
 print(dict(supplementaryPodiumSolidWitnessPassed=True),flush=True)
if __name__=='__main__':main()
