"""Named original standing skins: genuine grade, clear complete upper perimeter.

No cap is invented, no contact tolerance increased, and no volume/load claim.
Whole source/current identity and the four complete worlds are caller bindings.
Raw ordinary whole-rim failures remain independent recorded facts.
"""
from collections import Counter,defaultdict
from fractions import Fraction as F
import hashlib
import numpy as np
from exact_original_shared_edge_component_census_v2_20261011 import census
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
from exact_original_face_conservative_clearance_v5_20261010 import verify as finite
IDS={62:[5035,5036]+list(range(7100,7110)),98:list(range(7599,7643)),99:list(range(7643,7687)),100:list(range(7687,7731))}
def sha(a):return hashlib.sha256(np.asarray(a,dtype='<f8').tobytes()).hexdigest()
def point(p):return tuple(F(float(v))for v in p)
def cross(a,b):return(a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def closed_ring(edges):
 assert edges and len(edges)==len(set(edges));adj=defaultdict(set)
 for a,b in edges:assert a!=b;adj[a].add(b);adj[b].add(a)
 assert len(adj)==len(edges)and all(len(v)==2 for v in adj.values())
 start=min(adj);order=[start];previous=None;current=start
 while True:
  following=min(v for v in adj[current]if v!=previous)
  if following==start:break
  assert following not in order;order.append(following);previous,current=current,following
 assert len(order)==len(edges)
 def orient(a,b,c):return(b[0]-a[0])*(c[2]-a[2])-(b[2]-a[2])*(c[0]-a[0])
 assert sum(a[0]*b[2]-b[0]*a[2]for a,b in zip(order,order[1:]+order[:1]))!=0
 for i,(a,b)in enumerate(zip(order,order[1:]+order[:1])):
  for j,(c,d)in enumerate(zip(order,order[1:]+order[:1])):
   if j<=i or j in {(i-1)%len(order),(i+1)%len(order)}:continue
   assert orient(a,b,c)*orient(a,b,d)>0 or orient(c,d,a)*orient(c,d,b)>0
 return order
def verify(part,ground,*,component,source_face_ids,expected_binding,current_binding):
 assert component in IDS and source_face_ids==IDS[component]and expected_binding==current_binding
 t=np.asarray(part,dtype='<f8');g=np.asarray(ground,dtype='<f8');assert t.shape==(len(source_face_ids),3,3)and g.ndim==3 and g.shape[1:]==(3,3)and len(g)and np.isfinite(t).all()and np.isfinite(g).all()
 assert expected_binding==dict(completePartSHA256=sha(t),completeGroundSHA256=sha(g))
 inv=census(t,list(range(len(t))));assert inv['sharedEdgeConnectedComponents']==[list(range(len(t)))]and not inv['exactNonrenderingOriginalFaces']and inv['boundaryEdges']==inv['nonmanifoldEdges']==inv['twoFaceOrientationConflicts']==0
 faces=[[point(v)for v in f]for f in t];upper=max(v[1]for f in faces for v in f)
 caps=[i for i,f in enumerate(faces)if all(v[1]==upper for v in f)]
 bases=[i for i,f in enumerate(faces)if all(v[1]<upper for v in f)]
 walls=sorted(set(range(len(t)))-set(caps)-set(bases));assert caps and bases and walls and set(caps+bases+walls)==set(range(len(t)))
 edges=Counter()
 for i in walls:
  f=faces[i];n=cross(tuple(f[1][k]-f[0][k]for k in range(3)),tuple(f[2][k]-f[0][k]for k in range(3)))
  assert any(n)and 16*n[1]*n[1]<=sum(v*v for v in n)
  edges.update(tuple(sorted((a,b)))for a,b in zip(f,f[1:]+f[:1]))
 assert set(edges.values())<={1,2}
 boundary=[e for e,n in edges.items()if n==1];top=[e for e in boundary if all(v[1]==upper for v in e)];bottom=[e for e in boundary if all(v[1]<upper for v in e)]
 assert set(top+bottom)==set(boundary);topring=closed_ring(top);bottomring=closed_ring(bottom)
 ordinary=[finite(f,g)for f in t];assert all(p['existingOrdinaryClearanceBoundProved']for p in ordinary)
 cap_proofs=[dict(originalSourceFace=source_face_ids[i],completeFiniteClearance=ordinary[i])for i in caps]
 assert all(F(p['completeFiniteClearance']['exactCertifiedLowerClearanceM'])>0 for p in cap_proofs)
 reverseg=g.copy();reverseg[:,:,1]*=-1;bottom_proofs=[]
 for i in bases:
  reverse=t[i].copy();reverse[:,1]*=-1;p=finite(reverse,reverseg);assert p['groundProjectionCovered']and F(p['exactCertifiedLowerClearanceM'])>0
  bottom_proofs.append(dict(originalSourceFace=source_face_ids[i],heightSignReversedBelowGradeProof=p,qualification='Exact finite height-sign reversal proves original base below actual ground, without changing either geometry.'))
 upper_proofs=[]
 for a,b in top:
  p=finite(np.asarray([[float(v)for v in x]for x in [a,b,b]],dtype='<f8'),g);assert p['groundProjectionCovered']and F(p['exactCertifiedLowerClearanceM'])>0
  upper_proofs.append(dict(completeOriginalUpperEdge=[list(map(str,a)),list(map(str,b))],completeFiniteClearance=p))
 grade=exact_finite_contacts(t,range(len(t)),g,range(len(g)),maximum_pairs=len(t)*len(g));assert grade['allPairsExamined']and grade['sourceFacesOmitted']==0
 contacts=grade['contacts'];assert contacts and {c['sourceFaceA']for c in contacts}==set(walls)
 assert all(c['dimension']==1 and c['sourcePrimitiveDimensionA']==c['sourcePrimitiveDimensionB']==2 and len(c['exactPoints'])==2 for c in contacts)
 return dict(contract='Evangel-named-original-standing-grade-skin-v1',originalComponent=component,completeOriginalFaceIds=source_face_ids,binding=current_binding,
  completeOriginalTopology=inv,completeOriginalUpperCapFaceIds=[source_face_ids[i]for i in caps],completeOriginalBaseFaceIds=[source_face_ids[i]for i in bases],completeOriginalLateralFaceIds=[source_face_ids[i]for i in walls],
  completeOriginalUpperRing=[[str(v)for v in p]for p in topring],completeOriginalLowerRing=[[str(v)for v in p]for p in bottomring],completeUpperPerimeterProofs=upper_proofs,
  completeStrictClearOriginalCapProofs=cap_proofs,completeEmbeddedOriginalBaseProofs=bottom_proofs,completeOrdinaryAllFacetProofs=ordinary,genuineCompleteFiniteGradeContacts=grade,
  everyLateralFacetGenuinelyCrossesGrade=True,wholeOriginalUpperPerimeterStrictlyClear=True,allOriginalCapsAndBaseSurfacesRetained=True,
  rawWholeFootingFailureRemains=True,sourceGeometryChanges=0,terrainGeometryChanges=0,closedSolidCertified=False,loadBearingClaim=False,supportTransferToOtherSourceBodies=False,currentAcceptance=False,installationApproved=False)
