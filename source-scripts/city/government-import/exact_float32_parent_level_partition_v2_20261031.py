"""Exact Float32 coplanar terrain subdivision; no displacement or model edits.

Reject intersections not representable in Float32. This prepares a terrain
basis only and grants no source, terrain-edit or publication approval.
"""
from fractions import Fraction as F
import hashlib
import numpy as np

def sub(a,b):return tuple(x-y for x,y in zip(a,b))
def cross(a,b):return(a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def rational(t):return[tuple(F(float(v))for v in p)for p in t]
def clip(poly,h,below):
 out=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  ia=a[1]<=h if below else a[1]>=h;ib=b[1]<=h if below else b[1]>=h
  if ia:out.append(a)
  if ia!=ib:
   q=(h-a[1])/(b[1]-a[1]);out.append(tuple(x+q*(y-x)for x,y in zip(a,b)))
 clean=[]
 for p in out:
  if not clean or p!=clean[-1]:clean.append(p)
 if len(clean)>1 and clean[0]==clean[-1]:clean.pop()
 return clean

def partition(faces,level):
 raw=np.asarray(faces,dtype='<f8');values=raw.astype('<f4').astype('<f8')
 assert raw.ndim==3 and raw.shape[1:]==(3,3)and len(raw)and np.isfinite(raw).all()
 assert np.array_equal(raw,values),'Parent is not the actual represented Float32 surface'
 h=F(level);assert F(6,5)<=h<=2
 output=[];lineage=[];changed=0
 for i,face in enumerate(values):
  tri=rational(face);n=cross(sub(tri[1],tri[0]),sub(tri[2],tri[0]));assert n[1]!=0;parts=[]
  if min(p[1]for p in tri)<h<max(p[1]for p in tri):
   changed+=1
   for below in [True,False]:
    poly=clip(tri,h,below)
    for j in range(1,len(poly)-1):
     t=[poly[0],poly[j],poly[j+1]]
     if cross(sub(t[1],t[0]),sub(t[2],t[0]))[1]:parts.append(t)
  else:parts=[tri]
  area=F(0)
  for t in parts:
   encoded=np.asarray([[float(v)for v in p]for p in t],dtype='<f4').astype('<f8')
   assert rational(encoded)==t,'Clipping would introduce a nonrepresentable coordinate'
   nn=cross(sub(t[1],t[0]),sub(t[2],t[0]));assert nn[1]*n[1]>0 and all(dot(n,sub(p,tri[0]))==0 for p in t)
   assert all(p[1]<=h for p in t)or all(p[1]>=h for p in t)
   area+=abs(nn[1]);output.append(encoded);lineage.append(i)
  assert area==abs(n[1]),'Exact projected area changed'
 result=np.asarray(output,dtype='<f8')
 if changed==0:
  assert np.array_equal(result,values) and lineage==list(range(len(values))), 'No-op partition must preserve every represented face exactly'
 return result,dict(contract='exact-float32-coplanar-current-parent-level-partition-v2',levelM=float(h),exactLevel=str(h),sourceFaces=len(values),outputFaces=len(result),subdividedParentFaces=changed,sourceFaceByOutputFace=lineage,inputSHA256=hashlib.sha256(values.astype('<f4').tobytes()).hexdigest(),outputSHA256=hashlib.sha256(result.astype('<f4').tobytes()).hexdigest(),everyOutputCoordinateExactlyFloat32=True,exactOriginalPlaneAndWinding=True,exactProjectedAreaConservation=True,parentSurfaceExactlyUnchanged=True,parentTriangulationChanged=bool(changed),governmentBuildingGeometryChanges=0,installationApproved=False)

def choose(faces):
 failures=[]
 for numerator in range(77,129):
  try:
   out,proof=partition(faces,F(numerator,64));proof['rejectedLevels']=failures;return out,proof
  except AssertionError as error:failures.append(dict(level=str(F(numerator,64)),reason=str(error)))
 raise AssertionError('No exact Float32 parent partition in1.2..2m: '+repr(failures))
