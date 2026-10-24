"""UNEXECUTED complete saved authentic-positive negative-region separation.
New exact distance only; no full finite replay, DB, lease, terrain or acceptance.
"""
import sys,json,gzip,hashlib
from pathlib import Path
from fractions import Fraction as F
from southside_saved_negative_region_exact_core_distance_draft_v1_20261013 import closed_negative_region,prepare_complete_core,distance_to_complete_core,authentic_positive_faces
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent;BASE=ROOT/'docs/astra-city/government-import';P=BASE/'government-xl-southside-private-authentic-terrain-draft-v2-20261012/selective13-parent-restoration-draft-v1';OUT=P/'all-saved-negative-region-exact-core-distance-v1'
COLLAR=P/'full-new-collar-saved-piece-compatibility-v1/diagnostic.json';CORE=P/'closed-core-preparation-v1/closed-core-preparation.json';AUDIT=P/'readonly-negative-collar-source-provenance-audit-v1.json'
FINITE=BASE/'government-xl-southside-315025-300867-complete-four-stream-current-finite-v1-20261012/diagnostic.json.gz';AUTH=BASE/'government-xl-southside-315025-300867-unfiltered-original-sheets-comparison-v2-20261012/diagnostic.json.gz'
read=lambda p:json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
CODE=[Path(__file__),HERE/'southside_saved_negative_region_exact_core_distance_draft_v1_20261013.py',HERE/'test_southside_saved_negative_region_exact_core_distance_draft_v1_20261013.py']
def preflight():
 assert sha(COLLAR)=='e2cf4c07b006fa0c5ddfad8b26ec9434ca3d67e1d878a1eb3ee20fdbc97c0b5e'and sha(CORE)=='34643eec3a1db460d6b0ae0f7c404079fca7e0747d47c511aa55f12c9a9a62ec'and sha(AUDIT)=='472de1bbe557da66c698bf419312cbd85b3e701f96b2fab89627fb10b9982ad5'
 collar,core,audit=read(COLLAR),read(CORE),read(AUDIT);assert len(collar['baselineFalseAuthenticTrueRestrictionFailures'])==3484 and collar['unresolvedRestrictions']==[]and audit['allInputPinsVerified']==43
 provenance_path=P/'literal-generator-and-authentic-classification-provenance-v1.json';assert sha(provenance_path)=='95b0e0219abeb23eb69aa8bb8d1638d1ad59a537ec5baa5c6c2208ccb2a8ee24';provenance=read(provenance_path);provenance_refs=[provenance_path]
 for record in provenance['originalProducerReferenceMatches']:
  producer=ROOT/record['actualProducerPath'];receipt_path=ROOT/record['completedReceiptPath'];assert sha(producer)==record['actualProducerSHA256']and sha(receipt_path)==record['completedReceiptSHA256'];receipt=read(receipt_path);assert receipt['jobId']==record['originalCompletedJob']and record['exactOriginalProducerReference']in receipt['evidenceRefs'];provenance_refs.extend([producer,receipt_path])
 kernel=provenance['originalSavedPieceKernel'];assert sha(ROOT/kernel['path'])==kernel['sha256'];provenance_refs.append(ROOT/kernel['path'])
 assert collar['completeOriginal13DomainLineage']==core['completeRawClosedDomainUnion']['completeRawDomainRecords']and core['completeClosedParentCoverage']['allClosedPrimitivesCovered']
 pins=dict(collar['inputHashes'])
 for p,h in pins.items():assert sha(ROOT/p)==h
 assert sha(FINITE)==pins[str(FINITE.relative_to(ROOT))]and sha(AUTH)==pins[str(AUTH.relative_to(ROOT))]
 finite,auth=read(FINITE),read(AUTH);assert len(finite['rows'])==len(auth['rows'])==8
 for row in finite['rows']:
  ar=next(q for q in auth['rows']if q['uid']==row['uid']and q['arithmetic']==row['arithmetic']);assert ar['completeWorldSHA256']==row['completeWholeWorldSHA256'];assert [r['sourceFace']for r in row['completeOriginalFaceComparisons']]==list(range(row['completeOriginalFaceCount']));authentic_positive_faces(ar,row)
 assert sum(r['completeOriginalFaceCount']for r in finite['rows'])==51560
 vpath=P/'immutable-exact-distance-fixtures-v1/validation.json';v=read(vpath);log=vpath.parent/'tests.log';assert v['testCount']==14 and v['actualExitCode']==0 and v['allPassed']and sha(log)==v['testLogSHA256'];assert v['codePins']=={str(p.relative_to(ROOT)):sha(p)for p in CODE}
 for p in [*CODE,*provenance_refs,COLLAR,CORE,AUDIT,vpath,log,P/'EXACT-NEGATIVE-REGION-CORE-DISTANCE-METHOD.md']:pins[str(p.relative_to(ROOT))]=sha(p)
 return collar,core,finite,auth,pins

