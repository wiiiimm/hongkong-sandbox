"""UNEXECUTED exact plane partition for named saved current protection masks.
Not an ordinary/coverage/seam/role certificate; packing is checked separately.
"""
from fractions import Fraction as F
from upton_original_tin_current_ring_join_nomination_v1_20261012 import point,nonzero,triangulate,packed,split_rectangle,boundary_edges

def orient(a,b,p):return (b[0]-a[0])*(p[2]-a[1])-(b[1]-a[1])*(p[0]-a[0])
def mask(raw):
 q=[tuple(F(v)for v in x)for x in raw];assert len(q)==3 and all(len(x)==2 for x in q)
 a=sum(x[0]*y[1]-x[1]*y[0]for x,y in zip(q,q[1:]+q[:1]));assert a!=0,'Collapsed protection mask'
 if a<0:q.reverse()
 return q

def clip(poly,a,b,inside):
 out=[]
 for u,v in zip(poly,poly[1:]+poly[:1]):
  du=orient(a,b,u)*(1 if inside else -1);dv=orient(a,b,v)*(1 if inside else -1)
  if du>=0:out.append(u)
  if du*dv<0:
   t=du/(du-dv);out.append(tuple(u[k]+t*(v[k]-u[k])for k in range(3)))
 clean=[]
 for q in out:
  if not clean or clean[-1]!=q:clean.append(q)
 if len(clean)>1 and clean[0]==clean[-1]:clean.pop()
 return clean

def split_mask(poly,m):
 """Exact convex plane partition; boundary-only polygons are not duplicated."""
 remain=list(poly);outside=[]
 for a,b in zip(m,m[1:]+m[:1]):
  if not remain:break
  if any(orient(a,b,x)<0 for x in remain):
   q=clip(remain,a,b,False)
   if len(q)>=3:outside.append(q)
  remain=clip(remain,a,b,True)
 return (remain if len(remain)>=3 else []),outside

def split_union(poly,masks):
 """Disjoint assigned bins for overlapping masks; every untouched point remains
 on its source plane. Zero/vertical projections stay recorded, not discarded.
 """
 pending=[list(poly)];inside=[]
 for i,m in enumerate(masks):
  nxt=[]
  for q in pending:
   # Exact closed bounds: omitted masks have strict disjoint projected bounds.
   if any(max(x[c]for x in q)<min(v[k]for v in m)or min(x[c]for x in q)>max(v[k]for v in m)for k,c in [(0,0),(1,2)]):
    nxt.append(q);continue
   part,rest=split_mask(q,m)
   if part:inside.append(dict(mask=i,polygon=part))
   nxt+=rest
  pending=nxt
 return dict(protected=inside,unprotected=pending)

def partition(face,domain,core,masks,kind):
 assert kind in ('originalTIN','capturedCurrent')
 original=[point(x)for x in face];d=split_rectangle(original,domain)['inside'];emitted=[]
 if not d:return emitted
 # A convex polygon is decomposed only for rectangle helper's triangle API.
 for t in triangulate(d):
  cut=split_rectangle(t,core)
  if kind=='capturedCurrent':
   emitted +=[dict(region='currentExteriorRing',mask=None,polygon=q)for q in cut['outside']]
  if cut['inside']:
   parts=split_union(cut['inside'],masks)
   if kind=='originalTIN':emitted +=[dict(region='sourceOutsideProtection',mask=None,polygon=q)for q in parts['unprotected']]
   else:emitted +=[dict(region='currentProtection',**q)for q in parts['protected']]
 return emitted

def same_triplet(t,face):return list(t)==[point(x)for x in face]
def interface_edges(poly,core,masks):
 """Only explicit retention/core cuts; no global manifold admission rule."""
 for a,b in zip(poly,poly[1:]+poly[:1]):
  if (a[0],a[2])==(b[0],b[2]):continue
  causes=[]
  for axis,value in [(0,F(core[0])),(2,F(core[1])),(0,F(core[2])),(2,F(core[3]))]:
   if a[axis]==b[axis]==value:causes.append(dict(kind='coreBoundary',axis=axis,value=str(value)))
  for i,m in enumerate(masks):
   for j,(u,v)in enumerate(zip(m,m[1:]+m[:1])):
    if orient(u,v,a)==orient(u,v,b)==0 and all(min(u[k],v[k])<=x[c]<=max(u[k],v[k])for x in [a,b]for k,c in [(0,0),(1,2)]):causes.append(dict(kind='protectionMaskBoundary',mask=i,edge=j))
  if causes:yield (a,b),causes
