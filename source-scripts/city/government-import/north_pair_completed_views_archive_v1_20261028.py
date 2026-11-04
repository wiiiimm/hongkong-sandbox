"""Freeze a failed installation's completed browser evidence without installation credit."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from primrose_compound_foundation_v2_20261015 import module
P='government-xl-west-kowloon-north-pair-after-ocean-';BASE=ROOT/'docs/astra-city/government-import';OLD=P+'original-installed-v2-20261028';BATCH=P+'completed-v2-browser-evidence-v1-20261028'
def main():
 out=BASE/BATCH;assert not out.exists();doc=BASE/OLD;local=HERE/'local'/OLD;failure=read(doc/'failure-recovery.json');assert failure['allPublicDestinationsRestored']and failure['currentPointerRestoredNotDerivedCredit']and not failure['derivedInstalledReviewHistoryRetained']and not failure['rollbackErrors'];history=read(doc/'historical-input-context.json');saved={r['originalPath']:r for r in history['mutableCurrentByteSnapshots']}
 for path in history['allMutableDestinations']:
  p=ROOT/path
  if path in saved:assert p.exists()and digest(p.read_bytes())==saved[path]['originalSHA256']
  else:assert not p.exists(),path
 report=read(doc/'live-browser.json');assert report['passed']and not report['errors']and len([v for v in report['views']if 'time'in v])==8 and not report['jointViews'];assert len(report['retainedNativeOwnViews'])==268
 for w in [390,1280]:
  part=read(doc/('viewport-'+str(w))/'live-browser.json');assert part['passed']and not part['errors'];assert len(part['retainedNativeOwnViews'])==134 and len([v for v in part['views']if 'time'in v])==4
 atomic=read(doc/'atomic-live/report.json');assert atomic['passed']and not atomic['pageErrors']and len(atomic['cases'])==4
 result=dict(uids=['landsd/182397:0','landsd/309340:0'],completedLiveViewports=[390,1280],completedRetainedExports=268,completedSourceExports=8,atomicCasesPassed=4,missingJointViews=True,allCurrentMutableBytesIndependentlyRestored=True,installationApproved=False,sourceGeometryChanges=0,qualification='Terminal rolled-back attempt. Both full browser reports passed and all actual source/retained exports are archived. Installer failed because it required jointViews never requested by config. Reuse requires exact republished public/runtime bindings, fresh atomic and missing joint/source checks; no installed credit.')
 save(out/'summary.json',result);refs=[Path(__file__),HERE/'north_pair_live_install_v2_20261028.py',ROOT/'docs/astra-city/model-integration-20260909'/OLD/'publication-plan.json'];refs.extend(p for folder in [doc,local]for p in folder.rglob('*')if p.is_file()and p.name!='reservation.json');module('north_completed_v2_views_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'completed-full-browser-evidence-from-rolled-back-install-missing-joint-only',refs,result);print(result,flush=True)
if __name__=='__main__':main()
