"""Separate literal-runtime mounted sleeve contract; v1 stays immutable.

No parity tolerance substitutes for source equality. Both complete provider
original streams and exact literal actual-rendered world streams are fixed;
every actual rendered opening/facet is independently checked as well.
"""
import hashlib,numpy as np
from tung_sing_original_single_end_visual_sleeves_20261010 import source_roles,single_opening_role,SOURCE_SHA,WORLD_SHA,UID,SPECS,HOST,FINITE_HOSTS
from source_closed_components import components
LITERAL_RENDERED_WORLD_SHA='144809a23e43be6a92be2071eac0b83712eefa056082cf4b83038a8e762dd6dc'
LITERAL_ORIGINAL_STREAMS_SHA='f85e5b5017959db09503c02c38313ba1ecbd6bac517cc10c6256e578d4805e10'
def verify_current_visual_roles(triangles,rendered,drawn_ground,graph,source_streams,*,expected_binding,current_binding):
 """Source-owned visual parts only after independent complete current rooting.

Every ordinary actor/physical/foundation/runtime gate is still independent.
The graph keeps its two raw unresolved components. This method accounts for
only their unchanged original visual role; neither becomes a graph root/edge.
 """
 import json
 from exact_original_face_conservative_clearance_v4_20261010 import verify as clearance
 a=np.asarray(triangles,float);world=np.asarray(rendered,float);ground=np.asarray(drawn_ground,float)
 assert expected_binding==current_binding and world.shape==a.shape==(11445,3,3) and np.isfinite(world).all()
 assert ground.ndim==3 and ground.shape[1:]==(3,3) and len(ground) and np.isfinite(ground).all()
 sha=lambda v:hashlib.sha256(v).hexdigest()
 # Two literal source/runtime streams are independently bound. The v1
 # exact-equality failure is preserved; no coordinate tolerance replaces it.
 assert sha(a.astype('<f8').tobytes())==WORLD_SHA and sha(world.astype('<f8').tobytes())==LITERAL_RENDERED_WORLD_SHA
 assert sha(json.dumps(source_streams,sort_keys=True,separators=(',',':'),allow_nan=False).encode())==LITERAL_ORIGINAL_STREAMS_SHA and source_streams['sourceSHA256']==SOURCE_SHA
 assert current_binding['completeProviderRootAndStreamsSHA256']==LITERAL_ORIGINAL_STREAMS_SHA
 assert current_binding['completeOriginalWorldSHA256']==WORLD_SHA and current_binding['completeActualRenderedWorldSHA256']==sha(world.astype('<f8').tobytes()) and current_binding['completeActualDrawnGroundSHA256']==sha(ground.astype('<f8').tobytes())
 assert current_binding['completeCurrentRootedGraphSHA256']==sha(json.dumps(graph,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
 for key in ['currentManifestSHA256','completeCurrentPhysicalSHA256','completeCurrentForeignActorScopeSHA256','completeProviderRootAndStreamsSHA256']:assert len(current_binding[key])==64
 assert graph['completeOriginalFaces']==12751 and graph['completeOriginalComponentCount']==387 and graph['completeOriginalActorUIDs']==sorted([UID,'landsd/254604:0','landsd/126434:0'])
 assert graph['genuineGroundAnchorComponents']==[361,365]
 parents=graph['groundRootedComponentParents'];assert parents.get(str(HOST),parents.get(HOST)) is not None
 assert set(range(387))-set(graph['resolvedOriginalComponents'])==set(SPECS) and HOST in graph['resolvedOriginalComponents']
 assert graph['reasons']==['unresolved-original-component:343','unresolved-original-component:344'] and not graph['supportInterfaceAccepted']
 assert all(not (set(v['components'])&set(SPECS)) for v in graph['exactOriginalContacts'])
 role=source_roles(a,SOURCE_SHA,WORLD_SHA);bounded=[];rendered_roles=[]
 topology=components(a)['components']
 for k,ids in SPECS.items():rendered_roles.append({'originalComponent':k,**single_opening_role(world,ids,topology[HOST]['faceIndices'],FINITE_HOSTS[k])})
 for k,ids in SPECS.items():
  for i in ids:
   original=clearance(a[i],ground);actual=clearance(world[i],ground);assert original['existingOrdinaryClearanceBoundProved'] and actual['existingOrdinaryClearanceBoundProved']
   bounded.append({'originalComponent':k,'originalSourceFace':i,'completeOriginalFacetClearance':original,'completeActualRenderedFacetClearance':actual})
 return {**role,'completeIndependentCurrentOriginalFacetClearance':bounded,'completeActualRenderedVisualMounts':rendered_roles,'priorExactOriginalRenderedEqualityPassed':bool(np.array_equal(a,world)),'maximumObservedActualWorldArithmeticDifferenceM':float(np.max(np.abs(a-world))),'currentBinding':current_binding,'rawCurrentGraphReasonsVerbatim':graph['reasons'],'hostIndependentlyReachesGenuineCurrentPlatformRoot':True,'typedOriginalVisualRoleAccepted':True,'physicalAccepted':False,'installationApproved':False,'ordinaryCurrentForeignFoundationRuntimeGatesRemainIndependent':True}
