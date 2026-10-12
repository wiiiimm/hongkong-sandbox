"""UNEXECUTED bounded Upton surface partition/ruled-join nomination.
No source edits, smoothing, fixed-band change, mesh/root/role acceptance.
"""
from fractions import Fraction as F
import math,hashlib
import numpy as np
from exact_original_segment_surface_contact_band_20261009 import verify_contact_segment
from exact_original_boundary_vertical_join_feasibility_v1_20261011 import nominate

def point(p):
 assert len(p)==3 and all(type(v) in (int,float,F) for v in p)
 assert all(not isinstance(v,float) or math.isfinite(v) for v in p)
 return tuple(F(v) for v in p)
def bounds(b):
 assert len(b)==4 and all(type(v) in (int,float,F) for v in b)
 q=tuple(F(v) for v in b);assert q[0]<q[2] and q[1]<q[3];return q

def _clip(poly,axis,value,greater):
 out=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  da=(a[axis]-value)*(1 if greater else -1);db=(b[axis]-value)*(1 if greater else -1)
  if da>=0:out.append(a)
  if (da<0<db)or(db<0<da):
   t=da/(da-db);out.append(tuple(a[k]+t*(b[k]-a[k])for k in range(3)))
 # Repeated endpoints are an interpolation representation, not extra facets.
 clean=[]
 for p in out:
  if not clean or p!=clean[-1]:clean.append(p)
 if len(clean)>1 and clean[0]==clean[-1]:clean.pop()
 return clean

def split_rectangle(face,rectangle):
 """Disjoint positive-area inside/outside decomposition on the original plane.
 Degenerate source input remains separately inventoried, never given credit.
 """
 original=[point(p)for p in face];assert len(original)==3;box=bounds(rectangle)
 remain=original;outside=[]
 for axis,value,greater in [(0,box[0],True),(2,box[1],True),(0,box[2],False),(2,box[3],False)]:
  if not remain:break
  # Only a piece with a strictly exterior vertex belongs to this outside bin;
  # coincident boundary faces are not duplicated into inside and outside.
  if any((p[axis]-value)*(1 if greater else -1)<0 for p in remain):
   q=_clip(remain,axis,value,not greater)
   if len(q)>=3:outside.append(q)
  remain=_clip(remain,axis,value,greater)
 return dict(inside=remain if len(remain)>=3 else [],outside=outside,originalExactPoints=original)

def triangulate(poly):
 return [[poly[0],poly[i],poly[i+1]]for i in range(1,len(poly)-1)]if len(poly)>=3 else []
def nonzero(face):
 a,b,c=map(point,face);u=[b[k]-a[k]for k in range(3)];v=[c[k]-a[k]for k in range(3)]
 return any(u[i]*v[j]-u[j]*v[i]for i,j in [(0,1),(0,2),(1,2)])
def packed(face):
 a=np.asarray([[float(x)for x in p]for p in face],dtype='<f4');assert a.shape==(3,3)and np.isfinite(a).all();return a.astype('<f8')
def boundary_edges(face,rectangle):
 box=bounds(rectangle);out=[];pts=list(map(point,face))
 for a,b in zip(pts,pts[1:]+pts[:1]):
  if(a[0],a[2])==(b[0],b[2]):continue
  for axis,value in [(0,box[0]),(2,box[1]),(0,box[2]),(2,box[3])]:
   if a[axis]==b[axis]==value:out.append((a,b));break
 return out

def nominated_upper_join(edge,current_faces):
 """Reuse finite segment pieces; .1-band result is retained, never interpreted
 as a join approval. Exact pairwise plane crossings nominate ruled facets.
 """
 a,b=map(point,edge);assert(a[0],a[2])!=(b[0],b[2])
 line=np.asarray([[float(v)for v in p]for p in [a,b]],dtype='<f8')
 # Caller supplies the actual packed source edge, so no rational-to-F64 drift.
 assert [point(p.tolist())for p in line]==[a,b]
 proof=verify_contact_segment(line,np.asarray(current_faces,dtype='<f8'))
 if not proof['completeFiniteCoverage']:return dict(complete=False,rawFixedBandProof=proof,reason='Current drawn boundary has unproved complete finite coverage',joinNominations=[])
 pieces=[{**p,'left':F(p['left']),'right':F(p['right']),'h0':F(p['h0']),'h1':F(p['h1'])}for p in proof['completeOriginalSurfacePieces']]
 cuts={F(0),F(1)}
 for p in pieces:cuts.update([p['left'],p['right']])
 for i,p in enumerate(pieces):
  for q in pieces[i+1:]:
   l=max(p['left'],q['left']);r=min(p['right'],q['right']);s=(p['h1']-p['h0'])-(q['h1']-q['h0'])
   if l<=r and s:
    t=(q['h0']-p['h0'])/s
    if l<=t<=r:cuts.add(t)
 ordered=sorted(cuts);rows=[]
 for l,r in zip(ordered,ordered[1:]):
  if l==r:continue
  active=[p for p in pieces if p['left']<=(l+r)/2<=p['right']];assert active
  height=lambda p,t:p['h0']+t*(p['h1']-p['h0'])
  top=max(active,key=lambda p:(height(p,(l+r)/2),-p['originalSurfaceFace']))
  assert all(height(top,t)>=height(p,t)for p in active for t in [l,r])
  at=lambda t:tuple(a[k]+t*(b[k]-a[k])for k in range(3))
  u,v=at(l),at(r);old_u=(u[0],height(top,l),u[2]);old_v=(v[0],height(top,r),v[2])
  rows.append(dict(currentFace=top['originalSurfaceFace'],exactParameterInterval=[str(l),str(r)],ruled=nominate(old_u,old_v,u,v)))
 return dict(complete=True,rawFixedBandProof=proof,joinNominations=rows,noContactRootOrRoleCredit=True,sourceGeometryChanges=0)

def protected_core(whole_bounds,domain,margin=1):
 assert margin==1,'Declared source-bound margin cannot change'
 d=bounds(domain);allb=[]
 for b in whole_bounds:
  assert len(b)==2 and all(len(p)==3 for p in b);lo,hi=map(point,b);assert all(lo[k]<=hi[k]for k in range(3));allb.append((lo,hi))
 assert allb;scale=1024
 floor=lambda x:(x*scale).__floor__()/F(scale);ceil=lambda x:(x*scale).__ceil__()/F(scale)
 c=(floor(min(x[0][0]for x in allb)-1),floor(min(x[0][2]for x in allb)-1),ceil(max(x[1][0]for x in allb)+1),ceil(max(x[1][2]for x in allb)+1))
 assert d[0]<c[0]<c[2]<d[2]and d[1]<c[1]<c[3]<d[3],'Complete source/unused/literal/F32 region does not fit inside parent domain'
 return c
