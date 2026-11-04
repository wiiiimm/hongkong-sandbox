"""Named unchanged Heya source account; no engineered support certification.

The complete attached source envelope has a genuine exposed original path to
the actual installed podium's grade. Named58 source-owned terminal facade
surfaces never supply a root or bridge. Every independent ordinary/foreign/
native guard remains mandatory. Caller binds complete receipt provenance.
"""
from fractions import Fraction as F
import hashlib
import numpy as np
from heya_aqua_58_original_terminal_visual_placement_20261011 import NAMED,SOURCE,WORLD,UID as T,PODIUM

P=PODIUM
MODES=['providerOriginal','actualLiteral','explicitLeftAssociatedF32ModelMatrix','explicitBalancedF32ModelMatrix']
CURRENT='947f0a3b3a1d7167a9f98074af35d4030ff0245e121ee682eed4f9ab9baedfa6'
def sha(a):return hashlib.sha256(np.asarray(a,dtype='<f8').tobytes()).hexdigest()
def positive(c):return c['dimension']>0 and c['sourcePrimitiveDimensionA']==c['sourcePrimitiveDimensionB']==2

def verify_roles(*,actual,source,interfaces,finite,visual,account):
 assert source['sourceGeometryChanges']==source['terrainGeometryChanges']==source['sourceFacesOmitted']==0
 assert visual['sourceSHA256']==SOURCE and visual['completeOriginalWorldSHA256']==WORLD
 assert visual['completeNamedTerminalComponents']==NAMED and len(visual['completeNamedTerminalFaces'])==1312
 assert visual['structuralRootCredit']is visual['structuralBridgeCredit']is visual['loadBearingClaim']is False
 assert account['sourceGeometryChanges']==account['terrainGeometryChanges']==0
 assert account['engineeringSupportCertified']is account['installedPodiumReapproved']is False
 assert account['rawTwoResidualRimFailuresRetained']==source['rawTwoResidualRimFailuresRetained']
 assert account['completeNamed58ProviderPlacementProof']==visual
 assert source['rawTwoResidualRimFailuresRetained']['unresolved']==2
 assert all(r['completeSourceComponentIds']==[4]and not r['pointSupportCredit']for r in source['residualSourceIncidences'])
 assert set(actual)=={T,P}and len(account['rows'])==4
 assert {r['arithmetic']for r in account['rows']}==set(MODES)
 assert len(interfaces['rows'])==4 and len(finite['rows'])==8
 attached=sorted(set(range(574))-set(NAMED));records=[]
 for mode in MODES:
  row=next(r for r in account['rows']if r['arithmetic']==mode)
  item=next(r for r in interfaces['rows']if r['arithmetic']==mode)
  for uid,count in [(T,17910),(P,3844)]:
   world=actual[uid]['completeWorldStreams'][mode]
   assert sha(world['completeWorldTriangles'])==world['completeWorldTriangleSHA256']==item['completeWorldHashes'][uid]==row['completeWorldHashes'][uid]
   fr=next(r for r in finite['rows']if r['uid']==uid and r['arithmetic']==mode)
   assert fr['completeWholeWorldSHA256']==world['completeWorldTriangleSHA256']and fr['completeOriginalFaceCount']==count
   assert fr['completeCurrentGroundSHA256']==actual[uid]['completeDrawnGroundSHA256']==sha(actual[uid]['completeDrawnGround'])
   assert fr['failedFacesRetained']==[]and [r['sourceFace']for r in fr['completeOriginalFaceComparisons']]==list(range(count))
   assert all(r['currentDrawnGroundComparison']['completeFiniteOrdinaryBoundProved']for r in fr['completeOriginalFaceComparisons'])
  parts=item['completeActualTopologies'][T]['sharedEdgeConnectedComponents']
  assert len(parts)==574 and parts==source['actors'][T]['completeOriginalTopology']['sharedEdgeConnectedComponents']
  assert item['completeActualTopologies'][T]['exactNonrenderingOriginalFaces']==[]
  assert row['completeAttachedTowerComponents']==attached and row['completeNamed58Components']==NAMED
  faces=sorted(i for k in attached for i in parts[k]);visual_faces=sorted(i for k in NAMED for i in parts[k])
  assert row['completeAttachedTowerFaceIds']==faces and row['completeNamed58FaceIds']==visual_faces==visual['completeNamedTerminalFaces']
  assert len(faces)==16598 and sorted(faces+visual_faces)==list(range(17910))
  assert row['allCompleteSourceFacesAccounted']==17910 and row['terminalVisualsNeverProvideRootOrBridge']
  assert not row['engineeringSupportCertified']
  graph={i:set()for i in attached};seen_pairs=set()
  for pair in row['completeWithinTowerBoundsNominatedPairs']:
   a,b=pair['componentA'],pair['componentB'];assert 0<=a<b<574 and(a,b)not in seen_pairs;seen_pairs.add((a,b))
   inventory=pair['completePrimitiveContactInventory'];assert inventory['allPairsExamined']and inventory['sourceFacesOmitted']==0
   contacts=[c for c in inventory['contacts']if positive(c)]
   assert pair['positiveRealFacetInterfaces']==len(contacts)
   if contacts:
    assert a in graph and b in graph
    assert all(c['sourceFaceA']in parts[a]and c['sourceFaceB']in parts[b]for c in contacts)
    graph[a].add(b);graph[b].add(a)
  parents={int(k):v for k,v in row['componentParentFromT4'].items()};assert set(parents)==set(attached)and parents[4]is None
  for node in attached:
   visited=set();current=node
   while current!=4:
    assert current not in visited;visited.add(current)
    parent=parents[current];assert parent in graph[current];current=parent
  root=row['originalExposedGradeToT4Path']
  assert root['originalPodiumComponent']==0 and root['originalTowerComponent']==4
  assert root['completePodiumWorldSHA256']==item['completeWorldHashes'][P]
  assert root['completeDrawnGroundSHA256']==actual[P]['completeDrawnGroundSHA256']
  assert root['engineeringSupportCertified']is root['loadBearingClaim']is root['pointRootCredit']is root['installedPodiumReapproved']is False
  grade=root['genuineGradeToExposedAscent']['genuineGradeContact'];contact=root['wholePositiveTowerPodiumContact']
  assert grade in item['allGroundPrimitiveRecordsWithRealComponentBindings']and positive(grade)and grade['podiumComponent']==0
  assert contact in item['allCrossPrimitiveRecordsWithRealComponentBindings']and positive(contact)and contact['towerComponent']==4 and contact['podiumComponent']==0
  path=root['podiumOriginalFacePath'];assert path and path[0]==grade['sourceFaceA']and path[-1]==contact['sourceFaceB']
  assert len(root['completeStrictSharedEdges'])==len(path)-1
  for (a,b),edge in zip(zip(path,path[1:]),root['completeStrictSharedEdges']):
   assert edge['sourceFaces']==[a,b]and edge['completeExposureProof']['strictlyExposedWholePositiveInterface']
   points=edge['exactEndpoints'];assert len(points)==2 and points[0]!=points[1]
  assert root['completeTerminalInterfaceExposure']['strictlyExposedWholePositiveInterface']
  assert root['completeTerminalInterfaceExposure']['completeGroundSHA256']==actual[P]['completeDrawnGroundSHA256']
  records.append(dict(arithmetic=mode,completeAttachedSourceEnvelopeComponents=attached,
   completeNonstructuralTerminalVisualComponents=NAMED,completeSourceFaces=17910,
   sourceEnvelopeRoot='genuine original P0 grade/exposed-source path/positive original T4 interface',
   structuralOrEngineeringCertification=False,visualsProvideNoRootOrBridge=True))
 return dict(rows=records,completeOriginalComponents=574,completeOriginalFaces=17910,
  completeAttachedSourceEnvelopeComponents=516,completeNonstructuralTerminalVisualComponents=58,
  preservedRawTwoRimFailures=source['rawTwoResidualRimFailuresRetained'],engineeringSupportCertified=False,
  sourceGeometryChanges=0,terrainGeometryChanges=0)

