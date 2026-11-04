"""UNEXECUTED acquisition-only compatibility of full selective13 NEW collar.
No DB, lease, source decode, terrain construction or whole finite replay.
"""
import sys,json,importlib.util
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,digest
from southside_selective13_parent_retention_affine_collar_draft_v1_20261013 import prepare_branches,complete_changed_projection_domains
from southside_saved_finite_piece_guard_domain_v1_20261012 import restrict_saved_piece,rational_point
from southside_saved_piece_closed_bounds_schedule_v1_20261012 import prepare_domains,saved_piece_bounds,nominate_domains
D=ROOT/'docs/astra-city/government-import/government-xl-southside-private-authentic-terrain-draft-v2-20261012';P=D/'selective13-parent-restoration-draft-v1';OUT=P/'full-new-collar-saved-piece-compatibility-v1'
CORE=P/'closed-core-preparation-v1/closed-core-preparation.json';AUDIT=P/'readonly-core-preparation-result-audit-v1.json';BASE=ROOT/'docs/astra-city/government-import'
FINITE=BASE/'government-xl-southside-315025-300867-complete-four-stream-current-finite-v1-20261012/diagnostic.json.gz';AUTH=BASE/'government-xl-southside-315025-300867-unfiltered-original-sheets-comparison-v2-20261012/diagnostic.json.gz'
CODE=[Path(__file__),HERE/'southside_selective13_parent_retention_affine_collar_draft_v1_20261013.py',HERE/'test_southside_selective13_parent_retention_affine_collar_draft_v1_20261013.py',HERE/'southside_saved_piece_closed_bounds_schedule_v1_20261012.py',HERE/'southside_saved_finite_piece_guard_domain_v1_20261012.py',HERE/'southside_saved_local_core_parent_adapter_v3_20261012.py',HERE/'southside_exact_private_terrain_adapter_v1_20261012.py',HERE/'exact_original_paired_finite_clearance_20261010.py',HERE/'exact_original_projection_coverage_v2_20261010.py',HERE/'xl-southside-selective13-guard-union-parent-preparation-draft-v1-20261013.py']
def preflight():
 assert digest(CORE.read_bytes())=='34643eec3a1db460d6b0ae0f7c404079fca7e0747d47c511aa55f12c9a9a62ec' and digest(AUDIT.read_bytes())=='d3fdf2b71f4dc83dfd918b76a4feb305060bcc86e0c933045e42f4fcc80d6594'
 core=read(CORE);audit=read(AUDIT);assert audit['all13OriginalUIDsPreserved']and audit['all3653ClosedCoverageProved']and not audit['remainingCollarProved']
 for p,h in core['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h
 module_path=CODE[-1];spec=importlib.util.spec_from_file_location('exact_historical_core_preparation',module_path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);saved=module.preflight()
 assert digest(FINITE.read_bytes())==saved['pins'][str(FINITE.relative_to(ROOT))]and digest(AUTH.read_bytes())==saved['pins'][str(AUTH.relative_to(ROOT))]
 finite,auth=read(FINITE),read(AUTH);assert len(finite['rows'])==len(auth['rows'])==8
 slots=0
 for row in finite['rows']:
  uid,mode=row['uid'],row['arithmetic'];source=saved['source']['rows'][uid];world=np.asarray(source['completeWorldStreams'][mode]['completeWorldTriangles'],dtype='<f8');ground=np.asarray(source['completeDrawnGround'],dtype='<f8')
  assert digest(world.tobytes())==row['completeWholeWorldSHA256']and digest(ground.tobytes())==row['completeCurrentGroundSHA256'];assert [r['sourceFace']for r in row['completeOriginalFaceComparisons']]==list(range(len(world)))
  for r in row['completeOriginalFaceComparisons']:assert digest(world[r['sourceFace']].tobytes())==r['completeOriginalFacetSHA256']
  ar=next(r for r in auth['rows']if r['uid']==uid and r['arithmetic']==mode);assert ar['completeWorldSHA256']==row['completeWholeWorldSHA256'];slots+=len(world)
 assert slots==51560
 validation=P/'immutable-collar-fixtures-v1/validation.json';v=read(validation);assert v['testCount']==8 and v['actualExitCode']==0 and v['allPassed'];log=validation.parent/'tests.log';assert digest(log.read_bytes())==v['testLogSHA256']
 assert v['codePins']=={str(p.relative_to(ROOT)):digest(p.read_bytes())for p in CODE}
 pins={**saved['pins'],**core['inputHashes'],**v['codePins']}
 for p in [CORE,AUDIT,validation,log,P/'FIVE-METRE-COLLAR-DRAFT-METHOD.md']:pins[str(p.relative_to(ROOT))]=digest(p.read_bytes())
 return saved,core,finite,auth,pins

def main():
 saved,core,finite,auth,pins=preflight()
 if '--preflight-only'in sys.argv:print(json.dumps(dict(savedSlots=51560,sourceRows=8,provedCorePrimitives=3653,fixtureCount=8,noDB=True,noLease=True,noTerrainConstruction=True,currentAcceptance=False)));return
 assert '--calculate-collar-compatibility-only'in sys.argv and not OUT.exists()
 branches=prepare_branches(core['completeRawClosedDomainUnion']);domains=complete_changed_projection_domains(branches);prepared=prepare_domains(domains);rows=[];negative=[];unresolved=[];schedule=dict(savedPieces=0,nominatedDomains=0,primitiveStrictDisjoint=0,nonFiniteNotPruned=0)
 for row in finite['rows']:
  uid,mode=row['uid'],row['arithmetic'];ground=[list(map(rational_point,t))for t in saved['source']['rows'][uid]['completeDrawnGround']];ar=next(r for r in auth['rows']if r['uid']==uid and r['arithmetic']==mode);failed=set(ar['allAuthenticatedGroundFailuresRetained']);records=[]
  for facet in row['completeOriginalFaceComparisons']:
   c=facet['currentDrawnGroundComparison']
   if c['completeFiniteOrdinaryBoundProved']:continue
   if c['paired']is None:unresolved.append(dict(uid=uid,arithmetic=mode,sourceFace=facet['sourceFace'],savedFullRecord=facet,unresolvedMissingPairedPieces=True));continue
   for i,piece in enumerate(c['paired']['allExactFiniteSourceGroundPieces']):
    ground_face=ground[piece['originalGroundFace']];restrict_saved_piece(piece,ground_face,[])
    nominated,nom=nominate_domains(saved_piece_bounds(piece),prepared);schedule['savedPieces']+=1;schedule['nominatedDomains']+=len(nominated);schedule['primitiveStrictDisjoint']+=nom['primitiveStrictDisjoint'];schedule['nonFiniteNotPruned']+=int(nom['nonFiniteRecordNotPruned'])
    if not nominated:continue
    proof=restrict_saved_piece(piece,ground_face,nominated);record=dict(sourceFace=facet['sourceFace'],savedPieceID=i,authenticWholeFacetFinitePositive=facet['sourceFace']not in failed,restriction=proof);records.append(record)
    if record['authenticWholeFacetFinitePositive']:
     for restriction in proof['restrictions']:
      if not restriction['unchangedOrdinaryBoundProvedOnRestriction']:negative.append(dict(uid=uid,arithmetic=mode,sourceFace=facet['sourceFace'],savedPieceID=i,restriction=restriction))
     if proof['unresolved']:unresolved.append(dict(uid=uid,arithmetic=mode,sourceFace=facet['sourceFace'],savedPieceID=i,restriction=proof))
  rows.append(dict(uid=uid,arithmetic=mode,completeSourceWorldSHA256=row['completeWholeWorldSHA256'],savedCurrentGroundSHA256=row['completeCurrentGroundSHA256'],completeSavedFalseWholeFacetIDs=[r['sourceFace']for r in row['completeOriginalFaceComparisons']if not r['currentDrawnGroundComparison']['completeFiniteOrdinaryBoundProved']],completeNominatedRestrictions=records))
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h
 out=dict(schema='southside-selective13-entire-new-collar-saved-piece-compatibility-v1',completeOriginal13DomainLineage=core['completeRawClosedDomainUnion']['completeRawDomainRecords'],completeNewClosedOuterProjectionDomains=domains,all8SourceWorldRows=rows,baselineFalseAuthenticTrueRestrictionFailures=negative,unresolvedRestrictions=unresolved,noImprovedClippedRegionLost=not negative and not unresolved,entireNewCollarCompatibilityIsNotWholeCandidateAcceptance=True,conservativeClosedNomination=schedule,all1560PriorRestrictionsVerbatim=saved['q']['baselineFalseAuthenticTrueRestrictionFailures'],all19HistoricalObligationsVerbatim=saved['q']['all19HistoricalObligationsVerbatim'],all46ProtectedFormsVerbatim=saved['q']['all46ProtectedFormsVerbatim'],inputHashes=pins,historicalCapturedBaselineOnly=True,noSourceDecode=True,noNewWholeFiniteOrGradePredicates=True,noDB=True,noLease=True,noTerrainConstruction=True,currentAcceptance=False,physicalAccepted=False)
 OUT.mkdir();p=OUT/'diagnostic.json';p.open('x').write(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()),negativeRestrictions=len(negative),unresolvedRestrictions=len(unresolved),noImprovedClippedRegionLost=out['noImprovedClippedRegionLost'],currentAcceptance=False)))
if __name__=='__main__':main()
