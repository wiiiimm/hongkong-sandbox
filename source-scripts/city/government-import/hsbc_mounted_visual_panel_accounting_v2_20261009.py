"""Named original HSBC hanging-panel visual accounting, never support/root credit.

The source adapter must independently pin the actual government acquisition and
full current physical/runtime/foreign proofs. Exact point contacts are actual
scene attachment witnesses, not positive-dimensional load-bearing interfaces.
"""
import hashlib,json
from fractions import Fraction
import numpy as np
from original_shell_diagnostic_20261009 import shell_context
from exact_shell_context_accelerated_20261009 import shell_self_intersections
from exact_original_shell_intersections_20261009 import rational_face,intersection_points

UID='landsd/265848:0'
SOURCE='848eb61d88b19162d2166127f3c04c4f920f986c55106ffbb121b110ef0973cd'
def canonical_sha(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def verify(triangles,contexts,strict_graph,*,expected_role,expected_binding,current_binding):
 tri=np.asarray(triangles,float);assert tri.ndim==3 and tri.shape[1:]==(3,3) and len(tri) and np.isfinite(tri).all()
 assert expected_binding==current_binding and current_binding
 assert current_binding['completeOriginalWorldTrianglesSHA256']==hashlib.sha256(tri.tobytes()).hexdigest()
 assert current_binding['strictGraphSHA256']==canonical_sha(strict_graph)
 assert current_binding['continuousContextsSHA256']==canonical_sha(contexts)
 assert current_binding['frozenRoleSHA256']==canonical_sha(expected_role)
 assert expected_role['uid']==UID and expected_role['sourceSHA256']==SOURCE
 for key in ['providerRootStreamsSHA256','fullCurrentPhysicalSHA256','fullCurrentForeignScopeSHA256']:assert current_binding[key]
 component=expected_role['component'];components=strict_graph['components'];assert 0<=component<len(components)
 faces=expected_role['originalFaces'];assert len(faces)==5 and len(set(faces))==5 and all(isinstance(f,int) and 0<=f<len(tri) for f in faces)
 assert components[component]['globalOriginalFaces']==faces and components[component]['actorUID']==UID
 rooted=set(strict_graph['resolvedOriginalComponents']);assert rooted==set(range(len(components)))-{component},'Every other original component must independently root without visual panel'
 assert not strict_graph['supportInterfaceAccepted'] and strict_graph['reasons']==['unresolved-original-component:'+str(component)]
 assert component not in strict_graph['ordinaryGroundRootComponents']
 for contact in strict_graph['contactWitnesses']:assert component not in contact['components'],'Panel must not supply an original load-bearing edge'
 for value in strict_graph['groundRootedComponentParents'].values():assert value!=component,'Panel cannot support another component'
 topology=shell_context(tri,faces);assert topology['componentFaces']==faces and not topology['inconsistentOrientedEdges'] and not topology['degenerateFaces']
 selfcheck=shell_self_intersections(tri[faces]);assert selfcheck['selfIntersectionFree']
 normals=np.cross(tri[faces,1]-tri[faces,0],tri[faces,2]-tri[faces,0]);ratios=np.abs(normals[:,1])/np.linalg.norm(normals,axis=1);assert np.all(ratios<=.25),'Original role must be vertical exterior panel'
 assert len(contexts)==5 and {c['sourceFace'] for c in contexts}==set(faces)
 for c in contexts:assert c['groundProjectionCovered'] and c['minimum'] and c['minimum']['minimumGapM']>=-.5,'Every complete panel facet retains ordinary clearance'
 body_component=expected_role['rootedBodyComponent'];assert body_component in rooted and components[body_component]['actorUID']==UID
 body_faces=components[body_component]['globalOriginalFaces'];assert expected_role['rootedBodyContactFaces'] and set(expected_role['rootedBodyContactFaces'])<=set(body_faces)
 # This locator accounts only for the existing packed/runtime floating arithmetic;
 # every actual attachment still requires exact finite triangle intersection.
 roundoff=Fraction.from_float(float(expected_role['independentlyVerifiedPackedWorldRoundoffM']));assert 0<=roundoff<=Fraction.from_float(1e-9)
 vertices=tri[faces].reshape(-1,3);top=Fraction.from_float(float(vertices[:,1].max()))
 top_vertices={tuple(map(float,v)) for v in vertices if top-Fraction.from_float(float(v[1]))<=roundoff}
 assert len(top_vertices)>=2
 # Lower slanted end vertices can extend past the authored top border.
 # Locate the two ends of its actual source boundary, not whole-panel bounds.
 counts={}
 for face in tri[faces]:
  vs=[tuple(map(float,v)) for v in face]
  for a,b in zip(vs,vs[1:]+vs[:1]):
   edge=tuple(sorted((a,b)));counts[edge]=counts.get(edge,0)+1
 border=[e for e,n in counts.items() if n==1 and set(e)<=top_vertices]
 adjacency={v:set() for e in border for v in e}
 for a,b in border:adjacency[a].add(b);adjacency[b].add(a)
 endpoints=[v for v,n in adjacency.items() if len(n)==1];assert len(endpoints)==2 and all(len(n)<=2 for n in adjacency.values()),'Actual complete top border must be one simple open path'
 reached={endpoints[0]};todo=list(reached)
 while todo:
  for v in adjacency[todo.pop()]-reached:reached.add(v);todo.append(v)
 assert reached==set(adjacency)==top_vertices,'Disconnected or omitted original top boundary'
 assert endpoints[0][2]!=endpoints[1][2]
 corners=[tuple(Fraction.from_float(float(x)) for x in v) for v in sorted(endpoints,key=lambda v:v[2])]
 anchors=[]
 for i in faces:
  for j in expected_role['rootedBodyContactFaces']:
   points=intersection_points(rational_face(tri[i]),rational_face(tri[j]))
   assert len(points)<=1,'Positive-dimensional contacts belong to strict support graph, not point-only visual role'
   for point in points:
    for k,corner in enumerate(corners):
     if point[0]==corner[0] and point[2]==corner[2] and abs(point[1]-corner[1])<=roundoff:
      anchors.append({'corner':k,'originalFaces':[i,j],'exactPoint':list(map(str,point)),'cornerLocatorExactHeightRoundoffM':str(abs(point[1]-corner[1]))})
 assert {a['corner'] for a in anchors}=={0,1},'Two distinct actual original top-corner attachments required'
 distinct={tuple(a['exactPoint']) for a in anchors};assert len(distinct)>=2
 return {'contract':'hsbc-original-mounted-visual-panel-accounting-v2','uid':UID,'sourceSHA256':SOURCE,'accountedVisualComponent':component,'allOriginalVisualFaces':faces,'allOtherComponentsIndependentlyRooted':True,'exactTopCornerAttachments':anchors,'originalTopology':topology,'originalSelfIntersection':selfcheck,'preservedStrictFailure':strict_graph['reasons'],'visualPanelAccounted':True,'addedGroundRoots':[],'addedLoadBearingEdges':[],'panelCanSupportOtherComponents':False,'sourceGeometryChanges':0,'installationApproved':False,'mandatoryIndependentPhysicalChecks':True,'currentBindings':current_binding}
