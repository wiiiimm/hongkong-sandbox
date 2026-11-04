"""Preserve failed v1, passed v2, and targeted exact-census reuse v3 runs.

Actual file bindings are captured after the completed unchanged-byte executions;
this writer does not relabel old runs as tests on new kernel versions.
"""
from pathlib import Path
import importlib.util,json,shutil,re
from run import ROOT,HERE,read,save,digest
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261011-elements998-composition-code-validation-v2';DOC=BASE/BATCH
UIDS=['landsd/204145:0','landsd/204143:0']
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();versions=[];paths=[Path(__file__)]
 for v,count,status in [(1,14,'failed-positive-fixture-local-global-representation'),(2,16,'passed-local-global-correction'),(3,3,'passed-exact-immutable-census-reuse')]:
  kernel=HERE/f'elements998_complete_original_role_composition_v{v}_20261011.py';test=HERE/f'test_elements998_complete_original_role_composition_v{v}_20261011.py';log=Path(f'/tmp/elements998-complete-original-role-composition-v{v}-tests-20261011.log');text=log.read_text();assert re.search(r'Ran '+str(count)+r' tests in [0-9.]+s',text)
  if v==1:assert text.endswith('FAILED (failures=1)\n')and "native['ownedFace']in bodies[seed]"in text
  else:assert text.endswith('OK\n')and 'FAILED'not in text
  dest=DOC/'logs'/log.name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(log,dest);assert log.read_bytes()==dest.read_bytes();paths.extend([kernel,test,dest]);versions.append(dict(version=v,kernel=ref(kernel),test=ref(test),log=ref(dest),executedTestCount=count,result=status,fileBindingsRecordedAfterCompletedExecution=True,previousRunNeverRelabelledAsNewVersion=True))
 save(DOC/'validation-versions.json',dict(uids=UIDS,versions=versions,initialFailurePreserved=True,sourceGeometryChanges=0,thresholdChanges=0,noCurrentOrInstallationCredit=True));paths.append(DOC/'validation-versions.json')
 spec=importlib.util.spec_from_file_location('freeze_elements_composition_validation',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 m.freeze(BATCH,'completed-exact-elements-composition-version-bound-test-runs-v2',paths,dict(uids=UIDS,sourceGeometryChanges=0,scriptChecksPassed=True,initialFailedVersionPreserved=True,currentAcceptance=False,installationApproved=False,newlyInstalled=0))
if __name__=='__main__':main()
