"""Unexecuted saved-probe context; no guard replay or restoration certificate."""
from fractions import Fraction as F
import math
import struct,base64
from collections import defaultdict
def xz_cross(a,b,p):return (b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0])
def on_segment(a,b,p):return xz_cross(a,b,p)==0 and min(a[0],b[0])<=p[0]<=max(a[0],b[0])and min(a[1],b[1])<=p[1]<=max(a[1],b[1])
def complete_closed_projection_member(xz,triangle):
 p=[(F(v[0]),F(v[2]))for v in triangle];area=xz_cross(p[0],p[1],p[2])
 if area:return all(xz_cross(a,b,xz)*area>=0 for a,b in zip(p,p[1:]+p[:1]))
 points=sorted(set(p));return xz==points[0]if len(points)==1 else on_segment(points[0],points[-1],xz)
def exact_plane_height(xz,t):
 a,b,c=[tuple(F(v)for v in p)for p in t];den=(b[0]-a[0])*(c[2]-a[2])-(c[0]-a[0])*(b[2]-a[2])
 if den==0:return None
 u=((xz[0]-a[0])*(c[2]-a[2])-(c[0]-a[0])*(xz[1]-a[2]))/den;v=((b[0]-a[0])*(xz[1]-a[2])-(xz[0]-a[0])*(b[2]-a[2]))/den;return a[1]+u*(b[1]-a[1])+v*(c[1]-a[1])
def bins_for_triangles(triangles):
 bins=defaultdict(set)
 for i,t in enumerate(triangles):
  xs=[F(p[0])for p in t];zs=[F(p[2])for p in t]
  for x in range(int(min(xs)//20),int(max(xs)//20)+1):
   for z in range(int(min(zs)//20),int(max(zs)//20)+1):bins[x,z].add(i)
 return bins
def nominated_closed_faces(point,triangles,bins):return [i for i in sorted(bins.get((int(point[0]//20),int(point[1]//20)),set()))if complete_closed_projection_member(point,triangles[i])]
def decode_complete_basic(row):
 n=row['completePositionVertices'];assert n>0 and row['wholeUnusedPositionVerticesIncluded']is True
 raw=base64.b64decode(row['completeIndexBytesBase64'],validate=True);assert len(raw)==row['completeIndexedFaces']*3*4;indices=struct.unpack('<'+str(len(raw)//4)+'I',raw);assert all(i<n for i in indices);out={}
 for mode,encoded in row['completeStreamBytesBase64'].items():
  kind='f'if mode=='productionPositionAttribute'else'd';data=base64.b64decode(encoded,validate=True);size=4 if kind=='f'else 8;assert len(data)==n*3*size;values=struct.unpack('<'+str(n*3)+kind,data);assert all(math.isfinite(v)for v in values);positions=[values[i:i+3]for i in range(0,len(values),3)];triangles=[[positions[j]for j in indices[i:i+3]]for i in range(0,len(indices),3)];out[mode]=dict(triangles=triangles,bins=bins_for_triangles(triangles),completeUnusedPositions=positions)
 assert set(out)=={'productionPositionAttribute','actualLiteral','explicitLeftAssociatedF32ModelMatrix','explicitBalancedF32ModelMatrix'};return out
