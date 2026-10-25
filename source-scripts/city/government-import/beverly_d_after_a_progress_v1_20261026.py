"""Persist qualified D and exact current continuation evidence before installation."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-beverly-d-after-a-progress-v1-20261026'
def main():
 out=BASE/BATCH;assert not out.exists();refs=[Path(__file__)];completed=[]
 for folder in sorted(BASE.iterdir()):
  relevant=folder.name.startswith('government-xl-beverly-d-after-a-')or folder.name.startswith('government-xl-beverly-d-finite-')
  if not relevant or folder.name==BATCH or not(folder/'result.json').exists():continue
  r,_=authenticate(folder);refs.append(folder/'result.json');completed.append(dict(batch=folder.name,jobId=r['jobId']))
 def take(batch,name):
  _,pins=authenticate(BASE/batch);refs.append(BASE/batch/'result.json');p=BASE/batch/name;assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
 cfgpath=BASE/'government-xl-beverly-d-finite-independent-original-install-config-v1-20261026.json';cfg=read(cfgpath);refs.append(cfgpath)
 review=take(cfg['review'],'ROOT-SOURCE-REVIEW.json');assert review['visualAcceptance']and len(review['imagesActuallyViewed'])==len(review['retainedImagesActuallyViewed'])==4
 q=take(cfg['prefix']+'-qualified-stage-v2-20261026','qualification.json');assert q['privateStageQualified']and q['runtimeAvailabilityDependenciesByUid']=={}
 exact=take('government-xl-after-beverly-a-unfinished-exact-source-inventory-v1-20261026','summary.json');assert exact['unfinished']==140 and exact['unmatchedViewerUIDs']==2
 finite=take(cfg['finiteEvidence'],'summary.json');assert finite['verifiedFinitePaths']==196 and finite['completeFourWorldCanonicalRetainedBasicSupport']is False
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==exact['currentManifestSHA256']==review['currentManifest']['sha256'];refs.append(manifest)
 result=dict(uids=list(cfg['sources']),installedXL=381,unfinishedXL=140,totalFixedXL=521,currentNativeActors=6958,newlyInstalled=0,installationApproved=False,publication=False,sourceGeometryChanges=0,aiGeometryModelling=False,humanDecisionRequired=False,state='private-qualified-awaiting-guarded-install',completed=completed,privateSourceImagesActuallyViewedByRoot=review['imagesActuallyViewed'],privateRetainedImagesActuallyViewedByRoot=review['retainedImagesActuallyViewed'],tests=dict(adversarialIndependentAdmission=12,passed=True,syntheticAcceptanceFixtureNeverPublished=True),rawFailuresPreserved=['Raw93.424136%coverage/tworeasons and freshAutomaticIdentityStillRejected remainexplicit. Current identity differsfromreviewedidentityONLYmanifestSHA; no global95%rulechange/identityreinvestigation.','CanonicalBASICsupport staysfalse; separatefiniteV2replays196pathsagainstfreshcurrent49unresolvedrawprobes.','Source C publicationApproved:false/wholeentry/bytesunchanged,notreapproved. RetainedCimageshaveordinarypartialforegroundBASICocclusion; roof/mostfacadesreadable; no newD/Ccontacts.','Before-BASICD/Cfallbackbaseline124contacts retained; all4originalD/Cdetailed andC BASICfallbackstreams have0contacts. No nativeavailabilityedgeinvented.'],remainingWork=['Prepare-onlyPASSED1source/+1XL/previous381. Commit/pushqualifiedD before actualinstall withselected_original_finite_basic_native_independent_install_v1_20261026.py andconfiggovernment-xl-beverly-d-finite-independent-original-install-config-v1-20261026.json/installVersionv2. Theninspect8FRESHliveexports,recorderV2,independentfinite_basic_native_independent_installed_readback_v1_20261026.py full6958oldassets/521/globalBASIC/C/allmanifestfields/terrain,refreshbounds/exact139including2nullUIDkeys,commit/push. ExpectedONLYafterverifiedsuccess382XL/139unfinished/6959actors.','KeepP233218BASICforK/F/E/A/D; replacingit requiresdependent revalidation. No sourcegeometry/terrain/scale edits, AI geometry modelling, optimisation, shared4176restart/mainmerge/newagents.','AfterD continueotherfixed139sources usingexactsourcekeys. Historical acquisition states are NOTcurrentpermanenteligibility. Preserve2nullUIDkeys and investigateexactsourceidentityratherthanignorethem.'])
 save(out/'remaining-work.json',result)
 log=Path('/tmp/beverly-d-independent-admission-tests.log');assert 'Ran 12 tests'in log.read_text()and log.read_text().rstrip().endswith('OK');(out/'admission-tests.log').write_bytes(log.read_bytes())
 refs.extend([HERE/'finite_basic_native_independent_admission_v1_20261026.py',HERE/'test_finite_basic_native_independent_admission_v1_20261026.py'])
 module('beverly_d_progress_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'qualified-current-D-original-and-explicit-remaining-installation-work',list(dict.fromkeys(refs)),result)
 print(dict(completed=len(completed),state=result['state']),flush=True)
if __name__=='__main__':main()
