"""Named full Mount pair composition; visual associations never create roots.

The original 576-face podium body qualifies from actual finite upper-ground
grade interfaces and strict clear-cap paths. Only exact nonzero edge bodies and
positive-dimensional authored contacts propagate that root. All 204 backing
details/two podium details and three original open-bottom perimeters are
separate bounded roles, never bridges for any other component.
"""
from collections import deque
import json,hashlib
from fractions import Fraction as F
import numpy as np
from exact_original_shared_edge_component_census_v2_20261011 import census,exact_nonrendering
from exact_original_shell_intersections_20261009 import rational_face,intersection_points
from exact_original_component_contacts_20261009 import contact_measure
from original_strict_clear_cap_wall_paths_20261009 import verify as cap_verify
from exact_original_upper_ground_interfaces_20261009 import exact_upper_ground_interfaces
from mount_verdant_204_original_complete_back_visual_proposals_v1_20261011 import verify as visual204,membership,MEMBERSHIP_SHA256,SOURCE_T,SOURCE_P
from mount_verdant_original_two_back_mounted_visual_proposals_v1_20261011 import verify as visual2
from original_open_roof_perimeter_band_accounting_20261009 import verify as roof_perimeters

def canonical(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def sha(x):return hashlib.sha256(np.asarray(x,np.float64).tobytes()).hexdigest()

def verify(world,mode,components,zero_faces,finite_rows,restricted,roof_templates,podium_ground,*,expected_binding,current_binding):
 tri=np.asarray(world,float); ground=np.asarray(podium_ground,float)
 assert tri.shape==(15579,3,3) and np.isfinite(tri).all() and ground.ndim==3 and ground.shape[1:]==(3,3) and len(ground) and np.isfinite(ground).all()
 assert expected_binding==current_binding
 for key,value in [('complete15579WorldSHA256',sha(tri)),('complete973ComponentsSHA256',canonical(components)),('completeZeroFaceIDsSHA256',canonical(zero_faces)),('completeCurrentFiniteRowsSHA256',canonical(finite_rows)),('restrictedNonvisualSourceGraphSHA256',canonical(restricted)),('completeRoofPerimeterTemplatesSHA256',canonical(roof_templates)),('completeActualPodiumGroundSHA256',sha(ground))]: assert current_binding[key]==value,'A complete composition input changed'
 assert current_binding['sourceSHA256ByUID']=={'landsd/261717:0':SOURCE_T,'landsd/75782:0':SOURCE_P}
 assert len(components)==973 and zero_faces==sorted(set(zero_faces)) and len(zero_faces)==3
 partition=[i for c in components for i in c['globalOriginalFaces']]+zero_faces
 assert len(partition)==15579 and sorted(partition)==list(range(15579))
 assert all(exact_nonrendering(tri[i]) for i in zero_faces)
 inventories=[census(tri[:14938],list(range(14938))),census(tri[14938:],list(range(641)))];actual_components=[];actual_zero=[]
 for offset,inv in zip([0,14938],inventories):
  actual_components.extend([[offset+i for i in ids] for ids in inv['sharedEdgeConnectedComponents']]);actual_zero.extend(offset+i for i in inv['exactNonrenderingOriginalFaces'])
 assert actual_components==[c['globalOriginalFaces'] for c in components] and actual_zero==zero_faces
 assert len(finite_rows)==2 and [r['uid'] for r in finite_rows]==['landsd/261717:0','landsd/75782:0']
 complete_context=[]
 for offset,count,row in zip([0,14938],[14938,641],finite_rows):
  assert row['mode']==mode and row['completeWorldSHA256']==sha(tri[offset:offset+count]) and row['completeOriginalFaces']==count
  assert len(row['allFaces'])==len(row['completeAllOriginalFacetContexts'])==count
  assert [p['sourceFace'] for p in row['allFaces']]==[p['sourceFace'] for p in row['completeAllOriginalFacetContexts']]==list(range(count))
  for i,(p,ctx) in enumerate(zip(row['allFaces'],row['completeAllOriginalFacetContexts'])):
   coarse=p['priorCoarseBoundProofVerbatim']['completeOriginal'];proof=coarse if coarse['existingOrdinaryClearanceBoundProved'] else p['pairedExactOriginalFiniteBound']
   assert proof and proof['sourceFaceSHA256']==sha(tri[offset+i]) and proof['completeCurrentGroundSHA256']==row['completeActualDrawnGroundSHA256']
   assert proof['groundProjectionCovered'] is True and ctx['groundProjectionCovered'] is True
   assert p['completeOriginalBoundProved']==proof['existingOrdinaryClearanceBoundProved']
   assert ctx['minimum']['minimumGapM'] is not None and np.isfinite(ctx['minimum']['minimumGapM'])
   complete_context.append({**ctx,'sourceFace':offset+i})
  if offset==0:assert not row['unprovedOrdinaryFaces'] and all(p['completeOriginalBoundProved'] for p in row['allFaces'])
 podium=tri[14938:];pctx=finite_rows[1]['completeAllOriginalFacetContexts'];main=components[966]['globalOriginalFaces'];localmain=[i-14938 for i in main];assert len(localmain)==576
 bind=dict(completeOriginalWorldTrianglesSHA256=sha(podium),completeCurrentFacetContextsSHA256=canonical(pctx),exactOriginalContactListSHA256=canonical([]))
 cap=cap_verify(podium,pctx,[],expected_binding=bind,current_binding=bind)
 assert canonical(cap)==canonical(finite_rows[1]['strictPodiumClearCapWallPaths']) and cap['allAffectedHavePaths'] and not cap['rawExposureFailures']
 assert cap['affectedOriginalWallFaces']==finite_rows[1]['unprovedOrdinaryFaces'] and set(cap['affectedOriginalWallFaces'])<=set(localmain)
 for p in cap['paths']:assert p['hasExactOriginalStrictClearCapRoofPath'] and set(p['originalPath'])<=set(localmain)
 assert finite_rows[1]['completeActualDrawnGroundSHA256']==sha(ground)
 grade=exact_upper_ground_interfaces(podium,localmain,ground)
 assert canonical(grade)==canonical(finite_rows[1]['complete576MainPodiumGradeInterfaces'])
 paths={p['sourceFace']:p for p in cap['paths']};anchors=[]
 for g in grade:
  i=g['sourceFace']
  if i not in paths:continue
  assert pctx[i]['maximumObservedGapM']>0 and paths[i]['hasExactOriginalStrictClearCapRoofPath']
  assert all(p['upperEnvelopeCertifiedOnOpenInterval'] and F(p['exactParameterOpenInterval'][0])<F(p['exactParameterOpenInterval'][1]) for p in g['exactActiveUpperGroundIntervals'])
  anchors.append({**g,'completeIndependentSameMainBodyClearCapPath':paths[i]})
 assert anchors,'No genuine exposed finite-grade/clear-cap podium root'
 data=membership();visualids=sorted(map(int,data['exactOriginalMembership']));assert len(visualids)==204
 excluded=sorted(visualids+[311,312,313,967,972]);assert len(excluded)==209
 allowed=sorted(set(range(973))-set(excluded));assert len(allowed)==764
 assert restricted['mode']==mode and restricted['complete15579WorldSHA256']==sha(tri) and restricted['nonvisualAllowedComponents']==allowed and restricted['forbiddenVisualAndPendingFootingBridges']==excluded
 assert not restricted['unresolvedNonvisualComponents'] and restricted['conditionalReachedComponents']==allowed
 adj={i:set() for i in allowed};contacts=[]
 for r in restricted['completeRestrictedOriginalInterfaceReplays']:
  assert r['positiveDimensionalInterface'];a,b=r['components'];assert a in adj and b in adj
  x,y=r['selectedCurrentRepresentationWitnessGlobalFaces'];assert x in components[a]['globalOriginalFaces'] and y in components[b]['globalOriginalFaces'] and x not in zero_faces and y not in zero_faces
  points=intersection_points(rational_face(tri[x]),rational_face(tri[y]));assert points
  measure=contact_measure(points);assert measure['dimension']>0 and canonical(measure)==canonical(r['selectedCurrentRepresentationExactContact'])
  adj[a].add(b);adj[b].add(a);contacts.append(r)
 parent={966:None};todo=deque([966])
 while todo:
  a=todo.popleft()
  for b in sorted(adj[a]):
   if b not in parent:parent[b]=a;todo.append(b)
 assert set(parent)==set(allowed),'Nonvisual support is incomplete without visual bridges'
 hosts=sorted(i for k in allowed for i in components[k]['globalOriginalFaces']);assert hosts==data['conditionalHostGlobalFaces']
 vb=dict(sourceSHA256ByUID=current_binding['sourceSHA256ByUID'],complete15579WorldSHA256=sha(tri),membershipBytesSHA256=MEMBERSHIP_SHA256,completeHostFaceIdsSHA256=canonical(hosts))
 v204=visual204(tri,mode,expected_binding=vb,current_binding=vb);assert [r['originalBody'] for r in v204['rows']]==visualids
 pb=dict(uid='landsd/75782:0',sourceSHA256=SOURCE_P,completeWorldTrianglesSHA256=sha(podium),completeHostSourceFaceIdsSHA256=canonical(localmain))
 v2=visual2(podium,localmain,expected_binding=pb,current_binding=pb)
 # Exact source zeros complete the partition for the unchanged open-perimeter
 # helper but never enter any independent root, roof, contact or host set.
 allcomponents=components+[dict(globalOriginalFaces=[i],exactNonrenderingUncredited=True) for i in zero_faces]
 roles=[]
 assert sorted(r['originalBody'] for r in roof_templates)==[311,312,313]
 for r in sorted(roof_templates,key=lambda p:p['originalBody']):
  k=r['originalBody'];assert r['completeAll10OriginalGlobalFaces']==components[k]['globalOriginalFaces'] and r['completeBodyArithmeticSHA256']==sha(tri[components[k]['globalOriginalFaces']])
  assert r['conditionalEntireOpenBottomWithinExistingBand'] and not r['completeOriginalBottomFacetIDs']
  roles.append(dict(component=k,kind='open-bottom-upright-roof-equipment',completeOriginalFaces=components[k]['globalOriginalFaces'],completeOriginalLowerBoundary=r['completeAuthoredOpenBottomBoundary']))
 rb=dict(completeOriginalWorldTrianglesSHA256=sha(tri),completeComponentsSHA256=canonical(allcomponents),completeCurrentFacetContextsSHA256=canonical(complete_context),independentRootedComponentsSHA256=canonical([966]),visualOnlyComponentsSHA256=canonical(visualids+[967,972]),sourceRolesSHA256=canonical(roles))
 roof=roof_perimeters(tri,allcomponents,complete_context,[966],visualids+[967,972],roles,expected_binding=rb,current_binding=rb)
 assert roof['sourceRoofFootingComponents']==[311,312,313] and roof['independentlyRootedRoofComponents']==[966]
 resolved=set(parent)|set(visualids)|{311,312,313,967,972};assert resolved==set(range(973))
 return dict(contract='mount-verdant-complete-current-four-stream-independent-main-podium-root-and-bounded-original-role-composition-v1',mode=mode,binding=current_binding,completeOriginalFaces=15579,completeNonzeroBodies=973,completeIndependentNonvisualBodies=allowed,independentMainPodium576GradeAnchors=anchors,independentMainPodiumClearCapPaths=cap,completeIndependentNonvisualParents=parent,exactPositiveNonvisualInterfaces=contacts,all204VisualBackingRoles=v204,allTwoPodiumVisualBackingRoles=v2,threeActualOriginalOpenBottomRoofPerimeters=roof,originalOpenBottomKindIsShapeLabelOnlyNoFunctionInferred=True,allActualCandidateFiniteContextsBound=True,allSourceZerosRetainedUncredited=zero_faces,nonrenderingFacetsReceiveNoSupportCredit=True,visualRootOrBridgeCredit=False,openBottomRolesProvideNoOtherComponentBridge=True,closedSolidCertification=False,all973NonzeroBodiesAccounted=True,currentForeignIdentityFoundationRuntimeBrowserStillMandatory=True,fullAcceptance=False,installationApproved=False)
