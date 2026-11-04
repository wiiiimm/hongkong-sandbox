"""Complete original Evangel typed account; no omitted source or blanket rule.

Caller independently binds/replays all receipts, current actor/source/pose,
terrain, native census and actual runtime. Visual surfaces never root or bridge.
Named lower source skins retain every raw failure as an interpreted source
surface, with no geometry/threshold change or engineering load certification.
"""
from collections import deque
from copy import deepcopy
from fractions import Fraction as F
import numpy as np
from evangel_college_original_wing_extension_identity_20261011 import UID,SOURCE_SHA
from evangel_college_named_lower_source_skin_v3_20261011 import verify as lower,sha,GROUND_SHA,BASES,SLOPING,strict_record
from evangel_college_named_two_upper_strips_v2_20261011 import verify as strips
from evangel_college_named_standing_grade_skin_20261011 import IDS as STANDING
MODES={'providerOriginal','actualLiteral','explicitLeftAssociatedF32ModelMatrix','explicitBalancedF32ModelMatrix'}
def row(doc,mode):
 rows=[r for r in doc['rows']if r['arithmetic']==mode];assert len(rows)==1;return rows[0]
def compose(*,data,ground,finite,graph,grade,qualification,standing,remaining,physical,metrics,validation,foundation,neighbours,native_checks,native,domain,foreign,identity,current_manifest):
 assert data['uid']==UID and data['sourceSHA256']==SOURCE_SHA and set(data['completeWorldStreams'])==MODES and sha(ground)==GROUND_SHA
 assert identity['passed']is True and identity['reasons']==[]
 assert physical['uids']==[UID]and physical['currentManifest']==current_manifest and physical['all17CurrentActorGuardsRetained']is True and physical['modelGeometryChanges']==0
 assert physical['rawOrdinaryReasons']==['terrain-intersects-source-over-0.5m','whole-source-foundation']
 assert validation['models']==validation['loaderAccepted']==validation['checksPassed']==1 and validation['exceptions']==0 and validation['published']is False
 assert len(metrics['rows'])==1;metric=metrics['rows'][0];assert metric['uid']==UID and metric['sourceSHA256']==SOURCE_SHA and metric['sourcePreserved']is True and metric['missingTerrain']==0 and metric['missingDrawnTerrain']['count']==metric['samplerDisagreement']['count']==0 and metric['maxSamplerDelta']==0 and metric['terrainTriangles']==1848
 assert len(foundation['rows'])==1;found=foundation['rows'][0];assert found['uid']==UID and found['sourceSHA256']==SOURCE_SHA and found['strictFoundationAccepted']is False and found['foundation']['triangles']==13960 and found['foundation']['fullyBuriedTriangles']==20 and found['foundation']['fullyBuriedUpwardTriangles']==0
 nrows=neighbours['rows'];assert len(nrows)==len({r['uid']for r in nrows})==17 and sum(r['candidate']is True for r in nrows)==1 and all(r['reasons']==[]for r in nrows)and not native_checks['blocked']
 assert foreign['uid']==UID and foreign['sourceSHA256']==SOURCE_SHA and foreign['currentManifest']==current_manifest and foreign['completeRegionalActors']==17 and foreign['completeForeignBasics']==16 and foreign['foreignActorsRequiringFullCollisionProof']==[] and foreign['allFourStreamsAndComplete16BasicsStrictClosedProjectionDisjoint']is True
 assert native['uids']==domain['uids']==[UID]and native['sourceSHA256']==SOURCE_SHA and native['currentManifest']==domain['currentManifest']==current_manifest and native['exactCurrentInputFormEntrySourceAndLoaderTuple']is True
 cert=native['completeNativeActualBoundsCertificate'];assert cert['completeForeignNativeActors']==6645 and cert['allFourOwnedByThreeActualNativeWorldBoundsStrictlyDisjoint']is True and cert['noToleranceOrGeographicBufferCredit']is True
 assert domain['complete6645CurrentNativeActors']==6645 and domain['terrainDomainNominatedActors']==[]and domain['allActualNativeBoundsDisjointFromCompleteChangedTerrainDomain']is True and domain['noRecordedGeographicFootprintCredit']is True
 for doc in [finite,graph,grade,qualification,standing,remaining]:
  assert doc['sourceSHA256']==SOURCE_SHA and len(doc['rows'])==4 and {r['arithmetic']for r in doc['rows']}==MODES
 assert standing['completeActualGroundSHA256']==remaining['completeActualGroundSHA256']==qualification['completeActualGroundSHA256']==grade['completeActualCandidateGroundSHA256']==GROUND_SHA
 assert remaining['currentManifestSHA256']==standing['currentManifestSHA256']==qualification['currentManifestSHA256']==grade['completeCurrentManifestSHA256']==current_manifest['sha256']
 out=[]
 for mode in sorted(MODES):
  stream=data['completeWorldStreams'][mode];w=np.asarray(stream['completeWorldTriangles'],dtype='<f8');wh=sha(w);assert w.shape==(13960,3,3)and wh==stream['completeWorldTriangleSHA256']
  g=row(graph,mode);fr=row(finite,mode);gr=row(grade,mode);q=row(qualification,mode);st=row(standing,mode);rm=row(remaining,mode)
  assert all(r['completeWorldSHA256']==wh for r in [g,gr,q,st,rm])and fr['completeWholeWorldSHA256']==wh
  topology=g['completeOriginalTopology'];parts=topology['sharedEdgeConnectedComponents'];zeros=topology['exactNonrenderingOriginalFaces'];assert len(parts)==226 and len(zeros)==33 and len(set(zeros))==33 and set(i for p in parts for i in p)|set(zeros)==set(range(13960))and not set(i for p in parts for i in p)&set(zeros)
  records=fr['complete13960FaceComparisons'];assert len(records)==13960 and [r['sourceFace']for r in records]==list(range(13960))
  failed={r['sourceFace']for r in records if not r['groundComparisons']['currentDrawn']['completeFiniteOrdinaryBoundProved']};assert len(failed)==132
  down=set(gr['rawDownwardFacesRetainedAsUncredited']);assert down==set(SLOPING+BASES[68]+BASES[69])and gr['rawZeroFailureFacesRetainedAsUncredited']==sorted(failed&set(zeros))and len(failed&set(zeros))==3
  p=gr['strictCapPathDiagnostic'];mapping=gr['eligibleWallCapPathFaceToSourceFace'];assert p['allAffectedHavePaths']is True and p['rawExposureFailures']==[]and p['collapsedOriginalFaces']==[]and p['completeOriginalFaces']==len(mapping)==5275
  wall_paths=p['paths'];wall_ids=[mapping[x['sourceFace']]for x in wall_paths];assert len(wall_ids)==len(set(wall_ids))==107 and set(wall_ids)==failed-down-set(zeros)
  for path in wall_paths:
   assert path['hasExactOriginalStrictClearCapRoofPath']is True and path['rawFaceExposurePositive']is True and path['originalPath'][0]==path['sourceFace']and path['strictClearNonWallFaces']and all(i not in down and i not in zeros for i in [mapping[j]for j in path['originalPath']])
   for cap in path['strictClearNonWallFaces']:strict_record(records,mapping[cap],w)
  actual_grade=gr['complete5297CurrentGradeContactInventory'];assert actual_grade['allPairsExamined']is True and actual_grade['sourceFacesOmitted']==0
  genuine={c['sourceFaceA']for c in actual_grade['contacts']if c['dimension']>0 and c['sourcePrimitiveDimensionA']==c['sourcePrimitiveDimensionB']==2}
  roots={c:sorted(set(parts[c])&set(wall_ids)&genuine)for c in [13,68,69,223]};assert all(roots.values())
  lower_proof=lower(world=w,ground=ground,finite_row=fr,grade_row=gr,parts=parts);assert lower_proof==rm['namedLowerSourceSkinProposal']
  assert q['unresolvedEnvelopeComponents']==[]and q['all33ZeroFacesRetainedAndUncredited']==zeros and q['all226RealComponentsPartitionedExactly']is True
  envelope=q['complete216ConditionalEnvelopeComponents'];assert len(envelope)==216 and set(envelope)==set(range(226))-{28,29,30,221,222,62,90,98,99,100}
  # Rebuild only the already-computed complete original interface account;
  # raw buried/zero/point surfaces cannot transfer ground credit.
  adjacency={i:set()for i in envelope};expected=[]
  for pair in g['everyNominatedPairPrimitiveInventory']:
   a,b=pair['originalComponentA'],pair['originalComponentB']
   if a not in adjacency or b not in adjacency:continue
   contacts=[c for c in pair['completePrimitiveContactInventory']['contacts']if c['dimension']>0 and c['sourcePrimitiveDimensionA']==c['sourcePrimitiveDimensionB']==2 and c['sourceFaceA']not in down and c['sourceFaceB']not in down]
   if contacts:adjacency[a].add(b);adjacency[b].add(a);expected.append(dict(originalComponentA=a,originalComponentB=b,completeEligibleOriginalContacts=contacts))
  assert q['completeEligibleEnvelopeInterfaceInventory']==expected
  paths={13:[13]};queue=deque([13])
  while queue:
   i=queue.popleft()
   for j in sorted(adjacency[i]):
    if j not in paths:paths[j]=paths[i]+[j];queue.append(j)
  assert set(paths)==set(envelope)and q['completeConditionalEnvelopeSourcePaths']==[dict(originalComponent=i,originalComponentPath=paths[i])for i in sorted(paths)]
  hosts=sorted(i for c in envelope for i in parts[c]if i not in down);assert q['completeConditionalHostFaceIds']==hosts
  # Ordinary independent body90 retains the unchanged strict JS footing.
  standing_rows=q['completeFiveStandingDispositions'];assert {r['originalComponent']for r in standing_rows}=={62,90,98,99,100}
  ordinary=next(r for r in standing_rows if r['originalComponent']==90);assert ordinary['completeOriginalFaces']==parts[90]and ordinary['completeOrdinaryFootingVerbatim']['passed']is True and ordinary['allOriginalFacetsOrdinaryClear']is True
  skins=st['completeFourStandingSkinProofs'];assert len(skins)==4 and {r['originalComponent']for r in skins}==set(STANDING)
  for skin in skins:
   c=skin['originalComponent'];pr=skin['completeNamedStandingSkinProof'];original=next(r for r in standing_rows if r['originalComponent']==c)
   assert parts[c]==STANDING[c]==pr['completeOriginalFaceIds']and pr['binding']==dict(completePartSHA256=sha(w[parts[c]]),completeGroundSHA256=GROUND_SHA)
   assert pr['everyLateralFacetGenuinelyCrossesGrade']is True and pr['wholeOriginalUpperPerimeterStrictlyClear']is True and pr['allOriginalCapsAndBaseSurfacesRetained']is True and pr['supportTransferToOtherSourceBodies']is False
   assert pr['closedSolidCertified']is False and pr['loadBearingClaim']is False and pr['sourceGeometryChanges']==pr['terrainGeometryChanges']==0
   # Named standalone helper indexes its complete part locally; the earlier
   # whole-source census reports literal original IDs. Bind the exact mapping,
   # preserving every contact coordinate/dimension/ground ID and inventory key.
   mapped=deepcopy(pr['genuineCompleteFiniteGradeContacts'])
   for contact in mapped['contacts']:contact['sourceFaceA']=parts[c][contact['sourceFaceA']]
   assert mapped==original['completeOriginalGroundContactInventory']and skin['rawOrdinaryWholeFootingVerbatim']==original['completeOrdinaryFootingVerbatim']and original['completeOrdinaryFootingVerbatim']['passed']is False
  visual=q['completeFiveVisualDispositions'];assert {r['originalComponent']for r in visual}=={28,29,30,221,222}
  for v in visual:
   assert v['completeOriginalFaces']==parts[v['originalComponent']]and v['allOriginalFacetsOrdinaryClear']is True and v['structuralRootCredit']is False and v['structuralBridgeCredit']is False and set(v['completeHostCandidateFaceIds'])<=set(hosts)
   if v['originalComponent']in {28,29,30}:assert v['completeBoundaryAssociated']is True and len(v['completeBoundaryEdgeFiniteHostBandProofs'])==4 and all(e['fullEdgeAssociated']is True for e in v['completeBoundaryEdgeFiniteHostBandProofs'])
  strip_proof=strips(world=w,qualification_row=q,parts=parts,qualified_host_face_ids=hosts);assert strip_proof==rm['namedTwoUpperStripProposal']
  accounted=set(envelope)|{62,90,98,99,100}|{28,29,30,221,222};assert accounted==set(range(226))
  out.append(dict(arithmetic=mode,completeWorldSHA256=wh,completeOriginalFaces=13960,qualifiedEnvelopeComponents=envelope,independentGroundSkinComponents=[62,98,99,100],ordinaryIndependentGroundComponent=90,nonstructuralWholePerimeterVisualComponents=[28,29,30],nonstructuralLowerAndSideBackedFreeUpperStrips=[221,222],completeActualEnvelopeGradeRoots=roots,namedLowerOriginalSkinProof=lower_proof,namedTwoStripProof=strip_proof,all33OriginalZerosRetainedWithoutRootOrBridge=zeros,all132RawFiniteFailuresRetained=sorted(failed),all226ComponentsAccounted=True))
 return dict(uid=UID,sourceSHA256=SOURCE_SHA,currentManifest=current_manifest,completeOriginalFaces=13960,completeRealComponents=226,completeFourWorldComposition=out,rawOrdinaryReasonsRetained=physical['rawOrdinaryReasons'],rawStrictFoundationRecordRetained=found,all17CurrentActorsAnd6645NativeGuardsRetained=True,visualPartsProvideNoRootOrBridge=True,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,sourceGeometryChanges=0,changedTerrainProposal=True,currentTypedPhysicalAccepted=True,acceptanceReadyForStaging=True,installationApproved=False,reasons=[],scriptChecksPassed=True)
