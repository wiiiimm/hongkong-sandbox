"""Exact whole-facet orthogonal distance to a finite noncoplanar facade union.

Diagnostic only, fixed existing .1m band. Each closed source-parameter piece is
clipped by a host triangle's exact finite orthogonal-foot half planes. Its
squared plane distance is bounded at every vertex; convexity bounds the whole
piece. Only proved pieces enter the exact union. No geometry/role/root credit.
"""
from fractions import Fraction as F
import hashlib
import numpy as np
from exact_original_projection_coverage_20261009 import clean,signed_area,subtract
from exact_original_facet_orthogonal_finite_facade_band_20261010 import cross

def dot(a,b):return sum(x*y for x,y in zip(a,b))
def difference(a,b):return tuple(x-y for x,y in zip(a,b))
def affine_clip(poly,values):
 if not poly:return []
 def at(p):return values[0]+p[0]*(values[1]-values[0])+p[1]*(values[2]-values[0])
 out=[]
 for p,q in zip(poly,poly[1:]+poly[:1]):
  vp,vq=at(p),at(q);ip,iq=vp>=0,vq>=0
  if ip:out.append(p)
  if ip!=iq:
   t=vp/(vp-vq);out.append(tuple(p[k]+t*(q[k]-p[k])for k in range(2)))
 return clean(out)

def verify(source_face,host_faces):
 source=np.asarray(source_face,float);hosts=np.asarray(host_faces,float)
 assert source.shape==(3,3)and hosts.ndim==3 and hosts.shape[1:]==(3,3)and len(hosts)
 assert np.isfinite(source).all()and np.isfinite(hosts).all()
 points=[tuple(F(float(v))for v in p)for p in source]
 assert any(cross(difference(points[1],points[0]),difference(points[2],points[0]))),'Zero-area source has no visual surface'
 parameter=[(F(0),F(0)),(F(1),F(0)),(F(0),F(1))]
 low=np.nextafter(source.min(axis=0)-.1,-np.inf);high=np.nextafter(source.max(axis=0)+.1,np.inf)
 candidate=np.flatnonzero(np.all(hosts.max(axis=1)>=low,axis=1)&np.all(hosts.min(axis=1)<=high,axis=1))
 witnesses=[];degenerate=[];outside_band=[];nonfacade=[];remaining=[parameter]
 for j in candidate:
  t=[tuple(F(float(v))for v in p)for p in hosts[j]];n=cross(difference(t[1],t[0]),difference(t[2],t[0]));n2=dot(n,n)
  if not n2:degenerate.append(int(j));continue
  if n[1]*n[1]>n2/F(16):nonfacade.append(int(j));continue
  errors=[dot(n,difference(p,t[0]))for p in points]
  feet=[tuple(p[k]-e*n[k]/n2 for k in range(3))for p,e in zip(points,errors)]
  piece=parameter
  for a,b in zip(t,t[1:]+t[:1]):
   values=[dot(n,cross(difference(b,a),difference(p,a)))for p in feet]
   piece=affine_clip(piece,values)
   if not piece:break
  if not piece or not signed_area(piece):continue
  squared=[]
  for u,v in piece:
   e=errors[0]+u*(errors[1]-errors[0])+v*(errors[2]-errors[0]);squared.append(e*e/n2)
  if any(x>F(.1)**2 for x in squared):outside_band.append(int(j));continue
  witnesses.append(dict(originalHostFace=int(j),exactClosedSourceParameterPiece=[[str(x)for x in p]for p in piece],exactSquaredPerpendicularDistancesAtEveryPieceVertexM2=[str(x)for x in squared],exactHostPlaneNormal=[str(x)for x in n]))
  # Convex clipped pieces are represented by a finite triangle fan only for
  # exact union accounting. Neither input mesh nor its topology is changed.
  for i in range(1,len(piece)-1):
   fan=[piece[0],piece[i],piece[i+1]]
   if signed_area(fan):remaining=[part for r in remaining for part in subtract(r,fan)]
 uncovered=sum(abs(signed_area(p))for p in remaining)
 return dict(contract='exact-whole-original-facet-piecewise-finite-facade-band-diagnostic-v1',verifiedWholeOriginalFacetFiniteFacadeBand=uncovered==0,strictEuclideanBandM=.1,completeSourceFacetSHA256=hashlib.sha256(source.tobytes()).hexdigest(),completeHostSHA256=hashlib.sha256(hosts.tobytes()).hexdigest(),completeOriginalHostFaces=len(hosts),broadphaseHostFaces=len(candidate),allExactCertifiedFiniteFacadePieces=witnesses,exactUncoveredSourceParameterArea=str(uncovered),exactZeroAreaCandidateHostFaces=degenerate,nonFacadeCandidateHostFaces=nonfacade,finiteFootPiecesOutsideExistingBand=outside_band,noToleranceOrBufferCredit=True,sourceGeometryChanges=0,visualRoleAccepted=False,structuralRootCredit=False,structuralBridgeCredit=False,installationApproved=False)
