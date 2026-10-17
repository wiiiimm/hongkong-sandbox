"""Two named source-authored horizontal visual sleeves; no roots or bridges.

The complete four-edge original mounting opening must meet finite surfaces of
its independently rooted original host within the EXISTING fixed .1m band.
The second original opening is retained as a free visual end, not support.
"""
import hashlib,numpy as np
from glorious_peak_original_mounted_detail_roles_v2_20261010 import boundaries,nearby_hosts,mount_edge
from exact_shell_context_accelerated_20261009 import shell_self_intersections
from source_closed_components import components
from exact_original_edge_finite_facade_distance_band_v2_20261010 import verify as finite_band
SOURCE_SHA='01b2b8a50351975e57fa036e8c358f72b93209c684a29194b5bcfeebaa2de60c'
UID='landsd/53800:0'
SPECS={343:[9229,9230,9231,9232,11296,11297,11298,11299],344:[9233,9234,9235,9236,11300,11301,11302,11303]}
HOST=1
WORLD_SHA='eb60a508924631729decbce9d436d21afd9f3222886b4b17c4fa44355a9969ef'
FINITE_HOSTS={343:[10158,11013,11269,11276],344:[10158,11013,11270]}

def single_opening_role(tri,faces,hostfaces,finite_host_faces):
 a=np.asarray(tri,float);assert a.ndim==3 and a.shape[1:]==(3,3) and np.isfinite(a).all();assert len(faces)==8 and len(set(faces))==8 and hostfaces and not set(faces)&set(hostfaces)
 assert finite_host_faces and set(finite_host_faces)<=set(hostfaces)
 part=a[faces];n=np.cross(part[:,1]-part[:,0],part[:,2]-part[:,0]);assert np.all(np.linalg.norm(n,axis=1)>0)
 loops=boundaries(a,faces);assert len(loops)==2 and all(len(v)==4 for v in loops);check=shell_self_intersections(part);assert check['selfIntersectionFree']
 # This role is a horizontal four-sided sleeve, not the existing vertical
 # upper-opening role. Both original openings span the full same Y interval.
 lo,hi=part[:,:,1].min(),part[:,:,1].max();assert hi>lo
 for loop in loops:assert min(min(p[1],q[1]) for _,p,q in loop)==lo and max(max(p[1],q[1]) for _,p,q in loop)==hi
 near,outside=nearby_hosts(a,faces,hostfaces);normal=np.cross(a[:,1]-a[:,0],a[:,2]-a[:,0]);evaluated=[];mounted=[]
 for li,loop in enumerate(loops):
  edge_results=[]
  for edge in loop:
   trials=[mount_edge(a,edge,near,axis,host_scope_faces=hostfaces) for axis in [0,2] if any(normal[j,axis]!=0 for j in near)];assert trials
   finite=finite_band([edge[1],edge[2]],a[near]);finite['finiteOriginalHostSourceFaces']=near;edge_results.append({'allOriginalAxisTrials':trials,'completeOriginalFiniteEuclideanBand':finite})
  accepted=all(r['completeOriginalFiniteEuclideanBand']['verifiedCompleteOriginalEdgeFiniteFacadeBand'] for r in edge_results);evaluated.append({'originalOpening':li,'completeOriginalDirectedOpening':[{'originalSourceFace':i,'vertices':[list(p),list(q)]} for i,p,q in loop],'everyCompleteOriginalEdgeTrial':edge_results,'completeOpeningWithinExistingVisualBand':accepted})
  if accepted:mounted.append(li)
 assert mounted,'One complete authored original opening must mount; partial/point-only mount cannot qualify'
 # An additional end being near a finite surface is not structural support.
 # The first fully certified literal opening is selected deterministically;
 # the other opening remains free/unclaimed even if it also lies near a host.
 mounted_index=min(mounted)
 return {'role':'authored-single-end-mounted-horizontal-original-visual-sleeve','allOriginalFaces':faces,'completeOriginalMountedOpeningIndex':mounted_index,'completeOriginalFreeOpeningIndex':1-mounted_index,'bothCompleteOriginalOpeningDispositions':evaluated,'completeAlreadyRootedHostFaceScope':hostfaces,'rigorouslyOutsideFixedBandHostFaces':outside,'originalSelfIntersection':check,'existingFixedVisualMountBandM':.1,'rawExactNoContactPreserved':True,'rawBothEndMountFailurePreserved':True,'freeEndSupportCredit':False,'functionalClaim':False,'closedSolidCertified':False,'syntheticCapCreated':False,'structuralRootCredit':False,'structuralBridgeCredit':False,'sourceGeometryChanges':0}

