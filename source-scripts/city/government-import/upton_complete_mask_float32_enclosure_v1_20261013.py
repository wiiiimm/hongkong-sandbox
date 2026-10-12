"""UNEXECUTED arithmetic enclosure and exact packed primitive coverage.
No support/ordinary tolerance, source geometry, or acceptance alteration.
"""
from fractions import Fraction as F
import math
import numpy as np
from exact_original_projection_coverage_20261009 import exact_coverage
from upton_six_basic_preserved_ground_feasibility_v1_20261012 import area,projected_mask

def scalar(v):
 if isinstance(v,F):return v
 if isinstance(v,str):return F(v)
 assert math.isfinite(float(v));return F(float(v))
def power(n):return F(2**n)if n>=0 else F(1,2**(-n))
def exponent(q):
 assert q>0;n=q.numerator.bit_length()-q.denominator.bit_length()
 if q<power(n):n-=1
 assert power(n)<=q<power(n+1);return n

def axis_error(maximum):
 m=abs(scalar(maximum));e64=power(max(exponent(m)-52,-1074))/2 if m else power(-1074)/2
 rounded_max=m+e64;assert rounded_max<(F(2)-power(-23))*power(127),'Unsupported Float32 overflow range'
 e32=power(max(exponent(rounded_max)-23,-149))/2
 return dict(binary64HalfSpacing=e64,float32HalfSpacing=e32,completeCastError=e64+e32,maximumExactMagnitude=m)
def domain_errors(domain):
 assert len(domain)==4;d=list(map(scalar,domain));assert d[0]<d[2]and d[1]<d[3]
 return dict(x=axis_error(max(abs(d[0]),abs(d[2]))),z=axis_error(max(abs(d[1]),abs(d[3]))),packingPath='rational -> binary64 -> Float32 -> binary64 readback',notToleranceExpansion=True)
def orient(a,b,c):return(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
def hull(points):
 p=sorted(set(tuple(map(scalar,q))for q in points));assert p and all(len(q)==2 for q in p)
 if len(p)==1:return p
 def half(seq):
  out=[]
  for q in seq:
   while len(out)>1 and orient(out[-2],out[-1],q)<=0:out.pop()
   out.append(q)
  return out
 return half(p)[:-1]+half(reversed(p))[:-1]
def envelope(primitive,errors,domain):
 d=list(map(scalar,domain));p=[tuple(map(scalar,q))for q in primitive];assert p and all(len(q)==2 for q in p)
 assert all(d[0]<=q[0]<=d[2]and d[1]<=q[1]<=d[3]for q in p),'Protected primitive exceeds captured domain'
 ex=errors['x']['completeCastError'];ez=errors['z']['completeCastError'];assert ex>0 and ez>0
 polygon=hull([(x+dx,z+dz)for x,z in p for dx in [-ex,ex]for dz in [-ez,ez]])
 triangles=[[polygon[0],polygon[i],polygon[i+1]]for i in range(1,len(polygon)-1)]
 assert all(area(t)>0 for t in triangles)
 return dict(originalPrimitive=p,exactEnvelopePolygon=polygon,exactEnvelopeTriangles=triangles,collapsedOriginalPrimitiveUncredited=area(hull(p))==0,noCoverageClaimFromErrorBound=True)
def packed_primitive_coverage(primitive,ground):
 p=[tuple(map(scalar,q))for q in primitive];assert len(p)==3
 # All actual protected primitives came from saved binary64 raw/form or F32
 # arrays. Refuse unrepresentable rational substitutions in this float-input API.
 assert all(F(float(v))==v for q in p for v in q),'Coverage input must be saved binary-float coordinates'
 a=np.asarray(ground,dtype='<f8');assert a.ndim==3 and a.shape[1:]==(3,3)and np.isfinite(a).all()
 assert np.array_equal(a,a.astype(np.float32).astype('<f8')),'Retained coverage must use actual Float32 storage'
 eligible=[];excluded=[]
 for i,t in enumerate(a):
  A,B,C=[[float(v)for v in q]for q in t];det=(B[2]-C[2])*(A[0]-C[0])+(C[0]-B[0])*(A[2]-C[2])
  (eligible if abs(det)>=1e-10 else excluded).append(i)
 faces=a[eligible].reshape(-1,3,3)
 source=np.asarray([[float(x),0.,float(z)]for x,z in p],dtype='<f8')
 whole=exact_coverage(source,faces)
 boundaries=[exact_coverage(np.asarray([source[i],source[(i+1)%3],source[(i+1)%3]]),faces)for i in range(3)]
 return dict(completeProtectedPrimitiveCovered=whole['exactProjectionCovered']and all(q['exactProjectionCovered']for q in boundaries),whole=whole,allThreeCompleteBoundaryEdges=boundaries,productionHeightEligibleRetainedFaceIDs=eligible,productionDeterminantExcludedRetainedFaceIDs=excluded,productionJSNumberDeterminantLimit=1e-10,excludedFacetsStillDrawnUncredited=True,noSampleHeightRootSupportOrAcceptanceCredit=True)
def native_whole_selection(selection,attribution,parent_path):
 native=[];base=[]
 for q in selection['selected']:
  at=attribution[q['currentFace']];assert at['globalCurrentFace']==q['currentFace']and at['uniqueSourceIdentity'],'Ambiguous whole-current source identity'
  p=at['assignedMultisetOccurrence']['sourcePath'];assert p in [parent_path,'3d-viewer/city/data/terrain.json'],'Unexpected current layer'
  (native if p==parent_path else base).append(q)
 return native,base
