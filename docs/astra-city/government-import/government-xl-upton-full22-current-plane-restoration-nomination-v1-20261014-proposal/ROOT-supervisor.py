from pathlib import Path
import sys,json,hashlib,subprocess,traceback
ROOT=Path('/home/williamli/projects/wiiiimm/hongkong-sandbox/.claude/worktrees/astra-hong-kong-city');HERE=ROOT/'source-scripts/city/government-import';sys.path.insert(0,str(HERE))
from run import read,save,connect,reservations
import upton_full22_current_plane_restoration_nomination_v1_20261014 as caller
assert hashlib.sha256(Path(caller.__file__).read_bytes()).hexdigest()=='2ddcc6f7226ef8a64da861780fc4d4da63585e8a253a20646bb555b110a9dc4f'
v=read(caller.PROPOSAL/'ROOT-validation-v1/summary.json');assert v['passed']and v['caller']==caller.ref(Path(caller.__file__))
assert not caller.DOC.exists()and not caller.LOCAL.exists()
r=subprocess.run([sys.executable,str(Path(caller.__file__)),'--nominate-full22-current-plane-restoration-only'],cwd=ROOT)
terminal={'actualWorkerExitCode':r.returncode,'newlyInstalled':0,'currentAcceptance':False}
try:
 assert r.returncode==0
 receipt=read(caller.DOC/'result.json')
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for ref in receipt['evidenceRefs']:assert hashlib.sha256((ROOT/ref['path']).read_bytes()).hexdigest()==ref['sha256']
 assert not reservations.owns(read(caller.LEASE))
 nominee=read(caller.DOC/'private-full22-current-plane-restoration-nomination.json.gz')
 assert nominee['all11580ExistingFacetsPreserved']and nominee['all68ProtectedLiteralTripletsUnchanged']
 assert nominee['completeNewCandidateFacets']==len(nominee['candidateRawPositionTriplets'])and not nominee['physicalAccepted']and not nominee['installationApproved']
 terminal.update(jobId=receipt['jobId'],exactNeonReadback=True,allEvidenceHashesVerified=True,evidenceRefCount=len(receipt['evidenceRefs']),leaseReleased=True,privateCandidateFacets=nominee['completeNewCandidateFacets'],addedFacets=len(nominee['addedCandidateFaceIDs']),privateCandidateRawSHA256=nominee['completeNewRawCandidateSHA256'])
except Exception as error:
 terminal['rootVerificationFailure']={'type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc()};save(caller.PROPOSAL/'ROOT-worker-terminal.json',terminal);print(json.dumps(terminal),flush=True);raise
save(caller.DOC/'ROOT-VERIFIED.json',terminal);print(json.dumps(terminal),flush=True)
