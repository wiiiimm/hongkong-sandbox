"""Named unchanged Ko Fung visual façade details; zero support/root credit.

Raw negative minima stay verbatim; impossible out-of-facet positions have a
separate complete finite bound under the same -.5 m limit. Complete authored open-back perimeters use the existing finite ±.1m surface
band. The separate triangular seam has two exact original top-edge mounts.
The caller must independently establish provider/current/foreign/source gates.
"""
import hashlib,json
from fractions import Fraction
import numpy as np
from original_open_facade_boundary_band_diagnostic_20261010 import diagnose
from exact_original_face_conservative_clearance_v2_20261010 import verify as finite_clearance
from exact_original_triangle_distance_20261009 import point_face
from exact_original_shell_intersections_20261009 import rational_face,intersection_points
from exact_shell_context_accelerated_20261009 import shell_self_intersections

SOURCES={'landsd/79097:0':'22b1fc96be53e64bf56cf4898b30649ef413851a4ad9d408d8efc7ad4ebdfcfe','landsd/110480:0':'fcd7083029cff8350b2651d18aa2ea66750cf35c7927af3aa79b5fcb55f9c248'}
def canonical(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def independent_visual_clearance(tri,world,ground,faces,contexts):
 assert len(contexts)==len(faces) and {c['sourceFace'] for c in contexts}==set(faces)
 byface={c['sourceFace']:c for c in contexts};proofs=[]
 for i in faces:
  c=byface[i];assert c['groundProjectionCovered'] is True and c['minimum']
  original=finite_clearance(tri[i],ground);rendered=finite_clearance(world[i],ground)
  assert original['existingOrdinaryClearanceBoundProved'] and rendered['existingOrdinaryClearanceBoundProved'],'Original and actual rendered whole facets must independently satisfy unchanged -.5 limit'
  invalid=False
  if c['minimum']['minimumGapM']<-.5:
   position=c['minimum'].get('position');assert position and len(position)==3
   y=position[1];assert (y<tri[i,:,1].min() or y>tri[i,:,1].max()) and (y<world[i,:,1].min() or y>world[i,:,1].max()),'A genuine finite raw below-limit position cannot use numerical-invalidity route'
   invalid=True
  proofs.append(dict(sourceFace=i,completeOriginalFiniteClearance=original,completeActualRenderedFiniteClearance=rendered,rawDiagnosticMinimumVerbatim=c['minimum'],rawReportedMinimumOutsideFiniteSource=invalid,rawDiagnosticChanged=False))
 return proofs

def open_back_role(triangles,faces,host_faces,contexts,ground,rendered_world):
 tri=np.asarray(triangles,float);proof=diagnose(tri,faces,host_faces)
 assert proof['sourceOnlyBoundaryBandPassed'],'Every authored opening edge must meet complete finite rooted façade band'
 assert len(contexts)==len(faces) and {c['sourceFace'] for c in contexts}==set(faces)
 independent=independent_visual_clearance(tri,np.asarray(rendered_world,float),np.asarray(ground,float),faces,contexts)
 axis=proof['signedCoordinatePermutation'][1];sign=proof['heightCoordinateSign'];front=tri[faces][:,:,axis]*sign;opening=np.asarray([p for e in proof['completeOriginalDirectedBoundaryEdges'] for p in e['vertices']])[:,axis]*sign
 assert front.min()>=opening.min() and front.max()>opening.max(),'Actual authored front must project outward from its sole original opening'
 selfcheck=shell_self_intersections(tri[faces]);assert selfcheck['selfIntersectionFree'],'Self-intersecting visual component'
 return dict(role='authored-open-back-mounted-facade-detail',allOriginalFaces=faces,completeOriginalOpening=proof,originalSelfIntersection=selfcheck,actualOutwardFrontProtrusionM=float(front.max()-opening.max()),independentCompleteFacetClearance=independent,closedSolidCertified=False,syntheticBackCapCreated=False,structuralRootCredit=False,structuralBridgeCredit=False)
def slanted_triangle_seam_role(triangles,faces,host_faces,contexts,ground,rendered_world):
 tri=np.asarray(triangles,float);assert len(faces)==1 and type(faces[0])is int and host_faces
 i=faces[0];face=tri[i];normal=np.cross(face[1]-face[0],face[2]-face[0]);length=np.linalg.norm(normal);assert length>0 and abs(normal[1])<=.25*length
 independent=independent_visual_clearance(tri,np.asarray(rendered_world,float),np.asarray(ground,float),faces,contexts)
 # The actual authored high edge is slanted. No flat-top epsilon locator and
 # no fictional projected corner are introduced.
 order=sorted(range(3),key=lambda k:(float(face[k,1]),tuple(face[k])),reverse=True);a,b,c=[tuple(Fraction.from_float(float(x)) for x in face[k]) for k in order]
 assert c[1]<min(a[1],b[1]) and a!=b
 anchors=[]
 for corner,p in enumerate([a,b]):
  for j in host_faces:
   assert j!=i
   if point_face(p,rational_face(tri[j]))[0]==0:
    points=intersection_points(rational_face(face),rational_face(tri[j]));assert points=={p},'Positive-length authored contact belongs to strict structural graph'
    anchors.append(dict(corner=corner,originalHostFace=j,exactOriginalPoint=list(map(str,p))))
 assert {r['corner'] for r in anchors}=={0,1},'Both distinct actual authored top-edge endpoints must attach exactly'
 return dict(role='authored-hanging-slanted-triangular-facade-seam',allOriginalFaces=faces,actualTopEdge=[list(map(str,a)),list(map(str,b))],actualLowerVertex=list(map(str,c)),exactOriginalTopEdgeMounts=anchors,independentCompleteFacetClearance=independent,structuralRootCredit=False,structuralBridgeCredit=False)
def verify(triangles,contexts,strict_graph,drawn_ground,rendered_world,*,expected_role,expected_binding,current_binding):
 tri=np.asarray(triangles,float);assert tri.ndim==3 and tri.shape[1:]==(3,3) and np.isfinite(tri).all()
 world=np.asarray(rendered_world,float);ground=np.asarray(drawn_ground,float);assert world.shape==tri.shape and np.isfinite(world).all() and ground.ndim==3 and ground.shape[1:]==(3,3) and np.isfinite(ground).all() and np.max(np.abs(world-tri))<=1e-9
 assert current_binding==expected_binding and current_binding
 assert current_binding['completeActualRenderedWorldSHA256']==hashlib.sha256(world.tobytes()).hexdigest() and current_binding['completeCurrentDrawnGroundSHA256']==hashlib.sha256(ground.tobytes()).hexdigest()
 for key,value in [('completeOriginalWorldTrianglesSHA256',hashlib.sha256(tri.tobytes()).hexdigest()),('completeContinuousContextsSHA256',canonical(contexts)),('completeStrictOriginalGraphSHA256',canonical(strict_graph)),('frozenProviderRoleSHA256',canonical(expected_role))]:assert current_binding[key]==value
 for key in ['actualProviderRootAndStreamsSHA256','completeCurrentPhysicalSHA256','completeCurrentForeignScopeSHA256','currentManifestSHA256']:assert len(current_binding[key])==64
 assert expected_role['contract']=='ko-fung-complete-original-mounted-facade-role-v3'
 assert expected_role['sources']==SOURCES
 components=strict_graph['components'];partition=[i for c in components for i in c['globalOriginalFaces']];assert sorted(partition)==list(range(len(tri))) and len(partition)==len(set(partition))
 assert len(contexts)==len(tri) and all(c['sourceFace']==i for i,c in enumerate(contexts))
 rooted=set(strict_graph['resolvedOriginalComponents']);wanted=sorted(set(range(len(components)))-rooted);assert wanted==expected_role['allVisualComponents'] and wanted and not strict_graph['supportInterfaceAccepted']
 assert strict_graph['ordinaryGroundRootComponents'] and not set(wanted)&set(strict_graph['ordinaryGroundRootComponents'])
 parents=strict_graph['groundRootedComponentParents'];assert all(v not in wanted for v in parents.values())
 seam=expected_role['slantedSeamComponent'];assert seam in wanted and components[seam]['actorUID']=='landsd/79097:0' and components[seam]['globalOriginalFaces']==[13402]
 assert set(expected_role['openBackComponents'])==set(wanted)-{seam}
 results=[]
 for k in wanted:
  c=components[k];uid=c['actorUID'];assert uid in expected_role['sources'];faces=c['globalOriginalFaces'];hosts=sorted(i for j in rooted if components[j]['actorUID']==uid for i in components[j]['globalOriginalFaces']);assert hosts
  if k==seam:
   body=expected_role['seamRootedBodyComponent'];assert body in rooted and components[body]['actorUID']==uid
   proof=slanted_triangle_seam_role(tri,faces,components[body]['globalOriginalFaces'],[contexts[i] for i in faces],ground,world)
  else:proof=open_back_role(tri,faces,hosts,[contexts[i] for i in faces],ground,world)
  results.append(dict(component=k,actorUID=uid,**proof))
 return dict(contract='ko-fung-complete-original-mounted-facade-role-v3',allOriginalFaces=len(tri),allOriginalComponents=len(components),independentlyStructuralComponents=sorted(rooted),accountedVisualComponents=wanted,completeOriginalVisualRoles=results,allComponentsAccounted=sorted(rooted|set(wanted))==list(range(len(components))),rawStrictReasonsPreserved=strict_graph['reasons'],visualGroundRootCredit=False,visualStructuralBridgeCredit=False,closedBuildingSolidCertified=False,sourceGeometryChanges=0,installationApproved=False,mandatoryIndependentFullCurrentGates=True,binding=current_binding)
