"""DRAFT diagnostic freezer. Association context cannot approve any body/root."""
import argparse,json
from pathlib import Path
from run import ROOT,HERE,read,connect,reservations,digest
import west_wing26195_visual_mounting_interface_context_draft_v1_20261012 as P

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--lease-file',required=True);args=parser.parse_args();valid=P.validation();lease=read(Path(args.lease_file));assert reservations.owns(lease);receipt,scope,worlds,finite,graph=P.inputs();d=read(P.DOC/'diagnostic.json.gz');assert d['sourceOnly']and d['completeFaces']==46918 and d['completeOriginalBodies']==118 and d['completeGroundFaces']==3240
 assert all(d[k]for k in ['all42OrdinaryFailuresAnd443StrictUncertifiedRetained','legacyDeliveryAnd15ReviewsUnchanged','unchangedOpeningV3TwoCycleRejectionPreserved','literalBody113PointOnlyNegativePreserved','allPrior17Plus24PlusSeed153PathsPreserved','noFiniteGradeCorridorOrContactCensusRerun']);assert not any(d[k]for k in ['physicalAccepted','bodySupportAccepted','gradeRootAccepted','installationApproved','sourceGeometryChanges','terrainGeometryChanges']);assert d['currentManifest']==scope['currentManifest']and d['allFourStreamBindings']==finite['allFourStreamBindings']and set(d['distinctBodyAssociationContexts'])=={x['proofTupleSHA256']for x in finite['allFourStreamBindings'].values()}
 checked=set()
 for mode,world in worlds.items():
  b=finite['allFourStreamBindings'][mode];assert digest(world.tobytes())==b['wholeWorldSHA256'];key=b['proofTupleSHA256']
  if key in checked:continue
  checked.add(key);r=d['distinctBodyAssociationContexts'][key];assert r==json.loads(json.dumps(P.calculate(world,key,finite,graph)));assert r['bodies']['108']['openingV3RejectionPreserved']and r['bodies']['108']['higherCompleteBoundaryRetainedUnfilled'];assert r['bodies']['113']['mountingEdgeDesignationNotAutomatic'];assert not any(x['visualRoleAccepted']or x['structuralRootCredit']or x['structuralBridgeCredit']or x['physicalAccepted']or x['installationApproved']for x in r['bodies'].values())
 walker=P.D.S.G.P.F.module(HERE/'parkview_block17_freeze_current_source_evidence_20261011.py','westwingtwohostfreeze');paths=set();walker.local_imports(Path(__file__),paths);walker.local_imports(Path(P.__file__),paths)
 for e in receipt['evidenceRefs']+d['evidenceRefs']+valid:assert P.ref(ROOT/e['path'])==e;paths.add(ROOT/e['path'])
 paths.add(P.DOC/'diagnostic.json.gz');paths.add(Path(args.lease_file));paths.update(p for p in P.LOCAL.rglob('*')if p.is_file());paths.update(p for p in P.PROPOSAL.iterdir()if p.is_file());P.inputs();assert reservations.owns(lease)
 result=walker.F.freeze(P.BATCH,'two-original-visual-surface-mounting-interface-context-no-root-support-credit',sorted(paths),dict(uids=[P.D.S.G.P.F.UID],sourceOnly=True,physicalAccepted=False,bodySupportAccepted=False,gradeRootAccepted=False,installationApproved=False,modelReviewWrites=0,completeFaces=46918,completeBodies=118,completeGroundFaces=3240,allRawNegativesRetained=True))
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(result['jobId'],)).fetchone()==('complete',result)
 for e in result['evidenceRefs']:assert P.ref(ROOT/e['path'])==e
 P.inputs();assert reservations.owns(lease);print(json.dumps(dict(jobId=result['jobId'],allRefs=len(result['evidenceRefs']),typedAcceptanceRouteEstablished=False)),flush=True)
if __name__=='__main__':main()
