"""DRAFT saved-contact conditional typed-role source-only freezer."""
import argparse,json
from pathlib import Path
from run import ROOT,HERE,read,connect,reservations
import west_wing26195_current_remaining_bodies_existing_contact_policy_draft_v2_20261012 as Q

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--lease-file',required=True);parser.add_argument('--expected-body0-result-sha',required=True);args=parser.parse_args();valid=Q.validation();lease=read(Path(args.lease_file));assert reservations.owns(lease);scope,receipt,result=Q.inputs(args.expected_body0_result_sha);d=read(Q.DOC/'diagnostic.json.gz');assert d['conditionalTypedGraph']==result and d['currentManifest']==scope['currentManifest']and d['allFourStreamBindings']==result['allFourStreamBindings'];assert d['sourceOnly']and d['noContactOrGroundArithmeticRerun']and d['legacyDeliveryAnd15ReviewsUnchanged'];assert not any(d[k]for k in ['physicalAccepted','installationApproved','modelReviewWrites','sourceGeometryChanges','terrainGeometryChanges']);assert not any(result[k]for k in ['actualIndependentGroundRootQualified','bodySupportAccepted','physicalAccepted','installationApproved'])
 walker=Q.P.T.M.D.S.G.P.F.module(HERE/'parkview_block17_freeze_current_source_evidence_20261011.py','westwingexistingcontactfreeze');paths=set();walker.local_imports(Path(__file__),paths);walker.local_imports(Path(Q.__file__),paths)
 for e in valid+d['evidenceRefs']+receipt['evidenceRefs']:assert Q.ref(ROOT/e['path'])==e;paths.add(ROOT/e['path'])
 paths.add(Q.DOC/'diagnostic.json.gz');paths.add(Path(args.lease_file));paths.update(p for p in Q.LOCAL.rglob('*')if p.is_file());paths.update(p for p in Q.PROPOSAL.iterdir()if p.is_file());codes=[Q.ref(p)for p in sorted(paths)];Q.P.fence(scope,lease,codes)
 saved=walker.F.freeze(Q.BATCH,'complete-saved-positive-dimensional-current-body-contact-typed-context-no-root-acceptance',sorted(paths),dict(uids=[Q.H.UID],sourceOnly=True,completeFaces=46918,completeBodies=118,conditionalNonvisualReachableBodies=116,visualNonbridgingBodies=[108,113],actualGroundRootQualified=False,physicalAccepted=False,installationApproved=False,modelReviewWrites=0,sourceGeometryChanges=0,terrainGeometryChanges=0))
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(saved['jobId'],)).fetchone()==('complete',saved)
 for e in saved['evidenceRefs']:assert Q.ref(ROOT/e['path'])==e
 Q.P.fence(scope,lease,codes);Q.inputs(args.expected_body0_result_sha);print(json.dumps(dict(jobId=saved['jobId'],allRefs=len(saved['evidenceRefs']),physicalAccepted=False)),flush=True)
if __name__=='__main__':main()