def main():
 collar,core,finite,auth,pins=preflight()
 if '--preflight-only'in sys.argv:print(json.dumps(dict(savedSlots=51560,savedCollarNegatives=3484,sourceWorldRows=8,original13CoreDomains=3653,fixtureCount=14,noDB=True,noLease=True,noTerrainConstruction=True,currentAcceptance=False)));return
 assert '--calculate-exact-separation-only'in sys.argv and not OUT.exists()
 prepared=prepare_complete_core(core['completeRawClosedDomainUnion']['completeRawDomainRecords']);rows=[];unresolved=[];global_min=None;global_witnesses=[];all_piece_records=0
 for row in finite['rows']:
  uid,mode=row['uid'],row['arithmetic'];ar=next(q for q in auth['rows']if q['uid']==uid and q['arithmetic']==mode);auth_positive=authentic_positive_faces(ar,row);records=[];paired_piece_count=0
  for facet in row['completeOriginalFaceComparisons']:
   c=facet['currentDrawnGroundComparison'];face_id=facet['sourceFace']
   if c['completeFiniteOrdinaryBoundProved']or face_id not in auth_positive:continue # exact prior positive or authentic-negative obligation retained independently.
   if c['paired']is None:unresolved.append(dict(uid=uid,arithmetic=mode,sourceFace=face_id,savedFullFacetVerbatim=facet));continue
   for piece_id,piece in enumerate(c['paired']['allExactFiniteSourceGroundPieces']):
    paired_piece_count+=1;all_piece_records+=1
    if 'allExactSourcePrismIntersectionVertices'not in piece:
     assert piece.get('closedProjectionDisjoint')or piece.get('collapsedProjectionConservative')
     if piece.get('collapsedProjectionConservative'):unresolved.append(dict(uid=uid,arithmetic=mode,sourceFace=face_id,savedPieceID=piece_id,savedPieceVerbatim=piece))
     continue
    if F(piece['exactMinimumGapM'])>=F(-1,2):continue
    vertices=piece['allExactSourcePrismIntersectionVertices'];region=closed_negative_region([v['exactOriginalSourcePoint']for v in vertices],[v['exactGapM']for v in vertices]);assert region['hasStrictNegativePoint']and region['completeClosedNegativeSourcePoints']
    proof=distance_to_complete_core([(p[0],p[2])for p in region['completeClosedNegativeSourcePoints']],prepared);record=dict(sourceFace=face_id,completeOriginalFacetSHA256=facet['completeOriginalFacetSHA256'],savedPieceID=piece_id,originalGroundFace=piece['originalGroundFace'],completeClosedStrictNegativeRegion=region,completeExactCoreSeparation=proof);records.append(record);distance=proof['exactMinimumDistanceM']
    if global_min is None or distance<global_min:global_min=distance;global_witnesses=[]
    if distance==global_min:global_witnesses.append(dict(uid=uid,arithmetic=mode,sourceFace=face_id,savedPieceID=piece_id,completeExactNearestCoreBoundaryWitnesses=proof['completeNearestCoreTies']))
  rows.append(dict(uid=uid,arithmetic=mode,completeWorldSHA256=row['completeWholeWorldSHA256'],completeCurrentGroundSHA256=row['completeCurrentGroundSHA256'],savedAuthenticPositiveFalseFacetIDs=[f['sourceFace']for f in row['completeOriginalFaceComparisons']if not f['currentDrawnGroundComparison']['completeFiniteOrdinaryBoundProved']and f['sourceFace']in auth_positive],completeSavedPairedPiecesExamined=paired_piece_count,completeNegativeRegionSeparationRecords=records))
 for p,h in pins.items():assert sha(ROOT/p)==h
 out=dict(schema='southside-all-saved-authentic-positive-negative-region-exact-core-distance-v1',all8WorldRows=rows,completePreparedOriginal13Core=prepared,all3653OriginalCoreDomainRecords=core['completeRawClosedDomainUnion']['completeRawDomainRecords'],all3484PriorCollarNegativesVerbatim=collar['baselineFalseAuthenticTrueRestrictionFailures'],completeUnresolvedRecords=unresolved,exactGlobalDistanceInfimumM=global_min,completeGlobalMinimumWitnesses=global_witnesses,positiveUniformGeometricSeparationExists=global_min is not None and global_min>0 and not unresolved,zeroDistanceIsNotInstallationImpossibility=True,narrowerTerrainNotConstructedOrQualified=True,completeSavedPairedPiecesExamined=all_piece_records,all19HistoricalObligationsVerbatim=collar['all19HistoricalObligationsVerbatim'],all46ProtectedFormsVerbatim=collar['all46ProtectedFormsVerbatim'],inputHashes=pins,historicalCapturedSourceOnly=True,noDB=True,noLease=True,noSourceDecode=True,noWholeFiniteReplay=True,noTerrainConstruction=True,currentAcceptance=False)
 OUT.mkdir();dest=OUT/'diagnostic.json.gz';payload=json.dumps(out,sort_keys=True,separators=(',',':'),default=lambda v:str(v)if isinstance(v,F)else (_ for _ in ()).throw(TypeError(type(v).__name__))).encode();dest.open('xb').write(gzip.compress(payload,mtime=0));print(json.dumps(dict(path=str(dest.relative_to(ROOT)),sha256=sha(dest),exactGlobalDistanceInfimumM=str(global_min),savedNegativeRegions=sum(len(r['completeNegativeRegionSeparationRecords'])for r in rows),unresolved=len(unresolved),currentAcceptance=False)))
if __name__=='__main__':main()
