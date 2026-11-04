"""DRAFT typed source visual evidence freezer; no role/root/review acceptance."""
import argparse,json
from pathlib import Path
from run import ROOT,HERE,read,connect,reservations
import west_wing26195_current_typed_visual_surface_roles_draft_v1_20261012 as P

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--lease-file',required=True);args=parser.parse_args();valid=P.validation();lease=read(Path(args.lease_file));assert reservations.owns(lease);receipt,scope,mount,visual,finite,graph=P.inputs();d=read(P.DOC/'diagnostic.json.gz');assert d['sourceOnly']and not d['physicalAccepted']and not d['installationApproved']and d['legacyDeliveryAnd15ReviewsUnchanged']and d['noGroundContactCorridorOrBandArithmeticRerun'];assert d['currentManifest']==scope['currentManifest']and d['allFourStreamBindings']==finite['allFourStreamBindings'];assert d['typedSourceVisualRoleContext']==P.calculate(mount,visual,finite,graph);r=d['typedSourceVisualRoleContext'];assert r['sourceVisualOnlyBodies']==[108,113]and len(r['remaining116BodyRolesUnqualified'])==116 and r['all118BodyObligationsRetained']and not any(r[k]for k in ['fullRoleReconciliationAccepted','bodySupportAccepted','gradeRootAccepted','physicalAccepted','installationApproved','legacyAcceptanceBackfillAllowed','sourceGeometryChanges'])
 walker=P.M.D.S.G.P.F.module(HERE/'parkview_block17_freeze_current_source_evidence_20261011.py','westwingtypedvisualfreeze');paths=set();walker.local_imports(Path(__file__),paths);walker.local_imports(Path(P.__file__),paths)
 for e in receipt['evidenceRefs']+d['evidenceRefs']+valid:assert P.ref(ROOT/e['path'])==e;paths.add(ROOT/e['path'])
 paths.add(P.DOC/'diagnostic.json.gz');paths.add(Path(args.lease_file));paths.update(p for p in P.LOCAL.rglob('*')if p.is_file());paths.update(p for p in P.PROPOSAL.iterdir()if p.is_file());P.inputs();assert reservations.owns(lease)
 result=walker.F.freeze(P.BATCH,'two-pinned-provider-authored-visual-surface-context-no-whole-body-root-physical-credit',sorted(paths),dict(uids=[P.H.UID],sourceOnly=True,physicalAccepted=False,bodySupportAccepted=False,gradeRootAccepted=False,installationApproved=False,modelReviewWrites=0,sourceVisualOnlyBodies=[108,113],completeFaces=46918,completeBodies=118,remainingBodyRoles=116,allRawNegativesRetained=True))
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(result['jobId'],)).fetchone()==('complete',result)
 for e in result['evidenceRefs']:assert P.ref(ROOT/e['path'])==e
 P.inputs();assert reservations.owns(lease);print(json.dumps(dict(jobId=result['jobId'],allRefs=len(result['evidenceRefs']),physicalAccepted=False)),flush=True)
if __name__=='__main__':main()