def source_roles(tri,source_sha,world_sha):
 a=np.asarray(tri,float);assert a.shape==(11445,3,3) and np.isfinite(a).all() and source_sha==SOURCE_SHA and world_sha==WORLD_SHA and hashlib.sha256(a.astype('<f8').tobytes()).hexdigest()==world_sha
 topology=components(a)['components'];assert len(topology)==365
 partition=[i for p in topology for i in p['faceIndices']];assert sorted(partition)==list(range(11445)) and len(partition)==len(set(partition))
 result=[]
 for k,faces in SPECS.items():
  assert topology[k]['faceIndices']==faces;proof=single_opening_role(a,faces,topology[HOST]['faceIndices'],FINITE_HOSTS[k]);result.append({'originalComponent':k,'actorUID':UID,'requiredIndependentlyRootedOriginalHostComponent':HOST,**proof})
 return {'uid':UID,'sourceSHA256':source_sha,'completeOriginalWorldSHA256':world_sha,'completeOriginalFaces':11445,'completeOriginalComponents':365,'visualOriginalComponents':[343,344],'all16OriginalVisualFacesRetained':16,'completeSourceOnlyVisualRoles':result,'visualGroundRootCredit':False,'visualStructuralBridgeCredit':False,'sourceGeometryChanges':0,'physicalAccepted':False,'installationApproved':False,'mandatoryIndependentCurrentHostRootClearanceForeignFoundationRuntimeGates':True}

def verify_current_visual_roles(triangles,rendered,drawn_ground,graph,*,expected_binding,current_binding):
 """Source-owned visual parts only after independent complete current rooting.

Every ordinary actor/physical/foundation/runtime gate is still independent.
The graph keeps its two raw unresolved components. This method accounts for
only their unchanged original visual role; neither becomes a graph root/edge.
 """
 import json
 from exact_original_face_conservative_clearance_v4_20261010 import verify as clearance
 a=np.asarray(triangles,float);world=np.asarray(rendered,float);ground=np.asarray(drawn_ground,float)
 assert expected_binding==current_binding and world.shape==a.shape==(11445,3,3) and np.isfinite(world).all() and np.array_equal(world,a)
 assert ground.ndim==3 and ground.shape[1:]==(3,3) and len(ground) and np.isfinite(ground).all()
 sha=lambda v:hashlib.sha256(v).hexdigest()
 assert current_binding['completeOriginalWorldSHA256']==WORLD_SHA and current_binding['completeActualRenderedWorldSHA256']==sha(world.astype('<f8').tobytes()) and current_binding['completeActualDrawnGroundSHA256']==sha(ground.astype('<f8').tobytes())
 assert current_binding['completeCurrentRootedGraphSHA256']==sha(json.dumps(graph,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
 for key in ['currentManifestSHA256','completeCurrentPhysicalSHA256','completeCurrentForeignActorScopeSHA256','completeProviderRootAndStreamsSHA256']:assert len(current_binding[key])==64
 assert graph['completeOriginalFaces']==12751 and graph['completeOriginalComponentCount']==387 and graph['completeOriginalActorUIDs']==sorted([UID,'landsd/254604:0','landsd/126434:0'])
 assert graph['genuineGroundAnchorComponents']==[365]
 parents=graph['groundRootedComponentParents'];assert parents.get(str(HOST),parents.get(HOST)) is not None
 assert set(range(387))-set(graph['resolvedOriginalComponents'])==set(SPECS) and HOST in graph['resolvedOriginalComponents']
 assert graph['reasons']==['unresolved-original-component:343','unresolved-original-component:344'] and not graph['supportInterfaceAccepted']
 assert all(not (set(v['components'])&set(SPECS)) for v in graph['exactOriginalContacts'])
 role=source_roles(a,SOURCE_SHA,WORLD_SHA);bounded=[]
 for k,ids in SPECS.items():
  for i in ids:
   original=clearance(a[i],ground);actual=clearance(world[i],ground);assert original['existingOrdinaryClearanceBoundProved'] and actual['existingOrdinaryClearanceBoundProved']
   bounded.append({'originalComponent':k,'originalSourceFace':i,'completeOriginalFacetClearance':original,'completeActualRenderedFacetClearance':actual})
 return {**role,'completeIndependentCurrentOriginalFacetClearance':bounded,'currentBinding':current_binding,'rawCurrentGraphReasonsVerbatim':graph['reasons'],'hostIndependentlyReachesGenuineCurrentPlatformRoot':True,'typedOriginalVisualRoleAccepted':True,'physicalAccepted':False,'installationApproved':False,'ordinaryCurrentForeignFoundationRuntimeGatesRemainIndependent':True}
