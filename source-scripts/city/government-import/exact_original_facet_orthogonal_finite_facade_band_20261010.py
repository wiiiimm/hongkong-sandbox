"""Exact whole original facet feet on a finite coplanar facade union.

Diagnosis only. Fixed .1m Euclidean distance, no expanded/welded geometry.
Each successful witness proves every orthogonal foot is on the complete closed
union of original coplanar host facets. Affine signed distance attains its
maximum absolute value at an original source vertex. No structural role credit.
"""
from fractions import Fraction as F
import hashlib
import numpy as np
from exact_original_projection_coverage_20261009 import signed_area, subtract

def cross(a,b):
 return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])

def verify(source_face,host_faces):
 source=np.asarray(source_face,float);hosts=np.asarray(host_faces,float)
 assert source.shape==(3,3) and hosts.ndim==3 and hosts.shape[1:]==(3,3) and len(hosts)
 assert np.isfinite(source).all() and np.isfinite(hosts).all()
 points=[tuple(F(float(x)) for x in p) for p in source]
 nsource=cross(tuple(points[1][j]-points[0][j] for j in range(3)),tuple(points[2][j]-points[0][j] for j in range(3)))
 assert any(nsource),'Zero-area source cannot supply a finite visual surface'
 low=np.nextafter(source.min(axis=0)-.1,-np.inf);high=np.nextafter(source.max(axis=0)+.1,np.inf)
 candidate=np.flatnonzero(np.all(hosts.max(axis=1)>=low,axis=1)&np.all(hosts.min(axis=1)<=high,axis=1))
 groups={};degenerate=[]
 for i in candidate:
  t=[tuple(F(float(x)) for x in p) for p in hosts[i]]
  n=cross(tuple(t[1][j]-t[0][j] for j in range(3)),tuple(t[2][j]-t[0][j] for j in range(3)));n2=sum(x*x for x in n)
  if not n2:degenerate.append(int(i));continue
  if n[1]*n[1]>n2/F(16):continue
  scale=next(x for x in n if x);normal=tuple(x/scale for x in n);d=-sum(normal[j]*t[0][j] for j in range(3))
  groups.setdefault((*normal,d),[]).append((int(i),t))
 witnesses=[]
 for plane,entries in sorted(groups.items()):
  n=plane[:3];n2=sum(x*x for x in n);e=[sum(n[j]*p[j] for j in range(3))+plane[3] for p in points]
  distances=[x*x/n2 for x in e]
  if any(x>F(.1)**2 for x in distances):continue
  feet=[tuple(p[j]-x*n[j]/n2 for j in range(3)) for p,x in zip(points,e)]
  drop=max(range(3),key=lambda j:abs(n[j]));dims=[j for j in range(3) if j!=drop]
  projected=[tuple(p[j] for j in dims) for p in feet];area=abs(signed_area(projected))
  if not area:continue # No height/area/support from collapsed projection.
  remaining=[projected]
  for _,t in entries:
   face=[tuple(p[j] for j in dims) for p in t]
   remaining=[piece for r in remaining for piece in subtract(r,face)]
   if not remaining:break
  gap=sum(abs(signed_area(piece)) for piece in remaining)
  if gap==0:
   witnesses.append(dict(exactOriginalHostPlane=[str(x) for x in plane],completeCoplanarCandidateHostFaceIndices=[i for i,_ in entries],exactOriginalVertexSquaredPerpendicularDistancesM2=[str(x) for x in distances],exactOrthogonalFeet=[[str(x) for x in p] for p in feet],exactOrthogonalFootTriangleProjectedArea=str(area),exactUncoveredProjectedArea='0'))
 return dict(contract='exact-whole-original-facet-orthogonal-finite-facade-band-diagnostic-v1',verifiedWholeOriginalFacetFiniteFacadeBand=bool(witnesses),strictEuclideanBandM=.1,completeOriginalHostFaces=len(hosts),broadphaseHostFaces=len(candidate),completeSourceFacetSHA256=hashlib.sha256(source.tobytes()).hexdigest(),completeHostSHA256=hashlib.sha256(hosts.tobytes()).hexdigest(),allPassingExactCoplanarUnionWitnesses=witnesses,exactZeroAreaCandidateHostFaces=degenerate,noToleranceOrBufferCredit=True,sourceGeometryChanges=0,visualRoleAccepted=False,structuralRootCredit=False,structuralBridgeCredit=False,installationApproved=False)
