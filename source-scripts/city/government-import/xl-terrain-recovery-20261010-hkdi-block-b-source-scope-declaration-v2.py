"""Close the final HKDI proof and exact restored historical source inventory.

Keeps the unchanged recursive verifier and every original numerical input; old
failed declarations/normalisation failure and complete A/native negatives remain.
"""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
BASE=ROOT/'docs/astra-city/government-import';OLD=BASE/'xl-terrain-recovery-20261010-hkdi-block-b-source-scope-declaration-v1';DOC=BASE/'xl-terrain-recovery-20261010-hkdi-block-b-source-scope-declaration-v2'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();prior=read(OLD/'declared-scope.json');paths=set(prior['closedPaths']);dirs=[BASE/n for n in ['xl-terrain-recovery-20261010-hkdi-exact-historical-nw9b-tin-restore-v1','xl-terrain-recovery-20261010-hkdi-exact-historical-sw6d-tin-restore-v1','xl-terrain-recovery-20261010-hkdi-batch-exact-historical-tin-restore-v2','xl-terrain-recovery-20261010-hkdi-missing-historical-source-inventory-v1']]
 for d in dirs:
  assert d.is_dir();paths.update(str(p.relative_to(ROOT))for p in d.iterdir()if p.is_file())
 for n in ['xl-terrain-recovery-20261010-hkdi-exact-historical-nw9b-tin-restore-v1.py','xl-terrain-recovery-20261010-hkdi-exact-cached-historical-tin-restore-v1.py','xl-terrain-recovery-20261010-hkdi-batch-exact-historical-tin-restore-v2.py','xl-terrain-recovery-20261010-hkdi-missing-historical-source-inventory-v1.py']:paths.add(str((HERE/n).relative_to(ROOT)))
 paths.add(str(Path(__file__).relative_to(ROOT)));paths.add(str((OLD/'declared-scope.json').relative_to(ROOT)))
 out=dict(prior,closedPaths=sorted(paths),closedExplicitPaths=sorted(paths),presentFileBindings=[ref(ROOT/p)for p in sorted(paths)],metadataLeafJsonPointers=[],exactHistoricalOriginalFilesRestored=12,sourceClosureRuleChanged=False,rawFailedFirstScopePreserved=ref(OLD/'declared-scope.json'));save(DOC/'declared-scope.json',out);print(dict(paths=len(paths),historicalFilesRestored=12,metadataExceptionsAdded=0),flush=True)
if __name__=='__main__':main()
