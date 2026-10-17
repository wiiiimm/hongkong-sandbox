"""Read-only additive resume verifier inventory; inherits closed stage contracts.
No exclusions, numeric leaves, approval, publication or history changes are made.
"""
import argparse,json
from pathlib import Path
from run import ROOT,HERE,read,digest
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-lippo-exact-pending-current-full-replay-diagnostic-v1-20261011'
STAGE_CERT=BASE/'government-xl-lippo-post17-stage-root-closure-v1-20261011/root-closed-scope.json'
FOLDERS=[BASE/BATCH,HERE/'local'/BATCH,
 BASE/'government-xl-lippo-exact-preapply-pending-attempt-context-v1-20261011',
 BASE/'government-xl-lippo-tower-current-basic-unchanged-installed-v1-20261011',
 HERE/'local/government-xl-lippo-tower-current-basic-unchanged-installed-v1-20261011',
 STAGE_CERT.parent]
SCRIPTS=['lippo_exact_own_pending_preapply_phase_guard_v1_20261011.py',
 'test_lippo_exact_own_pending_preapply_phase_guard_v1_20261011.py',
 'lippo_tower_current_basic_complete_role_current_bound_v4_20261011.py',
 'test_lippo_tower_current_basic_complete_role_current_bound_v4_20261011.py',
 'xl-lippo-tower-exact-pending-resume-recheck-v1-20261011.py',
 'xl-lippo-tower-exact-pending-resume-live-install-v2-20261011.py',
 'xl-lippo-exact-pending-current-full-replay-diagnostic-v1-20261011.py',
 'xl-lippo-exact-pending-installed-result-scope-builder-v2-20261011.py']
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--stage-contract',required=True);p.add_argument('--out',required=True);a=p.parse_args()
 contract=read(Path(a.stage_contract));assert isinstance(contract['paths'],list)
 for k in ['historicalManifestAliases','metadataLeafPaths','metadataLeafJsonPointers','auditDeclarationContextRefs']:assert k in contract
 cert=read(STAGE_CERT);assert cert['independentlyVerified'] and cert['verifiedReferenceVersions']>0
 assert set(contract['paths'])<=set(cert['paths'])
 paths=set(cert['paths'])|set(contract['paths'])
 def add(path):
  path=Path(path).resolve();assert path.is_relative_to(ROOT) and path.is_file(),str(path);paths.add(str(path.relative_to(ROOT)))
 receipt=read(BASE/BATCH/'result.json');assert receipt['publication'] is False and receipt['newlyInstalled']==0
 proof=read(BASE/BATCH/'diagnostic.json.gz');assert proof['pendingSnapshotId']=='8d35b6f1d6f6bcdc'
 assert proof['completeCurrentMathematicalRoleExactlyMatchesOriginalV3'] and proof['stagedEntryExactlyMatchesOriginalV3']
 for folder in FOLDERS:
  assert folder.is_dir(),str(folder)
  for f in folder.rglob('*'):
   if f.is_file():add(f)
 for name in SCRIPTS:add(HERE/name)
 add(Path(__file__))
 for pin in receipt['evidenceRefs']:
  path=ROOT/pin['path'];assert digest(path.read_bytes())==pin['sha256'];add(path)
 context=read(BASE/'government-xl-lippo-exact-preapply-pending-attempt-context-v1-20261011/capture.json.gz')
 for pin in context['exactLiveFiles'].values():
  path=ROOT/pin['path'];assert digest(path.read_bytes())==pin['sha256'];add(path)
 assert all((ROOT/f).is_file() for f in paths)
 output={**contract,'paths':sorted(paths)}
 assert {k:v for k,v in output.items() if k!='paths'}=={k:v for k,v in contract.items() if k!='paths'}
 Path(a.out).write_text(json.dumps(output,indent=2)+'\n')
 print(json.dumps(dict(paths=len(paths),inheritedStageContractsUnchanged=True,pathInventoryOnly=True,independentlyVerified=False,publication=False,newlyInstalled=0)))
if __name__=='__main__':main()
