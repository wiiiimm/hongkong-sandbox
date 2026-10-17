"""Draft whole Twin pair:827 nonvisual paths plus293 terminal visual parts.

Only actual mainP1091 genuine grade intervals seed the nonvisual forest. All
827 parent chains stay inside827 in every arithmetic mode. Source/render zero
facets remain represented and cannot supply contacts/hosts. Completed exact
math is reused only under its full canonical/world/ground binding; the current
file adapter must independently pin actual sources, completed jobs and inputs.
This composition alone grants no identity/foreign/runtime/browser acceptance.
"""
from fractions import Fraction as F
import numpy as np
from twin155_named_complete_boundary_visual_assembly_proposal_v1_20261011 import MODES,SOURCE_SHA,canonical,world_sha
from twin138_named_original_source_placement_proposal_v1_20261011 import pins
from exact_original_shared_edge_component_census_v2_20261011 import census
UIDS=['landsd/222465:0','landsd/223206:0'];SEED=1091
def binding(worlds,graph,finite,paths,boundary155,placement138):
 return dict(sourceSHA256ByUID={r['uid']:r['asset']['sha256']for r in graph['completeSourceInputs']},completeWorldSHA256={m:world_sha(worlds[m])for m in MODES},completeGraphSHA256=canonical(graph),completeFiniteSHA256=canonical(finite),completePathSHA256=canonical(paths),completeBoundary155SHA256=canonical(boundary155),completePlacement138SHA256=canonical(placement138))
