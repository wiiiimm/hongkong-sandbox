"""Final closed HKDI source declaration with all exact archival restorations."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
BASE=ROOT/'docs/astra-city/government-import';OLD=BASE/'xl-terrain-recovery-20261010-hkdi-block-b-source-scope-declaration-v2';DOC=BASE/'xl-terrain-recovery-20261010-hkdi-block-b-source-scope-declaration-v3'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
assert not DOC.exists();prior=read(OLD/'declared-scope.json');paths=set(prior['closedPaths'])
for name in ['xl-terrain-recovery-20261010-hkdi-missing-historical-source-inventory-v2','xl-terrain-recovery-20261010-hkdi-all-prefix-exact-historical-tin-restore-v3']:
 d=BASE/name;assert d.is_dir();paths.update(str(p.relative_to(ROOT))for p in d.iterdir()if p.is_file());paths.add(str((HERE/(name+'.py')).relative_to(ROOT)))
restore=read(BASE/'xl-terrain-recovery-20261010-hkdi-all-prefix-exact-historical-tin-restore-v3/restored-inputs.json');assert restore['allEnumeratedOriginalFilesRestored']is True and not restore['remaining']and restore['numericalExceptions']==0
paths.add(str(Path(__file__).relative_to(ROOT)));paths.add(str((OLD/'declared-scope.json').relative_to(ROOT)))
out=dict(prior,closedPaths=sorted(paths),closedExplicitPaths=sorted(paths),presentFileBindings=[ref(ROOT/p)for p in sorted(paths)],metadataLeafJsonPointers=[],exactHistoricalOriginalFilesRestored=12+len(restore['files']),sourceClosureRuleChanged=False,allPrefixesExactHistoricalAcquisitionClosed=True);save(DOC/'declared-scope.json',out);print(dict(paths=len(paths),historicalOriginalPathsRestored=12+len(restore['files']),metadataExceptionsAdded=0),flush=True)
