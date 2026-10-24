"""Complete Elements source accounting: 866 nonvisual paths +132 visual bodies.

Only the twelve qualified actual native interfaces seed a nonvisual forest.
Named visual units remain terminal render representations; they never become
parents, roots or hosts. Existing complete immutable numeric proofs are reused
only under their full canonical/world binding, independently fenced by caller.
"""
from fractions import Fraction as F
import numpy as np
from elements24_named_original_mounted_visual_surface_proposal_v1_20261011 import MODES,SOURCE_SHA,canonical,world_sha
from elements11_named_original_visual_placement_proposal_v1_20261011 import WORLD_SHA
from exact_original_shared_edge_component_census_v2_20261011 import census
SEEDS={4,499,503,504,506,911,915,916,923,924,925,926}
UIDS=['landsd/204145:0','landsd/204143:0']

def binding(worlds,graph,finite,paths,caps,lateral,named24,named4,named11):
 return dict(sourceSHA256ByUID={r['uid']:r['sourceSHA256']for r in graph['binding']['completeSourceInputs'][:2]},completeWorldSHA256={m:world_sha(worlds[m])for m in MODES},completeGraphSHA256=canonical(graph),completeFiniteSHA256=canonical(finite),completeOwnedPathSHA256=canonical(paths),completeNativeGradeCapSHA256=canonical(caps),completeLateralUnitsSHA256=canonical(lateral),named24SHA256=canonical(named24),named4SHA256=canonical(named4),named11SHA256=canonical(named11))

