from pathlib import Path
import sys,json,subprocess,hashlib,traceback
ROOT=Path('/home/williamli/projects/wiiiimm/hongkong-sandbox/.claude/worktrees/astra-hong-kong-city')
HERE=ROOT/'source-scripts/city/government-import';sys.path.insert(0,str(HERE))
from run import read,save,connect,reservations
import polyu_five_eligible_current_parent_nomination_v1_20261014 as caller
assert hashlib.sha256(Path(caller.__file__).read_bytes()).hexdigest()=='2a7a941f828bd9e1ab3d0378c2420aaa5fadef5e26212223c5ca8efc14c9c2e2'
validation=read(caller.PROPOSAL/'ROOT-validation-v1/summary.json');assert validation['passed']and validation['all3214SavedRationalStringPackedIdentitiesVerified']
assert not caller.DOC.exists()and not caller.LOCAL.exists()
completed=subprocess.run([sys.executable,str(Path(caller.__file__)),'--nominate-five-eligible-current-parent-masks-only'],cwd=ROOT)
terminal={'actualWorkerExitCode':completed.returncode,'newlyInstalled':0,'currentAcceptance':False}
try:
 assert completed.returncode==0
 receipt=read(caller.DOC/'result.json')
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for ref in receipt['evidenceRefs']:assert hashlib.sha256((ROOT/ref['path']).read_bytes()).hexdigest()==ref['sha256']
 assert not reservations.owns(read(caller.LEASE))
 diagnostic=read(caller.DOC/'complete-five-mask-partition-diagnostic.json.gz')
 assert len(diagnostic['oldMappings'])==3214 and len(diagnostic['parentMappings'])==12
 assert len(diagnostic['all25AffectedUIDs'])==25 and len(diagnostic['all51Resources'])==51
 assert not diagnostic['currentAcceptance']and not diagnostic['physicalAccepted']
 assert receipt['unresolved']==len(diagnostic['unresolved'])
 candidate=caller.DOC/'private-five-mask-current-parent-nomination.json.gz'
 assert candidate.exists()==(receipt['unresolved']==0)
 terminal.update(jobId=receipt['jobId'],exactNeonReadback=True,allEvidenceHashesVerified=True,evidenceRefCount=len(receipt['evidenceRefs']),leaseReleased=True,unresolved=receipt['unresolved'],privateCandidateEmitted=candidate.exists())
 if candidate.exists():
  data=read(candidate);terminal['privateCandidateFacets']=len(data['newNativeMesh']['index'])//3
  assert not data['physicalAccepted']and not data['installationApproved']and data['newlyInstalled']==0
except Exception as error:
 terminal['rootVerificationFailure']={'type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc()}
 save(caller.PROPOSAL/'ROOT-worker-terminal.json',terminal)
 print(json.dumps(terminal),flush=True)
 raise
save(caller.DOC/'ROOT-VERIFIED.json',terminal)
print(json.dumps(terminal),flush=True)
