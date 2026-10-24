"""DRAFT nonaccepting rollback-history/provenance job; no old ledger mutations.
ROOT reviews/authorizes before any tests, leases, diagnostic job or stage execution.
"""
import importlib.util,json,subprocess,sys,uuid,unittest
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
import heya_aqua_exact_rollback_recovery_20261011 as recovery
BATCH='government-xl-heya-aqua-exact-v1-rollback-factual-entry-recovery-v2-20261011';DOC=recovery.BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
VALIDATION=recovery.BASE/'government-xl-heya-aqua-exact-rollback-recovery-validation-v2-20261011'
CODES=[Path(__file__),HERE/'heya_aqua_exact_rollback_recovery_20261011.py',HERE/'test_heya_aqua_exact_rollback_recovery_20261011.py',HERE/'heya_aqua_supplementary_recovery_camera_20261011.py',HERE/'xl-heya-aqua-184286-unchanged-private-stage-v2-20261011.py',HERE/'xl-heya-aqua-184286-unchanged-live-install-v2-20261011.py',HERE/'xl-heya-aqua-retained-podium-high-camera-browser-v1-20261011.mjs',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py']
def hashes():return {str(p.relative_to(ROOT)):digest(p.read_bytes())for p in CODES}
def validation():
 assert not VALIDATION.exists();before=hashes();VALIDATION.mkdir(parents=True);log=VALIDATION/'unittest.log'
 suite=unittest.defaultTestLoader.loadTestsFromName('test_heya_aqua_exact_rollback_recovery_20261011');assert suite.countTestCases()==12
 with log.open('w')as s:out=unittest.TextTestRunner(stream=s,verbosity=2).run(suite)
 assert hashes()==before;save(VALIDATION/'validation.json',dict(testsRun=out.testsRun,passed=out.wasSuccessful(),codeHashes=before,testLog=recovery.ref(log),hermeticActualEntryCounterexamples=True,publicationApproval=False))
 assert out.testsRun==12 and out.wasSuccessful()
def owned():
 assert reservations.owns(read(LEASE))and not DOC.exists();v=read(VALIDATION/'validation.json');assert v['passed']and v['testsRun']==12 and v['codeHashes']==hashes()and recovery.ref(ROOT/v['testLog']['path'])==v['testLog']
 role,entry,row=recovery.recheck(LOCAL/'current-exact-replay',require_entry_approval=False)
 history=recovery.current_scene_and_history();assert history['currentInstallationCredit']is False
 previous=read(recovery.BASE/'government-xl-twin-regency-evangel-three-atomic-installed-v1-20261011/full-xl-current-count.json');assert previous['counts']==dict(total=521,installedVerified=232,remaining=289)
 save(DOC/'failure-history-and-current-rollback.json',dict(**history,failedPhase='final-count-audit-after-live-browser-and-installed-ledger',missingSourceIdentityReviewed=True,privatePublicationApprovedWasFalse=True,proposedMetadataOnlyChanges=recovery.CHANGE,old232Verified289Remaining=True,oldReviewEventsPreserved=True,noOldReceiptGrantedCurrentCredit=True))
 save(DOC/'exact-unchanged-role-replay.json',role)
 refs=CODES+[VALIDATION/'validation.json',ROOT/v['testLog']['path'],recovery.HISTORY,recovery.SOURCE_CERT,recovery.ROLE/'result.json',recovery.ROLE/'complete-current-role.json.gz',recovery.ROLE/'private-stage-entry.json']
 refs+=[p for p in recovery.OLD.rglob('*')if p.is_file()]+[p for p in (HERE/'local'/recovery.OLD.name).rglob('*')if p.is_file()]
 oldstage=recovery.BASE/'government-xl-heya-aqua-184286-unchanged-private-stage-v1-20261011'
 refs+=[p for p in oldstage.rglob('*')if p.is_file()]+[p for p in LOCAL.rglob('*')if p.is_file()]
 assert reservations.owns(read(LEASE));before=hashes()
 spec=importlib.util.spec_from_file_location('heya_recovery_exact_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 m.freeze(BATCH,'heya-exact-failed-v1-rollback-factual-entry-diagnostic-v2',refs,dict(uids=[recovery.T,recovery.P],history=history,rawFailureRetained=True,sourceIdentityPositive=True,fullNumericalRoleUnchanged=True,proposedEntryMetadataOnlyChanges=recovery.CHANGE,rootFactualApprovalStillRequired=True,stageExecutionApproved=False,liveExecutionApproved=False,oldReviewsOrEventsModified=False))
 assert hashes()==before and reservations.owns(read(LEASE))
def main():
 if '--validate'in sys.argv:return validation()
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists()and not LOCAL.exists();forms=read(recovery.BASE/recovery.FOLDERS['actual']/'capture-inputs.json.gz')['completeCurrentForms']
 claim=reservations.claim('heya-exact-rollback-recovery-'+str(uuid.uuid4()),['building:'+f['uid']for f in forms],batch=BATCH,ttl=3600);assert claim['ok'];save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
 subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
