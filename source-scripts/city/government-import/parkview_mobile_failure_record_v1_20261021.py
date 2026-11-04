"""Persist completed failed browser attempt; no corruption or acceptance inference."""
from pathlib import Path
from run import ROOT,HERE,read,save
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';OLD=BASE/'government-xl-parkview-four-staged-browser-v1-20261021';BATCH='government-xl-parkview-mobile-failure-record-v1-20261021';DOC=BASE/BATCH
assert not DOC.exists();desktop=read(OLD/'1280/staged-browser.json');mobile=read(OLD/'390/staged-browser.json');assert desktop['passed'] and not desktop['errors'];assert not mobile.get('passed') and mobile['errors']==['page.waitForFunction: Timeout 60000ms exceeded.'];assert mobile['views']==[]
stage=HERE/'local'/OLD.name;cat=read(stage/'catalogue.json');uids=[m['uid']for m in cat['models']];assert len(uids)==4
result=dict(uids=uids,desktopPassed=True,mobilePassed=False,failedPhase='initial retained Parkview podium activation before candidate testing',failedRetainedUid='landsd/254491:0',sourceDownloadHTTPStatus=200,sourceGeometryChanges=0,installationApproved=False,permanentNoninstallable=False,nextAction='Capture exact cache/budget/dependency/activation state under unchanged checks; preserve timeout and rerun only after terminal lease release.')
save(DOC/'failure.json',result);refs=[Path(__file__),HERE/'parkview_four_staged_browser_v1_20261021.py',HERE/'harbourfront_live_browser_v4_20261021.mjs',*[p for p in OLD.rglob('*')if p.is_file()],*[p for p in stage.rglob('*')if p.is_file() and p.name!='reservation.json']]
module('parkview_failure_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-browser-failed-attempt-preserved',refs,result)