def verify(worlds,graph,finite,paths,caps,lateral,named24,named4,named11,*,expected_binding):
 arrays={m:np.asarray(worlds[m],np.float64)for m in MODES};assert set(worlds)==set(MODES)
 assert all(w.shape==(23809,3,3)and np.isfinite(w).all()and world_sha(w)==WORLD_SHA[m]for m,w in arrays.items())
 bound=binding(arrays,graph,finite,paths,caps,lateral,named24,named4,named11);assert bound==expected_binding and bound['sourceSHA256ByUID']==SOURCE_SHA
 components=graph['components'][:998];assert len(components)==998
 zeros=[i for i in graph['exactNonrenderingGlobalFacesRetained']if i<23809];assert len(zeros)==47 and zeros==sorted(set(zeros))
 bodies=[r['globalOriginalFaces']for r in components];all_body_faces=[f for ids in bodies for f in ids]
 assert len(all_body_faces)==len(set(all_body_faces))and sorted(all_body_faces+zeros)==list(range(23809))
 for i,(r,ids)in enumerate(zip(components,bodies)):
  uid='landsd/204145:0'if max(ids)<12129 else'landsd/204143:0';assert r['actorUID']==uid and ids==sorted(set(ids))
 assert caps['nativeBodyReceivesNoRootSeed']is True and caps['wholeNativeReacceptance']is False
 p24=named24['all24ExactNamedSourceVisualProposals'];p4=named4['all4ExactNamedCompletePerimeterVisualSheetProposals'];p11=named11['all11NamedOriginalVisualPlacementProposals']
 assert [len(p24),len(p4),len(p11)]==[24,4,11]
 named=p24+p4+p11;named_ids=[r['originalBody']for r in named];assert len(set(named_ids))==39
 for r in named:
  i=r['originalBody'];assert r['completeOriginalFaces']==bodies[i]and r['uid']==components[i]['actorUID']
  assert r['conditionalSourceVisualRoleProposal']is True and r['structuralRootCredit']is False and r['structuralBridgeCredit']is False and r['visualPartsNeverQualifyHosts']is True and r['currentAcceptance']is False
  proof=r.get('allFourStreamProofs',r.get('allFourStreamCompleteProofs'));assert len(proof)==4 and {p['mode']for p in proof}==set(MODES)
 result=[]
 for mode in MODES:
  w=arrays[mode];path=next(r for r in paths['rows']if r['mode']==mode);cap=next(r for r in caps['rows']if r['mode']==mode);unitrow=next(r for r in lateral['rows']if r['mode']==mode)
  assert path['completeWorldSHA256']==unitrow['completeWorldSHA256']==WORLD_SHA[mode]and path['noWholeNativeBodySeed']is True
  assert path['completeOriginalBodyCount']==998 and path['completeOwnedFacetCount']==23809 and path['sourceOriginalZeroFacetsRetained']==zeros
  assert path['completeNativeGroundSHA256']==cap['completeGroundSHA256']
  rows=[next(r for r in finite['rows']if r['mode']==mode and r['uid']==u)for u in UIDS]
  for offset,count,r in zip([0,12129],[12129,11680],rows):
   assert r['completeWorldSHA256']==world_sha(w[offset:offset+count])and [f['sourceFace']for f in r['allFaces']]==list(range(count))
   assert all(f['closedProjectionCovered']is True and f['existingOrdinaryClearanceBoundProved']is True and f['strictlyExposedWholeFacet']is True for f in r['allFaces'])
  saved=path['completeActualCensusForEveryOriginalBody'];assert len(saved)==998 and [r['originalBody']for r in saved]==list(range(998))
  # Reuse independently completed whole-actor edge censuses only under each
  # literal complete world hash and whole finite-document binding above.
  actual_groups=[];actual_zeros=[]
  for offset,count,r in zip([0,12129],[12129,11680],rows):
   c=r['completeNonzeroEdgeCensus'];assert c['completeWorldTrianglesSHA256']==world_sha(w[offset:offset+count]) and c['completeOriginalFaceIds']==list(range(count))
   assert c['pointOnlyComponentGlue']is False and c['nonrenderingFacesProvideNoBridge']is True
   actual_groups.extend([[f+offset for f in group]for group in c['sharedEdgeConnectedComponents']]);actual_zeros.extend(f+offset for f in c['exactNonrenderingOriginalFaces'])
  assert actual_zeros==zeros
  for i,r in enumerate(saved):
   assert r['completeActualBodyCensus']['sharedEdgeConnectedComponents']==[bodies[i]]and not r['completeActualBodyCensus']['exactNonrenderingOriginalFaces']
  # Original zeros are preserved and never inserted into a support endpoint.
  # Actual arithmetic representations of these facets remain explicit rather
  # than being silently called nonrendering after a transform.
  assert actual_groups==bodies
  source_zero_actual=census(w,zeros);assert source_zero_actual==path['actualRepresentationOfSourceZeroFacets']
  seeds={r['originalBody']for r in path['qualifiedNativeInterfaceNominations']if r['diagnosticQualifiedSeed']};assert seeds==SEEDS
  capseeds={r['ownedBody']for r in cap['all20OriginalInterfacesAccounted']if r['diagnosticStrictGradeCapPath']};assert SEEDS<=capseeds
  for seed in seeds:
   nomination=next(r for r in path['qualifiedNativeInterfaceNominations']if r['originalBody']==seed);native=nomination['wholeBoundedNativePath']
   assert native==next(r for r in cap['all20OriginalInterfacesAccounted']if r['ownedBody']==seed)
   assert nomination['actualBodyContinuous']is True and nomination['endpointIsActualNonzeroBodyFace']is True and nomination['ownedEndpointWholeFacet']['strictlyExposedWholeFacet']is True
   assert native['diagnosticStrictGradeCapPath']is True and native['actualPositiveDimensionalContact']is True and native['actualExactContact']['dimension']>0 
   assert native['ownedUID']==components[seed]['actorUID']
   owned_offset,owned_count=(0,12129)if native['ownedUID']==UIDS[0]else(12129,11680)
   assert 0<=native['ownedFace']<owned_count
   owned_global_face=native['ownedFace']+owned_offset
   assert owned_global_face==native['originalContact']['globalOriginalFaces'][0]==nomination['ownedEndpointWholeFacet']['sourceFace']and owned_global_face in bodies[seed]
   assert native['upwardCapFaces']and native['gradeWall']['exactUpperGroundIntervals']and native['gradeWall']['wholeRawFiniteProof']['groundProjectionCovered']is True and native['gradeWall']['wholeSharedEdgeProof']['strictlyExposedWholePositiveInterface']is True
   assert all(x['completeFiniteProof']['groundProjectionCovered']is True and F(x['completeFiniteProof']['exactCertifiedLowerClearanceM'])>0 for x in native['completeSelectedFiniteFaces'])
   assert all(x['completeEdgeProof']['strictlyExposedWholePositiveInterface']is True for x in native['completeSelectedStrictEdges'])
  nonvisual=set(path['qualifiedDiagnosticOwnedBodies']);assert len(nonvisual)==866 and seeds<=nonvisual and not path['unprovedGeometricCandidateBodies']
  parents={int(k):v for k,v in path['qualifiedDiagnosticParentForest'].items()};assert set(parents)==nonvisual-seeds
  attempts={tuple(p['originalBodies']):p for p in path['allAttemptedOriginalOwnedPairs']}
  for child,r in parents.items():
   parent=r['parent'];assert parent in nonvisual and child in nonvisual and r['proofKey']==sorted([child,parent]);p=attempts[tuple(r['proofKey'])]
   assert p['qualifiedExactInterface']is True and p['actualEndpointBodyContinuity']is True
   witness=p['witness'];pair=witness['actualGlobalFaces'];assert len(pair)==2 and ((pair[0]in bodies[child]and pair[1]in bodies[parent])or(pair[1]in bodies[child]and pair[0]in bodies[parent]))
   assert witness['actualExactContact']['dimension']>0 and witness['allPointsExposedByCompleteEndpointFacets']is True and witness['wholePositiveInterfaceProof']['strictlyExposedWholePositiveInterface']is True
   assert all(f['strictlyExposedWholeFacet']is True for f in witness['completeEndpointFacetProofs'])
   seen=set();cur=child
   while cur not in seeds:assert cur in parents and cur not in seen;seen.add(cur);cur=parents[cur]['parent']
  units=unitrow['all31CompleteUnitLateralDiagnoses'];assert len(units)==31;unit_ids=[]
  for u in units:
   ids=u['completeOriginalBodies'];assert len(ids)==3 and len(set(ids))==3 and len(u['complete22OriginalUnitFaceIds'])==22
   assert sorted(f for b in ids for f in bodies[b])==sorted(u['complete22OriginalUnitFaceIds'])
   assert u['conditionalLateralMountCandidate']is True and u['actualPatchMembershipMatchesCompleteSource']is True and u['allInternalActualInterfacesStrictPositive']is True
   assert u['completeOppositePatchBandCandidates']
   for pair in u['completeOppositePatchBandCandidates']:
    for index in pair:
     patch=u['allCompleteLateralPatchProofs'][index];assert patch['completePatchWithinExistingFiniteBand']is True
     assert all(f['wholeFacetWithinExistingFiniteHostBand']is True for f in patch['allFourActualFacetProofs'])and all(e['completeEdgeWithinExistingFiniteHostBand']is True for e in patch['allActualPatchBoundaryProofs'])
     host=patch['completeSameActorQualifiedHostSelection'];assert host['allSelectedHostsBelongToNonvisualQualifiedPaths']is True
     eligible={f for b in nonvisual if components[b]['actorUID']==components[ids[1]]['actorUID']for f in bodies[b]};assert set(host['selectedGlobalHostFaces'])<=eligible
   unit_ids.extend(ids)
  visual=unit_ids+named_ids;assert len(visual)==len(set(visual))==132 and not set(visual)&nonvisual and set(visual)|nonvisual==set(range(998))
  result.append(dict(mode=mode,completeOwnedWorldSHA256=WORLD_SHA[mode],completeOwnedFaces=23809,qualifiedNonvisualBodies=sorted(nonvisual),nativeInterfaceSeeds=sorted(seeds),boundedNonvisualParentForest=parents,complete31VisualAssemblyBodies=[u['completeOriginalBodies']for u in units],complete39NamedVisualBodies=sorted(named_ids),complete132VisualBodies=sorted(visual),completeActualSourceZeroRepresentationVerbatim=source_zero_actual,originalZerosReceiveNoSupportCredit=True,allCompleteOwnedFacetsStrictlyExposed=True,visualBodiesNeverEnterStructuralForest=True))
 return dict(contract='elements998-complete-source-four-stream-bounded-native-path-and-named-visual-role-composition-v3',binding=bound,uids=UIDS,completeOriginalFaces=23809,completeNonzeroOriginalBodies=998,completeStructuralPathBodies=866,completeNonstructuralVisualBodies=132,all47OriginalZeroFacetsPreservedUncredited=zeros,allFourStreamCompositions=result,noWholeNativeReacceptance=True,noVisualRootBridgeOrHostCredit=True,sourceGeometryChanges=0,currentAcceptance=False,installationApproved=False,newlyInstalled=0)
