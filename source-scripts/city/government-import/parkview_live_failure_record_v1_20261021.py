"""Preserve rolled-back Parkview live attempt without assigning source corruption."""
from pathlib import Path
from run import ROOT,HERE,read,save
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';OLD=BASE/'government-xl-parkview-four-original-installed-v1-20261021';BATCH='government-xl-parkview-live-failure-record-v1-20261021';DOC=BASE/BATCH
assert not DOC.exists()
r=read(OLD/'failure-recovery.json');assert r['allPublicDestinationsRestored'] and not r['rollbackErrors'] and not r['derivedInstalledHistoryRetained']
m=read(OLD/'390/live-browser.json');d=read(OLD/'1280/live-browser.json');assert m['passed'] and not d.get('passed');failure=d['retainedCaptureFailure'];assert failure['uid']=='landsd/255439:0' and failure['missingDetailedActor'] and failure['uid'] in failure['wanted']
result=dict(uids=read(OLD/'acceptance.json')['uids'],newlyInstalled=0,installationApproved=False,permanentNoninstallable=False,mobilePassed=True,desktopPassed=False,rollback=r,retainedCaptureFailure=failure,nextAction='Remove the asynchronous gap between closing selection, checking retained actor state and capturing pixels; retain all active, visible, whole-bounds, source-hash and fallback assertions. No runtime or geometry changes.')
save(DOC/'failure.json',result)
module('parkview_live_failure_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'rolled-back-original-live-capture-failure',[Path(__file__),HERE/'parkview_four_live_install_v1_20261021.py',HERE/'parkview_retained_capture_diagnostic_v1_20261021.mjs',*[p for p in OLD.rglob('*')if p.is_file()]],result)
