"""Exact 3D source-face clipping for PRIVATE terrain partitions, never building meshes."""
from fractions import Fraction as F
import numpy as np

def intersection(a,b):
 r=[max(a[0],b[0]),max(a[1],b[1]),min(a[2],b[2]),min(a[3],b[3])]
 return r if r[0]<r[2]and r[1]<r[3]else None

def subtract(a,b):
 b=intersection(a,b)
 if b is None:return[a]
 x,z,X,Z=a;l,bottom,r,top=b
 return[q for q in [[x,z,l,Z],[r,z,X,Z],[l,z,r,bottom],[l,top,r,Z]]if q[0]<q[2]and q[1]<q[3]]

def clip(face,bounds):
 planes=[(0,F(bounds[0]),1),(0,F(bounds[2]),-1),(2,F(bounds[1]),1),(2,F(bounds[3]),-1)]
 poly=[tuple(F(float(v))for v in p)for p in face]
 if all(all(s*(p[a]-b)>=0 for a,b,s in planes)for p in poly):return[face.tolist()],False
 for a,b,s in planes:
  out=[]
  for p,q in zip(poly,poly[1:]+poly[:1]):
   ip,iq=s*(p[a]-b)>=0,s*(q[a]-b)>=0
   if ip:out.append(p)
   if ip!=iq:
    t=(b-p[a])/(q[a]-p[a]);out.append(tuple(p[j]+t*(q[j]-p[j])for j in range(3)))
  poly=[]
  for p in out:
   if not poly or p!=poly[-1]:poly.append(p)
  if len(poly)>1 and poly[0]==poly[-1]:poly.pop()
  if len(poly)<3:return[],True
 return[[[float(v)for v in p]for p in [poly[0],poly[i],poly[i+1]]]for i in range(1,len(poly)-1)],True

def cut(tri,bounds):
 lo,hi=tri.min(1),tri.max(1);ids=np.flatnonzero((hi[:,0]>=bounds[0])&(lo[:,0]<=bounds[2])&(hi[:,2]>=bounds[1])&(lo[:,2]<=bounds[3]));out=[];lineage=[]
 for i in ids:
  faces,split=clip(tri[i],bounds)
  for face in faces:out.append(face);lineage.append(dict(sourceFace=int(i),clipped=split))
 return out,lineage

def drawn(node):
 m=node['nativeMesh'];v=np.asarray(m['position'],dtype='<f4').astype('<f8').reshape(-1,3);tri=v[np.asarray(m['index']).reshape(-1,3)].copy()
 for f in tri:
  a,b,c=f;y=(b[2]-a[2])*(c[0]-a[0])-(b[0]-a[0])*(c[2]-a[2])
  if y<0:f[[1,2]]=f[[2,1]]
 return tri

def pack(faces):
 positions=[];indices=[];lookup={}
 for face in faces:
  for point in face:
   p=tuple(float(v)for v in np.asarray(point,dtype='<f4'))
   if p not in lookup:lookup[p]=len(positions)//3;positions.extend(p)
   indices.append(lookup[p])
 return positions,indices
