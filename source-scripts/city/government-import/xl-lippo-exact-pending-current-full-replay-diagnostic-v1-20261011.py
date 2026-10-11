"""Replay the full unchanged current Lippo role under its exact own pending phase.
Preserves the original approval/inventory/event. No publication or review writes.
"""
import importlib.util,json,subprocess,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations,connect
import lippo_tower_current_basic_complete_role_current_bound_v4_20261011 as bound
BATCH='government-xl-lippo-exact-pending-current-full-replay-diagnostic-v1-20261011'
DOC=bound.BASE/BATCH;LOCAL=HERE/'local'/BATCH
RECHECK=HERE/'xl-lippo-tower-exact-pending-resume-recheck-v1-20261011.py'
FAILED=bound.BASE/'government-xl-lippo-tower-current-basic-unchanged-installed-v1-20261011'
LOG=Path('/tmp/xl-lippo-live-install-v1-20261011.log')
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def load(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 assert not DOC.exists() and not LOCAL.exists()
 inp=read(bound.INPUT/'input.json.gz')
 resources=[('building:' if r['building']['uid'].startswith('landsd/') else 'foreign-form:')+r['building']['uid'] for r in inp['completeCurrentForms']]
 claim=reservations.claim('lippo-exact-pending-replay-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'],claim
 try:
  stage=load('lippo_exact_pending_fresh_recheck',RECHECK)
  role,entry=stage.recheck(LOCAL)
  saved=read(stage.ROLE/'acceptance.json');assert {k:saved[k] for k in role}==role
  assert entry==read(stage.ROLE/'staged-entry.json')
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY');phase=bound.verify_pending_live(c,bound.PENDING_CONTEXT)
  assert phase['snapshotId']=='8d35b6f1d6f6bcdc'
  diagnostic=dict(batch=BATCH,pendingSnapshotId=phase['snapshotId'],completeCurrentMathematicalRoleExactlyMatchesOriginalV3=True,
   stagedEntryExactlyMatchesOriginalV3=True,currentRole=role,stagedEntry=entry,exactPendingPhase=phase,
   publication=False,installationApproved=False,newlyInstalled=0,sourceGeometryChanges=0,terrainGeometryChanges=0,
   originalApprovalAndInventoryRetained=True,reviewHistoryDeleted=False,newApprovalCreated=False,
   sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False)
  save(DOC/'diagnostic.json.gz',diagnostic)
  tests=[]
  for filename in ['test_lippo_exact_own_pending_preapply_phase_guard_v1_20261011.py','test_lippo_tower_current_basic_complete_role_current_bound_v4_20261011.py']:
   p=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(HERE),'-p',filename,'-v'],cwd=ROOT,capture_output=True,text=True)
   tests.append(dict(file=filename,exitCode=p.returncode,stdout=p.stdout,stderr=p.stderr,hermeticCapturedSourceCounterexamples=True));assert p.returncode==0,p.stderr
  save(DOC/'tests.json',dict(tests=tests,separateUnmockedProductionFullCurrentNativeIdentityPhysicalAndNeonReplayBeforeTests=True))
  assert LOG.is_file();target=DOC/'preserved-live-v1-preapply-failure.log';target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(LOG.read_bytes())
  save(DOC/'preserved-live-v1-failure.json',dict(originalLog=str(LOG),copiedLog=ref(target),failureBeforeApply=True,
   failedScript=ref(HERE/'xl-lippo-tower-current-basic-unchanged-live-install-v1-20261011.py'),
   exactOriginalApproval=ref(FAILED/'acceptance.json'),unchangedCurrentManifest=inp['currentManifest'],
   originalPendingSnapshotRetained='8d35b6f1d6f6bcdc',approvalHistoryReset=False,installedCreditGranted=False))
  context=read(bound.PENDING_CONTEXT)
  refs=[Path(__file__),RECHECK,HERE/'lippo_tower_current_basic_complete_role_current_bound_v4_20261011.py',
   HERE/'lippo_exact_own_pending_preapply_phase_guard_v1_20261011.py',bound.PENDING_CONTEXT,
   *[HERE/t['file'] for t in tests],*[p for p in LOCAL.rglob('*') if p.is_file()],
   *[ROOT/r['path'] for r in context['exactLiveFiles'].values()],
   *[p for p in FAILED.rglob('*') if p.is_file()]]
  for folder in [stage.ROLE,bound.INPUT,bound.IDENTITY,bound.PHYSICAL,bound.ROLE,bound.SEPARATION,bound.DELTA]:
   receipt=read(folder/'result.json');bound.receipt_pins(receipt);refs.append(folder/'result.json');refs.extend(ROOT/r['path'] for r in receipt['evidenceRefs'])
  bound.assert_live(inp,read(bound.INPUT/'complete-current-geometry.json.gz'));assert reservations.owns(claim['reservation'])
  freezer=load('lippo_exact_pending_immutable_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py')
  receipt=freezer.freeze(BATCH,'lippo-exact-own-pending-full-current-role-diagnostic-no-publication',refs,
   dict(uids=[entry['uid']],pendingSnapshotId=phase['snapshotId'],currentManifest=inp['currentManifest'],
   completeCurrentMathematicalRoleExactlyMatchesOriginalV3=True,stagedEntryExactlyMatchesOriginalV3=True,
   publication=False,installationApproved=False,newlyInstalled=0,sourceGeometryChanges=0,terrainGeometryChanges=0))
  print(json.dumps(dict(jobId=receipt['jobId'],completeCurrentReplayPassed=True,publication=False,newlyInstalled=0)),flush=True)
 finally:assert reservations.release(claim['reservation'])['ok']
if __name__=='__main__':main()
