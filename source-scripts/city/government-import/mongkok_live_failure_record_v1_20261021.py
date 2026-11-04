"""Record the rolled-back desktop readiness failure without installation credit."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-mongkok-live-failure-record-v1-20261021';DOC=BASE/BATCH
old=BASE/'government-xl-mongkok-original-installed-v1-20261021';recovery=read(old/'failure-recovery.json');assert recovery['allPublicDestinationsRestored'] and not recovery['rollbackErrors'] and not recovery['derivedInstalledHistoryRetained']
plan=read(BASE/'government-xl-mongkok-qualified-publication-plan-v1-20261021/publication-plan.json')
assert digest((ROOT/plan['currentManifest']['path']).read_bytes())==plan['currentManifest']['sha256']
assert digest((ROOT/plan['currentPointer']['path']).read_bytes())==plan['currentPointer']['sha256']
assert read(old/'390/live-browser.json')['passed'];failed=read(old/'1280/live-browser.json');assert failed['errors']==['page.waitForFunction: Timeout 300000ms exceeded.']
refs=[Path(__file__),HERE/'mongkok_live_install_v1_20261021.py',HERE/'mongkok_retained_joint_browser_v2_20261021.mjs',*[p for p in old.rglob('*')if p.is_file()]]
result=dict(uids=['landsd/240332:0'],installationApproved=False,publication=False,newlyInstalled=0,permanentRejection=False,rollbackVerified=True,liveMobilePassed=True,liveDesktopPassed=False,reason='Desktop test exceeded300s waiting for base-map cache completion before model assertions. Both originals were already active in captured log. Cause is not yet established; fixed-camera diagnostic with cache-state capture queued. Model geometry/canonical thresholds unchanged.',revisit='Complete deterministic desktop and mobile browser verification, then retry guarded publication from unchanged source plan with fresh bound evidence.')
save(DOC/'failure-summary.json',result);module('stadium_live_failure_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'rolled-back-live-browser-readiness-failure',refs,result)