def verify(worlds,graph,finite,paths,boundary155,placement138,*,expected_binding):
 assert set(worlds)==set(MODES);world={m:np.asarray(worlds[m],np.float64)for m in MODES};p=pins()
 assert all(w.shape==(13519,3,3)and np.isfinite(w).all()and world_sha(w)==p['completeFourWorldSHA256'][m]for m,w in world.items())
 bound=binding(world,graph,finite,paths,boundary155,placement138);assert bound==expected_binding and bound['sourceSHA256ByUID']==SOURCE_SHA
 bodies=graph['bodies'];assert len(bodies)==1120
 zeros=graph['exactNonrenderingGlobalFacesRetainedUncredited'];assert len(zeros)==8 and zeros==sorted(set(zeros))
 ids=[b['globalOriginalFaces']for b in bodies];partition=[f for a in ids for f in a]
 assert len(partition)==len(set(partition))and sorted(partition+zeros)==list(range(13519))
 for b,faces in zip(bodies,ids):
  assert faces==sorted(set(faces))and b['actorUID']==('landsd/222465:0'if max(faces)<13063 else'landsd/223206:0')
 assert bodies[SEED]['actorUID']==UIDS[1]and len(ids[SEED])==363
 common=set.intersection(*[set(r['qualifiedDiagnosticBodyIDs'])for r in paths['rows']]);assert len(common)==827 and SEED in common and 18 in common
 b155=boundary155['rows'];p138=placement138['rows'];assert [len(b155),len(p138)]==[155,138]
 visual=b155+p138;visualids=[r['originalBody']for r in visual]
 assert len(set(visualids))==293 and not set(visualids)&common and set(visualids)|common==set(range(1120))
 for r in visual:
  i=r['originalBody'];assert r['completeOriginalFaces']==ids[i]and r['uid']==bodies[i]['actorUID']
  assert r['conditionalSourceVisualRoleProposal']is True and r['structuralRootCredit']is False and r['structuralBridgeCredit']is False and r['visualPartsNeverQualifyHosts']is True and r['currentAcceptance']is False and r['nativeReacceptance']is False
  proof=r.get('allFourStreamProofs',r.get('allFourStreamCompleteProofs'));assert len(proof)==4 and {v['mode']for v in proof}==set(MODES)
 for r in p138:assert r['finiteMountingCertified']is False and r['wholeInteriorProximityCertified']is False and r['sourceContextIsPlacementEvidenceNotMount']is True and len(r['allPriorMountingAndFreeEdgeNegativesVerbatim'])==4
 for r in b155:assert r['wholeInteriorProximityNotCertified']is True and r['originalInteriorNegativesPreserved']is True
 rows=[]
 for mode in MODES:
  w=world[mode];path=next(r for r in paths['rows']if r['mode']==mode)
  assert path['completeWorldSHA256']==world_sha(w)and path['completeOriginalBodies']==1120 and path['completeOriginalFaces']==13519
  assert path['noVisualRootOrBridgeCredit']is True and path['all8SourceZeroFacetsRetainedUncredited']==zeros
  finite_rows=[next(r for r in finite['rows']if r['mode']==mode and r['uid']==uid)for uid in UIDS]
  contexts=[]
  for offset,count,r in zip([0,13063],[13063,456],finite_rows):
   assert r['completeWorldSHA256']==world_sha(w[offset:offset+count])and len(r['allFaces'])==len(r['completeAllOriginalFacetContexts'])==count
   assert r['completeActualDrawnGroundSHA256']==path['completeActorGroundSHA256'][0 if offset==0 else 1]
   assert [f['sourceFace']for f in r['allFaces']]==[c['sourceFace']for c in r['completeAllOriginalFacetContexts']]==list(range(count))
   assert not r['unprovedOrdinaryFaces']
   for i,(f,c)in enumerate(zip(r['allFaces'],r['completeAllOriginalFacetContexts'])):
    assert f['completeOriginalBoundProved']is True and c['groundProjectionCovered']is True and c['sourceFaceSHA256']==world_sha(w[offset+i])
   contexts+=r['completeAllOriginalFacetContexts']
  inventories=path['completeActualCensusForEveryOriginalBody'];assert len(inventories)==1120 and [r['originalBody']for r in inventories]==list(range(1120))
  for i,r in enumerate(inventories):
   c=r['completeActualEdgeCensus'];assert c['completeOriginalFaceIds']==ids[i]and c['completeWorldTrianglesSHA256']==world_sha(w)
   assert c['pointOnlyComponentGlue']is False and c['nonrenderingFacesProvideNoBridge']is True
   if i in common:
    assert len(c['sharedEdgeConnectedComponents'])==1
    assert sorted(c['sharedEdgeConnectedComponents'][0]+c['exactNonrenderingOriginalFaces'])==ids[i]
  assert census(w,zeros)==path['actualSourceZeroRepresentation']
  seed=path['mainPodiumGenuineGradeSeed'];assert seed['originalBody']==SEED and seed['diagnosticGradeSeedQualified']is True
  grade=seed['exactGenuineGradeIntervals'];assert grade==finite_rows[1]['complete363MainPodiumGradeInterfaces']and len(grade)==30
  assert seed['completeActualMainPodiumBodyCensus']==inventories[SEED]
  for g in grade:
   assert g['sourceFace']+13063 in ids[SEED]and g['exactActiveUpperGroundIntervals']
   assert all(v['upperEnvelopeCertifiedOnOpenInterval']is True and F(v['exactParameterOpenInterval'][0])<F(v['exactParameterOpenInterval'][1])for v in g['exactActiveUpperGroundIntervals'])
  cap=seed['strictCapPathsVerbatim'];assert cap==finite_rows[1]['strictPodiumClearCapWallPaths']and cap['allAffectedHavePaths']is True and not cap['rawExposureFailures']
  assert seed['capAffectedCount']==len(cap['affectedOriginalWallFaces']) and seed['vacuousCapIsNotIndependentCapCredit']==(not cap['affectedOriginalWallFaces'])
  parents={int(k):v for k,v in path['qualifiedDiagnosticParentForest'].items()if int(k)in common}
  assert set(parents)==common-{SEED}
  attempts={tuple(r['originalBodies']):r for r in path['allAttemptedOriginalPairs']};selected=[]
  for child,r in sorted(parents.items()):
   parent=r['parent'];assert parent in common and r['proofKey']==sorted([parent,child]),'Visual part used as a structural parent'
   a=attempts[tuple(r['proofKey'])];assert a['qualifiedExactInterface']is True and a['actualEndpointBodiesContinuous']is True
   q=a['witness'];faces=q['actualGlobalFaces'];assert len(faces)==2 and ((faces[0]in ids[child]and faces[1]in ids[parent])or(faces[1]in ids[child]and faces[0]in ids[parent]))
   assert all(f not in zeros and f not in inventories[b]['completeActualEdgeCensus']['exactNonrenderingOriginalFaces']for f,b in zip(faces,[z[0]for z in q['actualEndpointBodyMembership']]))
   assert q['actualExactContact']['dimension']>0 and q['allPointsExposedByCompleteEndpointFacets']is True
   assert q['completeStrictEndpointFacetContexts']==[contexts[f]for f in faces]
   assert all(c['groundProjectionCovered']is True and F(c['exactCertifiedLowerClearanceM'])>0 for c in q['completeStrictEndpointFacetContexts'])
   actors={0 if f<13063 else 1 for f in faces};interfaces=q['wholeInterfaceAgainstBothActorGrounds']
   assert {UIDS.index(v['actor'])for v in interfaces}==actors and len(interfaces)==len(actors)
   for v in interfaces:
    proof=v['proof'];assert proof['strictlyExposedWholePositiveInterface']is True and proof['closedWholeSegmentProjectionCovered']is True and F(proof['exactMinimumGapM'])>0
    assert proof['selection']['completeGroundSHA256']==path['completeActorGroundSHA256'][UIDS.index(v['actor'])]
   cur=child;seen=set()
   while cur!=SEED:assert cur in parents and cur not in seen and cur in common;seen.add(cur);cur=parents[cur]['parent']
   selected.append(dict(child=child,parent=parent,completeQualifiedWitnessVerbatim=q))
  for r in visual:
   i=r['originalBody'];c=inventories[i]['completeActualEdgeCensus'];assert c['sharedEdgeConnectedComponents']==[ids[i]]and not c['exactNonrenderingOriginalFaces']
  rows.append(dict(mode=mode,completeWorldSHA256=world_sha(w),completeActorGroundSHA256=path['completeActorGroundSHA256'],genuineMainPodiumGradeSeed=seed,complete827NonvisualParents=parents,all826CompleteStrictPositiveInterfaces=selected,all293VisualPartsAreTerminal=sorted(visualids),allOriginalZerosRetainedWithoutSupport=path['actualSourceZeroRepresentation'],allExtraActualCollapsedFacetsRetainedWithoutSupport=sorted(f for r in inventories for f in r['completeActualEdgeCensus']['exactNonrenderingOriginalFaces']),all1120OriginalBodiesAccounted=True))
 return dict(contract='twin-regency1120-complete-original-four-stream-role-composition-v1',binding=bound,completeSourceFacets=13519,completeOriginalNonzeroBodies=1120,complete827IndependentNonvisualBodies=sorted(common),complete155BoundaryVisualBodies=sorted(r['originalBody']for r in b155),complete138SourcePlacementVisualBodies=sorted(r['originalBody']for r in p138),all8OriginalZerosRetainedUncredited=zeros,allFourStreamRows=rows,nonrenderingFacetsReceiveNoSupportCredit=True,visualPartsNeverSupplyRootsBridgesOrHosts=True,wholeNativeReacceptance=False,sourceGeometryChanges=0,wholeCurrentIdentityForeignFoundationRuntimeBrowserStillMandatory=True,fullAcceptance=False,installationApproved=False,newlyInstalled=0)