def compose(*,actual,source,interfaces,finite,visual,account,identity,physical,foreign,native,native_uids,context,current_forms,provider_sources):
 role=verify_roles(actual=actual,source=source,interfaces=interfaces,finite=finite,visual=visual,account=account)
 assert identity['uid']==T and identity['sourceSHA256']==SOURCE and identity['passed']and identity['reasons']==[]
 assert physical['uid']==T and physical['completeOwnedFaces']==17910 and physical['strictFoundationAccepted']
 assert physical['ordinaryNumericReasons']==['ground-contact-unresolved']
 assert physical['loaderAccepted']==physical['runtimeChecksPassed']==1 and physical['runtimeExceptions']==0
 assert physical['neighbourRegressionReasons']==[]and physical['rawNativeNeighbourChecks']['blocked']==[]
 assert len(physical['rawRuntimeConcerns'])==1 and physical['rawRuntimeConcerns'][0]['concerns']==['sampled-ground-gap-below-model-bottom']
 assert foreign['completeRegionalActors']==14 and foreign['completeForeignBasics']==12 and len(foreign['rows'])==12
 assert len({r['uid']for r in foreign['rows']})==12 and {'landsd/184287:0','landsd/184519:0'}<=set(r['uid']for r in foreign['rows'])
 assert foreign['foreignActorsRequiringFullCollisionProof']==[]and foreign['allFourStreamsAndComplete12BasicsStrictClosedProjectionDisjoint']
 for row in foreign['rows']:
  assert len(row['fourStreamTrials'])==4 and {r['arithmetic']for r in row['fourStreamTrials']}==set(MODES)
  assert not row['requiresIndependentCompleteFiniteCollisionContext']
  assert all(r['strictCompleteClosedProjectionsDisjoint']and not r['allClosedFiniteProjectionIntersections']for r in row['fourStreamTrials'])
 assert len(native_uids)==6648 and len(set(native_uids))==6648 and P in native_uids and T not in native_uids
 assert native['completeCurrentNativeActors']==6648 and native['completeForeignNativeActors']==6647
 assert native['allOtherInstalledNativeWholeActualPositionBoundsStrictlyDisjoint']and native['actualNativeActorsRequiringFullFiniteCollision']==[]
 assert len(native['allSeparatedNativeActors'])==6647 and {r['uid']for r in native['allSeparatedNativeActors']}==set(native_uids)-{P}
 for row in native['allSeparatedNativeActors']:
  assert row['wholeUnusedPositionVerticesIncluded']and len(row['completePairProofs'])==12
  assert all(F(p['exactPositiveGapM'])>0 for p in row['completePairProofs'])
 assert native['coupledInstalledPodium']['uid']==P and native['coupledInstalledPodium']['notIgnoredOrReapproved']
 assert len(native['completeCoupledOriginalPrimitiveContext'])==4
 from heya_aqua_original_lower_assembly_join_20261011 import verify as verify_join
 join=verify_join(actual=actual,interfaces=interfaces,native=native,context=context,current_forms=current_forms,provider_sources=provider_sources,identity=identity)
 for proof in [physical,foreign,native]:assert proof['currentManifest']['sha256']==CURRENT
 return dict(uid=T,sourceSHA256=SOURCE,completeTypedOriginalRoleAccount=role,completeSourceOwnedLowerAssemblyJoin=join,
  preservedRawOrdinaryNumericReasons=physical['ordinaryNumericReasons'],
  preservedRawRuntimeConcerns=physical['rawRuntimeConcerns'],reasons=[],scriptChecksPassed=True,
  sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,sourceGeometryChanges=0,terrainGeometryChanges=0,
  engineeringSupportCertified=False,installedPodiumReapproved=False,
  stagingReady=True,installationApproved=False,newlyInstalled=0)
