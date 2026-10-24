"""DRAFT source-only complete current body0 candidate certificate freezer."""
import argparse,json
from pathlib import Path
from run import ROOT,HERE,read,connect,reservations
import west_wing26195_current_body0_source_bound_candidate_role_draft_v2_20261012 as P

def main():
 a=argparse.ArgumentParser();a.add_argument('--lease-file',required=True);a=a.parse_args();valid=P.validation();lease=read(Path(a.lease_file));assert reservations.owns(lease);scope,receipts,certificate=P.inputs();d=read(P.DOC/'diagnostic.json.gz');assert d['sourceOnly']and not d['physicalAccepted']and not d['installationApproved']and d['legacyDeliveryAnd15ReviewsUnchanged']and d['noCompletedNumericArithmeticRerun'];assert d['currentManifest']==scope['currentManifest']and d['allFourStreamBindings']==certificate['allFourStreamBindings'];assert d['body0CandidateRoleCertificate']==certificate and d['completeSourceFaces']==46918 and d['completeSourceBodies']==118 and d['raw42OrdinaryFailuresAnd443StrictWarningsRetained'];assert not any(d[k]for k in ['modelReviewWrites','sourceGeometryChanges','terrainGeometryChanges']);assert not any(certificate[k]for k in ['groundRootAccepted','bodySupportAccepted','physicalAccepted','installationApproved','legacyAcceptanceBackfillAllowed','sourceGeometryChanges'])
 walker=P.T.M.D.S.G.P.F.module(HERE/'parkview_block17_freeze_current_source_evidence_20261011.py','westwingbody0candidatefreeze');paths=set();walker.local_imports(Path(__file__),paths);walker.local_imports(Path(P.__file__),paths)
 refs=valid+d['evidenceRefs']+[e for r in receipts for e in r['evidenceRefs']]
 for e in refs:assert P.ref(ROOT/e['path'])==e;paths.add(ROOT/e['path'])
 paths.add(P.DOC/'diagnostic.json.gz');paths.add(Path(a.lease_file));paths.update(p for p in P.LOCAL.rglob('*')if p.is_file());paths.update(p for p in P.PROPOSAL.iterdir()if p.is_file());codes=[P.ref(p)for p in sorted(paths)];P.fence(scope,lease,codes);P.inputs()
 result=walker.F.freeze(P.BATCH,'complete-current-source-bound-body0-candidate-grade-role-no-root-physical-credit',sorted(paths),dict(uids=[P.H.UID],sourceOnly=True,completeFaces=46918,completeBodies=118,completeBody0Faces=5062,completeGradeWallFaces=42,body0SourceRoleCandidateQualified=True,remainingBodyObligations=117,groundRootAccepted=False,physicalAccepted=False,installationApproved=False,modelReviewWrites=0,sourceGeometryChanges=0,terrainGeometryChanges=0))
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(result['jobId'],)).fetchone()==('complete',result)
 for e in result['evidenceRefs']:assert P.ref(ROOT/e['path'])==e
 P.fence(scope,lease,codes);P.inputs();print(json.dumps(dict(jobId=result['jobId'],allRefs=len(result['evidenceRefs']),groundRootAccepted=False,physicalAccepted=False)),flush=True)
if __name__=='__main__':main()
