"""Three named original Festival Walk facade sign glyphs; visual-only accounting.

This fixture covers I/L/dash source components 46/53/58, never the upper actor's
other details. Complete original open boundaries remain within the fixed .1m
finite rooted facade band. No ground roots, bridges or collision exemptions.
The source adapter must bind actual provider streams, complete fresh physical,
all foreign geometry and component graph replay before any final acceptance.
"""
import hashlib,json
import numpy as np
from original_local_finite_facade_boundary_diagnostic_20261010 import prepare_hosts,diagnose
from exact_original_face_conservative_clearance_v5_20261010 import verify as clearance
from exact_shell_context_accelerated_20261009 import shell_self_intersections
SOURCE='786e89452ba921ce3b16ba1b899919d4965f829ea5fb7b1756cd6ab5ed4c2ef8'
WORLD='d0878dc75f48e8766db5cf9e27318d3605ee69fad4ffdd5821e0ad0c9a090d0c'
FACES={46:[4202,4203,*range(5057,5065)],53:[*range(4296,4300),*range(5309,5321)],58:[4367,4368,*range(5483,5491)]}
def canonical(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def verify(triangles,rendered_world,ground,strict_graph,provider_role,*,expected_binding,current_binding):
 tri=np.asarray(triangles,float);world=np.asarray(rendered_world,float);ground=np.asarray(ground,float);assert tri.shape==world.shape==(18484,3,3) and np.isfinite(tri).all() and np.isfinite(world).all() and ground.ndim==3 and ground.shape[1:]==(3,3) and len(ground) and np.isfinite(ground).all() and np.max(np.abs(tri-world))<=1e-9
 assert hashlib.sha256(tri.tobytes()).hexdigest()==WORLD
 assert expected_binding==current_binding and current_binding
 for key,value in [('completeOriginalWorldSHA256',WORLD),('completeActualRenderedWorldSHA256',hashlib.sha256(world.tobytes()).hexdigest()),('completeCurrentGroundSHA256',hashlib.sha256(ground.tobytes()).hexdigest()),('completeStrictGraphSHA256',canonical(strict_graph)),('frozenProviderRoleSHA256',canonical(provider_role))]:assert current_binding[key]==value,'Frozen complete source input changed'
 assert provider_role['contract']=='festival-walk-original-I-L-dash-facade-sign-role-v1' and provider_role['sourceSHA256']==SOURCE and provider_role['completeOriginalWorldSHA256']==WORLD
 assert provider_role['allSignComponents']==[46,53,58] and {int(k):v for k,v in provider_role['completeOriginalSignFaces'].items()}==FACES
 assert strict_graph['actors']==[provider_role['completeOriginalActor']]
 assert strict_graph['binding']['completeOriginalWorldTrianglesSHA256']==WORLD
 parts=strict_graph['components'];assert len(parts)==92;partition=[i for c in parts for i in c['globalOriginalFaces']];assert sorted(partition)==list(range(len(tri))) and len(partition)==len(set(partition))
 roots=strict_graph['resolvedOriginalComponents'];assert roots==sorted(set(roots)) and sorted(set(range(92))-set(roots))==[46,53,58] and strict_graph['ordinaryGroundRootComponents'] and not strict_graph['supportInterfaceAccepted']
 assert all(v not in FACES for v in strict_graph['groundRootedComponentParents'].values()),'Visual detail cannot be structural parent'
 for k,faces in FACES.items():assert parts[k]['actorUID']=='landsd/91827:0' and parts[k]['globalOriginalFaces']==faces
 hostids=sorted(i for k in roots for i in parts[k]['globalOriginalFaces']);prepared=prepare_hosts(tri,hostids);roles=[]
 for k,ids in FACES.items():
  p=diagnose(prepared,ids);assert p['sourceOnlyBoundaryBandPassed'] and len(p['completeOriginalLoops'])==1,'Complete authored opening fails existing finite facade band'
  selfcheck=shell_self_intersections(tri[ids]);assert selfcheck['selfIntersectionFree'],'Original sign is self intersecting'
  proof=[]
  for i in ids:
   a=clearance(tri[i],ground);b=a if np.array_equal(tri[i],world[i]) else clearance(world[i],ground);assert a['existingOrdinaryClearanceBoundProved'] and b['existingOrdinaryClearanceBoundProved'],'Ordinary complete original/rendered clearance remains strict';proof.append(dict(sourceFace=i,original=a,rendered=b))
  roles.append(dict(component=k,role='original-non-load-bearing-facade-sign-glyph',completeOriginalFaces=ids,completeFiniteOriginalMountBoundary=p,originalSelfIntersection=selfcheck,completeOrdinaryClearance=proof,syntheticBackCapCreated=False,structuralRootCredit=False,structuralBridgeCredit=False))
 return dict(contract=provider_role['contract'],sourceSHA256=SOURCE,completeOriginalFaces=len(tri),completeOriginalComponents=92,visualSignComponents=[46,53,58],independentlyStructuralComponents=roots,roles=roles,allPodiumComponentsAccounted=True,rawStrictReasonsPreserved=strict_graph['reasons'],upperActorOtherDetailsAccepted=False,visualGroundRootCredit=False,visualStructuralBridgeCredit=False,sourceGeometryChanges=0,installationApproved=False,mandatoryIndependentFullCurrentGates=True,binding=current_binding)
