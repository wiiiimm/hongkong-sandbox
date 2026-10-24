"""Recover the exact completed Neon receipt after a tuple/list readback mismatch.

Read-only database access: no job replay, evidence alteration or acceptance.
"""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-fung-yip-full-native-domain-exact-boundary-counterexample-v3-20261024'
def main():
 out=BASE/BATCH;assert not(out/'result.json').exists();summary=read(out/'summary.json')
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');rows=db.execute('SELECT id,status,result FROM astra_modelling.jobs WHERE batch=%s AND stage=%s',(BATCH,'exact-unchanged-source-boundary-guard-counterexample')).fetchall()
 assert len(rows)==1
 jid,state,result=rows[0];assert state=='complete'and result['jobId']==jid
 assert all(result[k]==v for k,v in summary.items())
 assert result['installationApproved']is False and result['allFiniteSegmentsStrictlyOutsideExistingGuard']is True
 for ref in result['evidenceRefs']:assert digest((ROOT/ref['path']).read_bytes())==ref['sha256']
 save(out/'result.json',result)
 save(out/'neon-sync.json',dict(jobId=jid,resultVerified=True,readOnlyRecovery=True,originalReadbackFailure='Python tuple/list mismatch for literalSharedChain; saved receipt is the exact completed database JSON',producer=str(Path(__file__).relative_to(ROOT)),producerSHA256=digest(Path(__file__).read_bytes())))
 print(dict(jobId=jid,verified=True,distance=summary['diagnosticDistanceM']),flush=True)
if __name__=='__main__':main()
