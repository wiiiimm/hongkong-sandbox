"""Whole unchanged King Cheung original role composition; no blanket waiver.

Caller must independently bind/replay source/current/Neon receipts and supplied
mathematical records. Visual191 never roots or bridges another component.
"""
from collections import deque
from king_cheung_named14_intrinsic_visual_placement_20261011 import verify as verify_named14,NAMED,IMAGES
from fractions import Fraction as F
from king_cheung_named_embedded_foundation_skin_v2_20261011 import UID,SOURCE,IDS,sha,canonical,GROUND_SHA
MODES={'providerOriginal','actualLiteral','explicitLeftAssociatedF32ModelMatrix','explicitBalancedF32ModelMatrix'}
def row_for(doc,mode):
 rows=[r for r in doc['rows']if r['arithmetic']==mode];assert len(rows)==1;return rows[0]
def compose(*,data,finite,graph,foundation,canopy,mounts,physical,native,foreign,identity,current_manifest,placement):
 assert data['uid']==UID and data['sourceSHA256']==SOURCE and set(data['completeWorldStreams'])==MODES
 assert data['completeDrawnGroundSHA256']==GROUND_SHA
 assert physical['uid']==UID and physical['completeOwnedFaces']==18742 and physical['currentManifest']==current_manifest
 assert physical['ordinaryNumericReasons']==['terrain-intersects-source-over-0.5m']
 assert physical['loaderAccepted']==physical['runtimeChecksPassed']==1 and physical['runtimeExceptions']==0 and physical['strictFoundationAccepted'] is True
 assert physical['neighbourRegressionReasons']==[] and physical['completeCurrentNeighbourForms']==5
 assert physical['rawNativeNeighbourChecks']['blocked']==[]
 assert identity['passed'] is True and identity['reasons']==[]
 assert native['uid']==foreign['uid']==UID and native['sourceSHA256']==foreign['sourceSHA256']==SOURCE
 assert native['currentManifest']==foreign['currentManifest']==current_manifest
 cert=native['completeNativeActualBoundsCertificate'];assert cert['completeForeignNativeActors']==6642 and cert['allFourOwnedByThreeActualNativeWorldBoundsStrictlyDisjoint'] is True and cert['noToleranceOrGeographicBufferCredit'] is True
 assert foreign['completeRegionalActors']==5 and foreign['completeForeignBasics']==4 and foreign['foreignActorsRequiringFullCollisionProof']==[] and foreign['allFourStreamsAndCompleteFourBasicsStrictClosedProjectionDisjoint'] is True
 for document in [finite,graph,foundation,canopy,mounts]:
  assert document['sourceSHA256']==SOURCE and {r['arithmetic']for r in document['rows']}==MODES and len(document['rows'])==4
 result=[]
 for mode in sorted(MODES):
  stream=data['completeWorldStreams'][mode];g=row_for(graph,mode);fr=row_for(finite,mode);f=row_for(foundation,mode)['proof'];c=row_for(canopy,mode);v=row_for(mounts,mode)
  assert all(r['completeWorldSHA256']==stream['completeWorldTriangleSHA256']for r in [g,v]) and fr['completeWholeWorldSHA256']==stream['completeWorldTriangleSHA256'] and c['completeWholeSourceWorldSHA256']==stream['completeWorldTriangleSHA256']
  assert f['binding']['completeWorldSHA256']==stream['completeWorldTriangleSHA256'] and f['binding']['completeGroundSHA256']==GROUND_SHA
  parts=g['completeOriginalTopology']['sharedEdgeConnectedComponents'];assert len(parts)==908 and g['completeOriginalTopology']['exactNonrenderingOriginalFaces']==[1149]
  records=fr['complete18742FaceComparisons'];assert len(records)==18742 and [r['sourceFace']for r in records]==list(range(18742))
  failed={r['sourceFace']for r in records if not r['groundComparisons']['currentDrawn']['completeFiniteOrdinaryBoundProved']}
  pathids=[p['originalSourceFace']for p in c['complete39And44ExposedOriginalCapPaths']];assert len(pathids)==len(set(pathids))==60
  canopy_failed=set(pathids)|set(range(2803,2811));assert failed==set(range(798,805))|canopy_failed and len(failed)==75
  assert f['completeFoundationOriginalFaces']==parts[34]==IDS and f['completeStrictlyClearHostOriginalFaces']==parts[23]
  assert f['completeStrictClearCapPaths']['allAffectedHavePaths'] is True and f['sourceBackedFoundationLeaf799']['soleSharedEdgeNeighbour']==798 and f['sourceBackedFoundationLeaf799']['exposedBridgeCredit'] is False
  assert c['namedIsolatedOpenPost43Proof']['everyLateralFaceCrossesActualGrade'] and c['namedIsolatedOpenPost43Proof']['wholeUpperPerimeterStrictlyExposed'] and c['namedIsolatedOpenPost43Proof']['canopySupportCredit'] is False
  adjacency={i:set()for i in range(908)}
  for p in g['everyNominatedPairPrimitiveInventory']:
   if p['positiveSourceInterfacePresent']:a,b=p['originalComponentA'],p['originalComponentB'];adjacency[a].add(b);adjacency[b].add(a)
  paths={34:[34]};queue=deque([34])
  while queue:
   i=queue.popleft()
   for j in sorted(adjacency[i]):
    if j not in paths:paths[j]=paths[i]+[j];queue.append(j)
  assert len(paths)==714 and 23 in paths and not set(paths)&{39,43,44}
  un=g['componentsWithoutCandidateSourcePath'];assert len(un)==191 and not set(paths)&set(un)
  visuals=v['completeDetachedComponentDispositions'];assert len(visuals)==191 and [r['originalComponent']for r in visuals]==un
  assert v['all191CompleteBoundariesAssociated'] is False and v['unresolvedCompleteBoundaryComponents']==NAMED
  named=verify_named14(context=placement,mode=mode,world=stream['completeWorldTriangles'],mounts=v,image_refs=IMAGES)
  hosts=sorted(i for k in paths for i in parts[k]);assert v['conditionalAttachedHostOriginalFaceIds']==hosts
  for visual in visuals:
   assert visual['completeOriginalFaces']==parts[visual['originalComponent']] and visual['allOriginalLoopsMandatory'] is True and visual['completeBoundaryAssociated'] is (visual['originalComponent'] not in NAMED)
   edges=visual['completeAllAuthoredBoundaryEdges'];loops=visual['completeEveryOriginalClosedBoundaryLoop'];assert len(edges)==sum(map(len,loops))==len(visual['completeBoundaryEdgeFiniteHostBandProofs'])
   if visual['originalComponent'] not in NAMED:assert all(e['fullEdgeAssociated'] is True and not e['emptyHostScopeExplicitlyUnqualified']for e in visual['completeBoundaryEdgeFiniteHostBandProofs'])
   assert visual['structuralRootCredit'] is False and visual['structuralBridgeCredit'] is False
  accounted=set(paths)|set(un)|{39,43,44};assert accounted==set(range(908))
  # All nonfoundation host facets and all detached visuals keep strictly
  # positive complete finite clearance, independent of their mount role.
  strict_ids=[i for k in (set(paths)-{34})|set(un)for i in parts[k]]
  for i in strict_ids:
   p=records[i]['groundComparisons']['currentDrawn'];proof=p['coarse']if p['coarse']['existingOrdinaryClearanceBoundProved']else p['paired']
   assert p['completeFiniteOrdinaryBoundProved'] is True and F(proof['exactCertifiedLowerClearanceM'])>0
  result.append(dict(arithmetic=mode,completeWholeSourceWorldSHA256=stream['completeWorldTriangleSHA256'],completeSourceFacets=18742,completeRealComponents=908,
   qualifiedAttachedEnvelopeComponents=sorted(paths),independentlyQualifiedAncillaryComponents=[39,43,44],nonstructuralPerimeterQualifiedVisualComponents=sorted(set(un)-set(NAMED)),nonstructuralNamedPlacementVisualComponents=NAMED,completeNamedVisualPlacementProof=named,
   originalZeroAreaFacesRetainedWithoutSupportCredit=[1149],raw75FiniteFailuresRetained=sorted(failed),allOriginalComponentsAccounted=True))
 return dict(uid=UID,sourceSHA256=SOURCE,currentManifest=current_manifest,completeOriginalFaces=18742,completeOriginalRealComponents=908,
  completeFourWorldComposition=result,rawOrdinaryNumericReasonsRetained=physical['ordinaryNumericReasons'],reasons=[],scriptChecksPassed=True,
  currentTypedPhysicalAccepted=True,acceptanceReadyForStaging=True,installationApproved=False,sourceGeometryChanges=0,terrainGeometryChanges=0,
  sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,visualPartsCanProvideStructuralRootsOrBridges=False,
  wholeOriginalFoundationSkinHasNoInventedCap=True,allCurrentForeignPhysicalActorsPreserved=True,nativeReapproval=False)
