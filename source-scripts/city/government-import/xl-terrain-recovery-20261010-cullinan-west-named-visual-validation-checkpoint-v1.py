"""Fence successful adversarial tests and immutable original failed branch."""
import importlib.util
from pathlib import Path
from run import ROOT,HERE,read,save,digest
BATCH='xl-terrain-recovery-20261010-cullinan-west-named-visual-validation-checkpoint-v1';DOC=ROOT/'docs/astra-city/government-import'/BATCH
NAMED=ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261010-cullinan-west-three-named-original-visual-details-v2'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();test=Path('/tmp/cullinan-original-named-visual-details-v2-tests-20261010.log').read_bytes();failure=Path('/tmp/cullinan-west-three-named-original-visual-details-v1-20261010.log').read_bytes();assert b'Ran 12 tests' in test and test.rstrip().endswith(b'OK');assert b'AssertionError' in failure and b'anchorpoints' in failure
 DOC.mkdir(parents=True);(DOC/'actual-adverse-tests.log').write_bytes(test);(DOC/'failed-v1-real-source.log').write_bytes(failure)
 refs=[ref(p)for p in [Path(__file__),HERE/'test_cullinan_original_named_visual_details_v2_20261010.py',HERE/'cullinan_original_named_visual_details_v1_20261010.py',HERE/'cullinan_original_named_visual_details_v2_20261010.py',HERE/'xl-terrain-recovery-20261010-cullinan-west-three-named-original-visual-details-v1.py',HERE/'xl-terrain-recovery-20261010-cullinan-west-three-named-original-visual-details-v2.py',NAMED/'diagnostic.json.gz',NAMED/'result.json',DOC/'actual-adverse-tests.log',DOC/'failed-v1-real-source.log']]
 save(DOC/'diagnostic.json',dict(uids=['landsd/262871:0','landsd/161931:0','landsd/120158:0'],actualAdverseTests=12,testsPassed=True,oldFailedBranchPreserved=True,cause='Part295 free slanted front bottom vertex is lower than the authored mounted back-chain endpoint; v2 uses exact original back-chain endpoints, no tolerance or extreme-height credit.',unchangedExistingMountingBandM=.1,sourceGeometryChanges=0,nativeReacceptance=False,installationApproved=False,evidenceRefs=refs))
 s=importlib.util.spec_from_file_location('f',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.freeze(BATCH,'immutable-source-only-cullinan-named-visual-twelve-actual-adverse-tests-v1',[ROOT/r['path']for r in refs]+[DOC/'diagnostic.json'],dict(uids=['landsd/262871:0','landsd/161931:0','landsd/120158:0'],testsPassed=True,actualAdverseTests=12,sourceGeometryChanges=0,nativeReacceptance=False,fullAcceptance=False))
if __name__=='__main__':main()
