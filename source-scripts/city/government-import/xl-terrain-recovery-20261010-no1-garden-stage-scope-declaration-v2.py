"""Declare all failed/final No1 stage artifacts and prepared live adapter."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
BASE=ROOT/'docs/astra-city/government-import';OUT=BASE/'xl-terrain-recovery-20261010-no1-garden-stage-scope-declaration-v2';assert not OUT.exists();OUT.mkdir();source=BASE/'xl-terrain-recovery-20261010-no1-garden-source-scope-declaration-v1/declared-scope.json';scope=read(source);paths=set(scope['closedPaths'])
def add(p):assert p.is_file();paths.add(str(p.relative_to(ROOT)))
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
final=BASE/'government-xl-terrain-recovery-no1-garden-typed-stage-v4-20261010';accept=read(final/'acceptance.json');assert accept['passed'] and accept['checksPassed'] and not accept['publication'] and accept['newlyInstalled']==0
for v in [1,2,3,4]:
 batch='government-xl-terrain-recovery-no1-garden-typed-stage-v'+str(v)+'-20261010'
 for parent in [BASE/batch,HERE/'accepted'/batch]:
  if parent.exists():
   for p in parent.rglob('*'):
    if p.is_file():add(p)
 add(HERE/('xl-terrain-recovery-20261010-no1-garden-stage-install-v'+str(v)+'.py'))
for v in [1,2]:add(HERE/('xl-terrain-recovery-20261010-no1-garden-live-install-v'+str(v)+'.py'))
add(source);add(Path(__file__));scope.update(closedPaths=sorted(paths),closedExplicitPaths=sorted(paths),presentFileBindings=[ref(ROOT/p) for p in sorted(paths)],sourceScope=ref(source),sourceScopeMetadataLeafOnly=False,stagedAcceptance=ref(final/'acceptance.json'),stageBrowserPassed=True,stagedCandidateViews=4,stagedRetainedOwnViews=48,retainedUids=read(HERE/'accepted'/final.name/'browser-config.json')['nativeSupportUidsByModel']['landsd/304714:0'],preparedLiveAdapter=ref(HERE/'xl-terrain-recovery-20261010-no1-garden-live-install-v2.py'),publication=False,newlyInstalled=0,declarationOnly=True,rootIndependentRecursiveVerificationRequired=True)
save(OUT/'declared-scope.json',scope);print(len(paths))
