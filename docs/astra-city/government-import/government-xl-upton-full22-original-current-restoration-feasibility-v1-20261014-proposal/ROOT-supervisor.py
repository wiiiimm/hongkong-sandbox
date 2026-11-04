from pathlib import Path
import sys,json,hashlib,subprocess,traceback
ROOT=Path('/home/williamli/projects/wiiiimm/hongkong-sandbox/.claude/worktrees/astra-hong-kong-city')
HERE=ROOT/'source-scripts/city/government-import';sys.path.insert(0,str(HERE))
from run import read,save,connect,reservations
import upton_full22_original_current_restoration_feasibility_v1_20261014 as caller
assert hashlib.sha256(Path(caller.__file__).read_bytes()).hexdigest()=='798f978b087b2d44646033a08a85d21a7d97e0aa2031d9be944c74b887887464'
validation=read(caller.PROPOSAL/'ROOT-validation-v1/summary.json');assert validation['passed']and validation['caller']==caller.ref(Path(caller.__file__))
assert not caller.DOC.exists()and not caller.LOCAL.exists()
result=subprocess.run([sys.executable,str(Path(caller.__file__)),'--test-full22-original-current-restoration-only'],cwd=ROOT)
terminal={'actualWorkerExitCode':result.returncode,'newlyInstalled':0,'terrainEmitted':False,'currentAcceptance':False}
try:
 assert result.returncode==0
 receipt=read(caller.DOC/'result.json')
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for ref in receipt['evidenceRefs']:assert hashlib.sha256((ROOT/ref['path']).read_bytes()).hexdigest()==ref['sha256']
 assert not reservations.owns(read(caller.LEASE))
 diagnostic=read(caller.DOC/'complete-full22-original-current-restoration-feasibility.json.gz')
 coverage=read(caller.DOC/'complete22-whole-gap-current-counterpart-plane-coverage.json.gz')
 assert len(coverage['rows'])==22 and len(diagnostic['complete1911BasicRows'])==1911
 assert sum('wholeCurrentMaskFeasibility'in r for r in diagnostic['complete1911BasicRows'])==52
 assert len(diagnostic['actors'])==4 and all(len(r['worlds'])==4 for r in diagnostic['actors'])
 assert not diagnostic['physicalAccepted']and not diagnostic['installationApproved']
 terminal.update(jobId=receipt['jobId'],exactNeonReadback=True,allEvidenceHashesVerified=True,evidenceRefCount=len(receipt['evidenceRefs']),leaseReleased=True,whole22ClosedCoverage=diagnostic['allWholeClosedResidualsCoveredByAuthenticCurrent'],currentMaskCompatibilityWithoutUncredited=diagnostic['wholeCurrentMaskOrdinaryCompatibilityWithoutUncredited'])
except Exception as error:
 terminal['rootVerificationFailure']={'type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc()}
 save(caller.PROPOSAL/'ROOT-worker-terminal.json',terminal);print(json.dumps(terminal),flush=True);raise
save(caller.DOC/'ROOT-VERIFIED.json',terminal);print(json.dumps(terminal),flush=True)
