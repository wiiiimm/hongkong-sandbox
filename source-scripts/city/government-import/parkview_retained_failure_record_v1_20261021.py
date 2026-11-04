"""Preserve terminal retained-view failure; source corruption is not inferred."""
from pathlib import Path
from run import ROOT,HERE,read,save
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';OLD=BASE/'government-xl-parkview-four-staged-browser-v2-20261021';BATCH='government-xl-parkview-retained-failure-record-v1-20261021';DOC=BASE/BATCH
assert not DOC.exists();report=read(OLD/'1280/staged-browser.json');assert not report.get('passed') and len(report['errors'])==1 and "Cannot read properties of undefined (reading 'group')"in report['errors'][0]
stage=HERE/'local'/OLD.name;uids=[m['uid']for m in read(stage/'catalogue.json')['models']];views=[r for r in report['views']if 'time'in r];assert len(views)==8 and len(report['retainedNativeOwnViews'])==4
result=dict(uids=uids,desktopPassed=False,newSourceViewsCompleted=8,retainedOwnViewsCompleted=4,mobileRun=False,failedPhase='retained own capture after activation/selection closure',failure=report['errors'][0],sourceGeometryChanges=0,installationApproved=False,permanentNoninstallable=False,nextAction='Capture current loader budget, selected ID, wanted set and cache errors when retained detail disappears; maintain all source/retained assertions.')
save(DOC/'failure.json',result);refs=[Path(__file__),HERE/'parkview_four_staged_browser_v2_20261021.py',HERE/'parkview_four_acceptance_browser_v1_20261021.mjs',*[p for p in OLD.rglob('*')if p.is_file()],*[p for p in stage.rglob('*')if p.is_file()and p.name!='reservation.json']]
module('parkview_retained_failure_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-retained-browser-failed-attempt-preserved',refs,result)
