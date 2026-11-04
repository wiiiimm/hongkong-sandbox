"""Exact analysis-only triangle partition at a recorded height; no runtime asset edits."""
from fractions import Fraction

def sub(a,b):return tuple(x-y for x,y in zip(a,b))
def cross(a,b):return(a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def area_vector(faces):
 total=[Fraction(0)]*3
 for a,b,c in faces:
  n=cross(sub(b,a),sub(c,a))
  total=[x+y for x,y in zip(total,n)]
 return tuple(total)
def clip(poly,height,above):
 out=[]
 for start,end in zip(poly,poly[1:]+poly[:1]):
  first=start[1]>=height if above else start[1]<=height
  second=end[1]>=height if above else end[1]<=height
  if first:out.append(start)
  if first!=second:
   t=(height-start[1])/(end[1]-start[1]);point=tuple(a+t*(b-a)for a,b in zip(start,end));assert point[1]==height;out.append(point)
 clean=[]
 for p in out:
  if not clean or clean[-1]!=p:clean.append(p)
 if len(clean)>1 and clean[-1]==clean[0]:clean.pop()
 faces=[]
 for i in range(1,len(clean)-1):
  face=(clean[0],clean[i],clean[i+1])
  if any(area_vector([face])):faces.append(face)
 return faces

def partition_triangle(face,base):
 """Return exact rational original-facet portions, never adding a grade-plane cap."""
 f=tuple(tuple(Fraction.from_float(float(v))for v in p)for p in face);height=Fraction.from_float(float(base));normal=area_vector([f])
 if not any(normal):
  above=[f]if max(p[1]for p in f)>=height else[];below=[]if above else[f]
 elif min(p[1]for p in f)>=height:above,below=[f],[]
 elif max(p[1]for p in f)<=height:above,below=[],[f]
 else:above,below=clip(f,height,True),clip(f,height,False)
 assert area_vector(above+below)==normal
 assert all(p[1]>=height for t in above for p in t)or not any(normal)
 assert all(p[1]<=height for t in below for p in t)or not any(normal)
 return above,below
