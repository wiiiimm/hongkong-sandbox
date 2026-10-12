"""DRAFT v3 receipt-only explicit actual log lineage freezer; no arithmetic."""
import argparse,json
from pathlib import Path
from run import ROOT,HERE,read,connect,reservations
import west_wing26195_body0_candidate_log_lineage_receipt_recovery_draft_v3_20261012 as Q

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--lease-file',required=True);args=parser.parse_args();lease=read(Path(args.lease_file));assert reservations.owns(lease);scope,certificate,paths=Q.inputs();d=read(Q.DOC/'receipt-lineage.json');assert d['body0CandidateRoleCertificate']==certificate and d['currentManifest']==scope['currentManifest'];assert d['oldPostfreezeExitCode']==1 and d['exactOld1602UnchangedRefs']and d['sourceOnly']and d['noNumericOrSourceRoleRecomputation']and not d['physicalAccepted']and not d['installationApproved']
 assert d['oldCompletedReceipt']==Q.ref(Q.P.DOC/'result.json');assert d['soleHistoricalLog']['originalPath']==Q.LOG_PATH and d['soleHistoricalLog']['historicalSHA256']==Q.LOG_SHA and d['soleHistoricalLog']['prefixBytes']==132 and d['soleHistoricalLog']['notRestoredToOriginalPath'];assert d['soleHistoricalLog']['actualStreamPrefix']==Q.ref(Q.P.PROPOSAL/'actual-stream-frozen-prefix-evidence-v2.log') and d['soleHistoricalLog']['fullTerminalStream']==Q.ref(HERE/'execution-logs'/f'{Q.P.BATCH}-terminal.log')
 walker=Q.P.T.M.D.S.G.P.F.module(HERE/'parkview_block17_freeze_current_source_evidence_20261011.py','westwingbody0logrecoveryfreeze');walker.local_imports(Path(__file__),paths);walker.local_imports(Path(Q.__file__),paths);paths.update(ROOT/e['path']for e in Q.P.validation());paths.update(p for p in Q.PROPOSAL.iterdir()if p.is_file());codes=[Q.ref(p)for p in sorted(paths)];Q.P.fence(scope,lease,codes);paths.add(Q.DOC/'receipt-lineage.json');paths.add(Path(args.lease_file))
 result=walker.F.freeze(Q.BATCH,'receipt-only-actual-stream-prefix-history-recovery-no-new-role-or-physical-credit',sorted(paths),dict(uids=[Q.P.H.UID],sourceOnly=True,noNumericRecomputation=True,oldJobId=Q.OLD_JOB,oldPostfreezeExitCode=1,completeFaces=46918,completeBodies=118,body0SourceRoleCandidateQualified=True,gradeRootAccepted=False,physicalAccepted=False,installationApproved=False,modelReviewWrites=0,sourceGeometryChanges=0,terrainGeometryChanges=0))
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(result['jobId'],)).fetchone()==('complete',result)
 for e in result['evidenceRefs']:assert Q.ref(ROOT/e['path'])==e
 Q.P.fence(scope,lease,codes);Q.inputs();print(json.dumps(dict(jobId=result['jobId'],allRefs=len(result['evidenceRefs']),physicalAccepted=False)),flush=True)
if __name__=='__main__':main()
