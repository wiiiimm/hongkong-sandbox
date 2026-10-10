"""204 exact-source conditional complete-back visual associations, never roots.

170 original ten-face open-back shapes retain their complete four-edge opening;
34 original 28-face shapes retain every six-face backing patch and its entire
perimeter. The three horizontal open-bottom strips are deliberately separate.
No whole-front-facet claim, closed-solid certification, function inference,
structural transfer, current acceptance or installation is supplied here.
"""
from pathlib import Path
from collections import Counter,defaultdict
import json,hashlib
import numpy as np
from exact_original_shared_edge_component_census_v2_20261011 import census
from exact_original_edge_finite_facade_distance_band_v2_20261010 import verify as edge_verify
from exact_original_facet_orthogonal_finite_host_band_diagnostic_v1_20261011 import verify as facet_verify
MEMBERSHIP=Path(__file__).with_name('mount_verdant_204_exact_original_back_visual_proposal_membership_v1_20261011.json')
MEMBERSHIP_SHA256='f0c757b3cd5347f39837e07902f043229597296c718900a5f174255497308b23'
SOURCE_T='c8e54f42cd1f52ce94d1112a5c51bd58674fdbe38d8af6ac0de2b9498fbddec1'
SOURCE_P='4d3d6e5e5b08c6f33b1ce710161edc3554998f7afc7ee15ce29577f9e4c2f781'
SOURCE_WORLDS={'providerOriginal':'75e56f08a30f5e31004fb7e7fa149801f3b2b55c024180629a5faefefeec8209','capturedLiteral':'8d299c1a766aadf7b5cb337b1d1c4c289e2e0376a494e999048263ac8cc4c877','explicitLeftAssociatedF32ModelMatrix':'75e56f08a30f5e31004fb7e7fa149801f3b2b55c024180629a5faefefeec8209','explicitBalancedF32ModelMatrix':'75e56f08a30f5e31004fb7e7fa149801f3b2b55c024180629a5faefefeec8209'}
def sha(x):return hashlib.sha256(np.asarray(x,np.float64).tobytes()).hexdigest()
def canonical(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def membership():
 raw=MEMBERSHIP.read_bytes();assert hashlib.sha256(raw).hexdigest()==MEMBERSHIP_SHA256,'Exact original membership file changed';return json.loads(raw)
def backing_inventory(tri,ids):
 inv=census(tri,ids);assert inv['sharedEdgeConnectedComponents']==[ids] and not inv['exactNonrenderingOriginalFaces'];assert inv['nonmanifoldEdges']==0 and inv['twoFaceOrientationConflicts']==0
 edgefaces=defaultdict(list)
 for i in ids:
  for a,b in zip(tri[i],np.roll(tri[i],-1,axis=0)):
   assert not np.array_equal(a,b);edgefaces[tuple(sorted((tuple(a),tuple(b))))].append(i)
 boundary=sorted(e for e,faces in edgefaces.items() if len(faces)==1);degree=Counter(v for e in boundary for v in e);assert boundary and all(n==2 for n in degree.values()),'Incomplete backing perimeter'
 adjacency={v:set() for v in degree}
 for a,b in boundary:adjacency[a].add(b);adjacency[b].add(a)
 reached={min(adjacency)};todo=list(reached)
 while todo:
  for b in adjacency[todo.pop()]-reached:reached.add(b);todo.append(b)
 assert reached==set(adjacency),'Multiple disconnected backing rings'
 return inv,boundary,[dict(edge=[list(v) for v in e],incidentOriginalFaces=faces) for e,faces in sorted(edgefaces.items())]
def association(triangles,entry,hostids):
 """Geometry subroutine; association alone never certifies a source role."""
 tri=np.asarray(triangles,float);assert tri.ndim==3 and tri.shape[1:]==(3,3) and np.isfinite(tri).all();ids=entry['allBodyFaces'];assert ids==sorted(set(ids)) and not set(ids)&set(hostids);assert hostids==sorted(set(hostids)) and hostids
 body=census(tri,ids);assert body['sharedEdgeConnectedComponents']==[ids] and not body['exactNonrenderingOriginalFaces'] and not body['nonmanifoldEdges'] and not body['twoFaceOrientationConflicts'];back=entry['backPatchFaces'];facets=[]
 if entry['kind']=='complete-original-incidence-one-opening':
  assert len(ids)==10 and back is None and body['boundaryEdges']==4;patch,edges,inventory=backing_inventory(tri,ids);assert len(edges)==4
  # The complete authored back opening has two vertical sides and two
  # horizontal sides. A horizontal open bottom belongs to another contract.
  vertical=[e for e in edges if e[0][0]==e[1][0] and e[0][2]==e[1][2] and e[0][1]!=e[1][1]];horizontal=[e for e in edges if e[0][1]==e[1][1]];assert len(vertical)==len(horizontal)==2,'Not the authored upright BACK opening';kind='exact-original-ten-face-complete-open-back-visual-shape'
 elif entry['kind']=='complete-six-facet-authored-backing-patch':
  assert len(ids)==28 and body['boundaryEdges']==0 and back==sorted(set(back)) and len(back)==6 and set(back)<=set(ids);patch,edges,inventory=backing_inventory(tri,back)
  for i in back:
   proof=facet_verify(tri[i],tri[hostids]);assert proof['wholeFacetAssociated'],'Complete backing facet detached from finite host';facets.append(dict(originalBackingFace=i,wholeBackingFacetProof=proof))
  kind='exact-original-28-face-complete-six-facet-backed-visual-shape'
 else:raise AssertionError('Unknown source-specific authored shape')
 edgeproofs=[]
 for edge in edges:
  proof=edge_verify(np.asarray(edge),tri[hostids]);assert proof['verifiedCompleteOriginalEdgeFiniteFacadeBand'],'Incomplete finite backing perimeter association';edgeproofs.append(dict(wholeOriginalBackingEdge=[list(v) for v in edge],finiteHostBandProof=proof))
 return dict(proposedRole=kind,completeAllOriginalFaces=ids,completeOriginalBodyCensus=body,completeBackingFaces=[] if back is None else back,completeBackingPatchOrOpeningCensus=patch,completeAllBackingEdgeIncidences=inventory,completeAllBackingFacetProofs=facets,completeWholeBackingPerimeterProofs=edgeproofs,allOtherSourceFacesAndFreeEdgesRetained=True,rawWholeFrontFacetAndLowerLoopNegativesMustRemain=True,mountAssociationVerified=True,structuralRootCredit=False,structuralBridgeCredit=False,hostTransferCredit=False,closedSolidCertification=False,authoredFunctionInferred=False)
def verify(triangles,mode,*,expected_binding,current_binding):
 tri=np.asarray(triangles,float);assert tri.shape==(15579,3,3) and np.isfinite(tri).all();assert mode in SOURCE_WORLDS and sha(tri)==SOURCE_WORLDS[mode],'Only pinned original arithmetic streams qualify';data=membership();mapping=data['exactOriginalMembership'];hosts=data['conditionalHostGlobalFaces'];assert current_binding==expected_binding
 assert current_binding['sourceSHA256ByUID']=={'landsd/261717:0':SOURCE_T,'landsd/75782:0':SOURCE_P};assert current_binding['complete15579WorldSHA256']==sha(tri) and current_binding['membershipBytesSHA256']==MEMBERSHIP_SHA256 and current_binding['completeHostFaceIdsSHA256']==canonical(hosts)
 assert len(mapping)==204 and not set(mapping)&{'311','312','313'};assert sum(v['kind']=='complete-original-incidence-one-opening' for v in mapping.values())==170 and sum(v['kind']=='complete-six-facet-authored-backing-patch' for v in mapping.values())==34
 groups=census(tri[:14938],list(range(14938)))['sharedEdgeConnectedComponents'];assert len(groups)==966
 rows=[]
 for body,entry in sorted(mapping.items(),key=lambda p:int(p[0])):
  assert entry['allBodyFaces']==groups[int(body)],'Complete original detail membership changed';rows.append(dict(originalBody=int(body),**association(tri,entry,hosts)))
 return dict(contract='mount-verdant-exact204-complete-back-source-only-visual-proposals-v1',mode=mode,binding=current_binding,rows=rows,completeOriginal15579FacesRetained=True,threeHorizontalOpenBottomComponentsNotClaimed=True,independentlyGroundedActualHostQualificationStillRequired=True,allActualCurrentClearanceForeignRuntimeGatesStillRequired=True,visualRoleAccepted=False,structuralRootCredit=False,structuralBridgeCredit=False,currentAcceptance=False,installationApproved=False)
