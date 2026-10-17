"""Declare complete successful Mei Yat stage and guarded root live interface."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
BASE=ROOT/'docs/astra-city/government-import';OUT=BASE/'xl-terrain-recovery-20261010-mei-yat-stage-scope-declaration-v3'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not OUT.exists();source=BASE/'xl-terrain-recovery-20261010-mei-yat-source-scope-declaration-v4/declared-scope.json';scope=read(source);paths=set(scope['closedPaths'])
 def add(p):assert p.is_file();paths.add(str(p.relative_to(ROOT)))
 batch='government-xl-terrain-recovery-mei-yat-plain-typed-stage-v2-20261010';final=BASE/batch;accept=read(final/'acceptance.json');assert accept['passed'] and accept['checksPassed'] and not accept['publication'] and accept['newlyInstalled']==0
 for parent in [final,HERE/'accepted'/batch,BASE/'government-xl-terrain-recovery-mei-yat-plain-typed-stage-v1-20261010',HERE/'accepted/government-xl-terrain-recovery-mei-yat-plain-typed-stage-v1-20261010',BASE/'xl-terrain-recovery-20261010-mei-yat-stage-scope-declaration-v1']:
  for p in parent.rglob('*'):
   if p.is_file():add(p)
 for n in ['xl-terrain-recovery-20261010-plain-single-source-stage-v1.py','xl-terrain-recovery-20261010-plain-single-source-live-v1.py','xl-terrain-recovery-20261010-plain-single-source-live-v2.py','xl-terrain-recovery-20261010-mei-yat-plain-stage-config-v1.py','xl-terrain-recovery-20261010-mei-yat-plain-stage-config-v2.py','test_plain_single_source_stage_interface_20261010.py']:add(HERE/n)
 add(source);add(Path(__file__));add(BASE/'xl-terrain-recovery-20261010-mei-yat-stage-scope-declaration-v2/declared-scope.json');scope.update(closedPaths=sorted(paths),closedExplicitPaths=sorted(paths),presentFileBindings=[ref(ROOT/p) for p in sorted(paths)],sourceScope=ref(source),sourceScopeMetadataLeafOnly=False,stagedAcceptance=ref(final/'acceptance.json'),stageBrowserPassed=True,stagedCandidateViews=4,stagedRetainedOwnViews=0,preparedLiveAdapter=ref(HERE/'xl-terrain-recovery-20261010-plain-single-source-live-v2.py'),publication=False,newlyInstalled=0,declarationOnly=True,rootIndependentRecursiveVerificationRequired=True)
 save(OUT/'declared-scope.json',scope);print(dict(paths=len(paths),stageBrowserPassed=True))
if __name__=='__main__':main()
