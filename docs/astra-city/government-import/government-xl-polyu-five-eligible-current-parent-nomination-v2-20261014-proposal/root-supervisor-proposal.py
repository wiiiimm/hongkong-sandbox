"""UNEXECUTED ROOT-only serial v2 launcher/auditor proposal."""
from pathlib import Path
import sys,json,subprocess,hashlib,traceback
ROOT=Path(__file__).resolve().parents[4]
HERE=ROOT/'source-scripts/city/government-import';sys.path.insert(0,str(HERE))
from run import read,save,connect,reservations
import polyu_five_eligible_current_parent_nomination_v2_20261014 as caller

def main():
 assert sys.argv[1:]==['--run-reviewed-v2-only']
 assert hashlib.sha256(Path(caller.__file__).read_bytes()).hexdigest()=='a04b61a23f15b567899760fb90a053610b4163a5dec55a6e97f91b0e3eb5070f'
 caller.prior_terminal_ready(live=True)
 assert not caller.DOC.exists()and not caller.LOCAL.exists()
 completed=subprocess.run([sys.executable,str(Path(caller.__file__)),'--nominate-five-eligible-current-parent-masks-only'],cwd=ROOT)
 terminal=dict(actualWorkerExitCode=completed.returncode,newlyInstalled=0,currentAcceptance=False)
 try:
  assert completed.returncode==0
  receipt=read(caller.DOC/'result.json')
  with connect()as db:
   db.execute('SET TRANSACTION READ ONLY')
   assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  for q in receipt['evidenceRefs']:assert hashlib.sha256((ROOT/q['path']).read_bytes()).hexdigest()==q['sha256']
  assert not reservations.owns(read(caller.LEASE))
  diagnostic=read(caller.DOC/'complete-five-mask-partition-diagnostic.json.gz')
  assert len(diagnostic['all25AffectedUIDs'])==25 and len(diagnostic['all51Resources'])==51
  assert not diagnostic['currentAcceptance']and not diagnostic['physicalAccepted']
  assert receipt['unresolved']==len(diagnostic['unresolved'])
  candidate=caller.DOC/'private-five-mask-current-parent-nomination.json.gz'
  assert candidate.exists()==(receipt['unresolved']==0)
  lineage=read(caller.DOC/'prefix-resume-lineage.json')
  assert lineage['reusedPartitionRows']==832 and lineage['reconstructedCandidateFaces']==1485 and lineage['actualPrefixPartitionCalls']==0
  terminal.update(jobId=receipt['jobId'],exactNeonReadback=True,allEvidenceHashesVerified=True,evidenceRefCount=len(receipt['evidenceRefs']),leaseReleased=True,unresolved=receipt['unresolved'],privateCandidateEmitted=candidate.exists(),reusedOriginalPrefixRows=832)
  if candidate.exists():
   data=read(candidate);assert len(diagnostic['oldMappings'])==3214 and len(diagnostic['parentMappings'])==12
   assert not data['physicalAccepted']and not data['installationApproved']and data['newlyInstalled']==0
   terminal['privateCandidateFacets']=len(data['newNativeMesh']['index'])//3
 except Exception as e:
  terminal['rootVerificationFailure']=dict(type=type(e).__name__,message=str(e),traceback=traceback.format_exc())
  save(caller.PROPOSAL/'ROOT-worker-terminal.json',terminal);print(json.dumps(terminal),flush=True);raise
 save(caller.DOC/'ROOT-VERIFIED.json',terminal);print(json.dumps(terminal),flush=True)

if __name__=='__main__':main()
