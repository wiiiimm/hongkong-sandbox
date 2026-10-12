"""Exact saved-surface compatibility only; masks are not new terrain geometry."""
from fractions import Fraction as F
import math
from exact_original_paired_finite_clearance_v3_20261011 import clip_source

def point(p,n):
 assert len(p)==n
 q=tuple(F(float(v))if not isinstance(v,F)else v for v in p)
 assert all(not isinstance(v,float)or math.isfinite(v)for v in p)
 return q

def orient(a,b,c):return(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
def area(p):return sum(a[0]*b[1]-a[1]*b[0]for a,b in zip(p,p[1:]+p[:1]))
def on_segment(a,b,p):return orient(a,b,p)==0 and all(min(a[k],b[k])<=p[k]<=max(a[k],b[k])for k in range(2))
def meets(a,b,c,d):
 x,y,z,w=orient(a,b,c),orient(a,b,d),orient(c,d,a),orient(c,d,b)
 return(x*y<0 and z*w<0)or any([x==0 and on_segment(a,b,c),y==0 and on_segment(a,b,d),z==0 and on_segment(c,d,a),w==0 and on_segment(c,d,b)])
def polygon_masks(ring):
 """Exact ears for the six actual single simple rings; reject unsupported shapes."""
 p=[point(v,2)for v in ring]
 if p[0]==p[-1]:p.pop()
 assert len(p)>=3 and len(set(p))==len(p)and area(p)!=0
 for i in range(len(p)):
  for j in range(i+1,len(p)):
   if j in[i,(i+1)%len(p)]or i==(j+1)%len(p):continue
   assert not meets(p[i],p[(i+1)%len(p)],p[j],p[(j+1)%len(p)]),'Non-simple ring'
 if area(p)<0:p.reverse()
 original=list(p);out=[]
 while len(p)>3:
  ears=[]
  for i,b in enumerate(p):
   a,c=p[i-1],p[(i+1)%len(p)]
   if orient(a,b,c)<=0:continue
   if any(all(orient(x,y,v)>=0 for x,y in[(a,b),(b,c),(c,a)])for j,v in enumerate(p)if j not in[(i-1)%len(p),i,(i+1)%len(p)]):continue
   ears.append(i)
  assert ears,'No exact ear';i=ears[0];out.append([p[i-1],p[i],p[(i+1)%len(p)]]);p.pop(i)
 out.append(p);assert sum(area(t)for t in out)==area(original)and all(area(t)>=0 for t in out)
 return out

def projected_mask(face):
 p=[(q[0],q[2])for q in map(lambda p:point(p,3),face)]
 if area(p)<0:p.reverse()
 return p

def nonzero(face):
 a,b,c=[point(p,3)for p in face];u=[b[k]-a[k]for k in range(3)];v=[c[k]-a[k]for k in range(3)]
 return any(u[i]*v[j]-u[j]*v[i]for i,j in[(0,1),(0,2),(1,2)])

def masked_current_pair(source,current,mask):
 s=[point(p,3)for p in source];g=[point(p,3)for p in current];m=[point(p,2)for p in mask]
 assert len(s)==len(g)==len(m)==3 and area(m)>0
 if not nonzero(s):return dict(exactSourceZero=True,supportCredit=False)
 gp=[(p[0],p[2])for p in g];ga=area(gp)
 if ga==0:return dict(collapsedCurrentGroundProjection=True,affineHeightCredit=False,supportCredit=False)
 if ga<0:gp.reverse()
 poly=s
 for region in[m,gp]:
  for a,b in zip(region,region[1:]+region[:1]):
   if not poly:break
   poly=clip_source(poly,a,b)
 if not poly:return dict(closedMaskedProjectionDisjoint=True,supportCredit=False)
 a,b,c=g;u=[b[k]-a[k]for k in range(3)];v=[c[k]-a[k]for k in range(3)];n=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]);assert n[1]!=0
 rows=[]
 for x,y,z in poly:
  h=a[1]-(n[0]*(x-a[0])+n[2]*(z-a[2]))/n[1]
  rows.append(dict(exactOriginalSourcePoint=list(map(str,(x,y,z))),exactCurrentDrawnHeightM=str(h),exactGapM=str(y-h)))
 low=min(F(q['exactGapM'])for q in rows)
 return dict(completeConvexMaskedPairVertices=rows,exactMinimumGapM=str(low),existingOrdinaryLowerBoundM='-1/2',violatesExistingOrdinaryBound=low<F(-1,2),closedIntersectionMayBePointLineOrArea=True,noCoverageRootRoleOrAcceptanceCredit=True)
