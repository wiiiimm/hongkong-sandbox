"""Exact contacts of complete original finite triangle, segment and point hulls.

Zero-area authored faces remain finite primitives; they are never dropped or
repaired. A point contact remains dimension zero, never positive support.
"""
import numpy as np
from exact_original_shell_intersections_20261009 import rational_face,intersection_points,sub,add,mul,dot,cross,cross2,segment_has
from exact_original_component_contacts_20261009 import contact_measure
def dimension(face):
 if any(cross(sub(face[1],face[0]),sub(face[2],face[0]))):return 2
 return 0 if len(set(face))==1 else 1
def point_in_triangle(p,face):
 n=cross(sub(face[1],face[0]),sub(face[2],face[0]));assert any(n)
 if dot(n,sub(p,face[0])):return False
 drop=max(range(3),key=lambda i:abs(n[i]));axes=[i for i in range(3) if i!=drop];xy=lambda q:tuple(q[i] for i in axes)
 signs=[cross2(sub(xy(b),xy(a)),sub(xy(p),xy(a))) for a,b in zip(face,face[1:]+face[:1])]
 return all(s>=0 for s in signs) or all(s<=0 for s in signs)
def point_in_hull(p,face):
 d=dimension(face)
 if d==2:return point_in_triangle(p,face)
 a,b=min(face),max(face)
 return p==a if d==0 else segment_has(a,b,p)
def segment_triangle(a,b,face):
 n=cross(sub(face[1],face[0]),sub(face[2],face[0]));assert any(n)
 da,db=dot(n,sub(a,face[0])),dot(n,sub(b,face[0]))
 if da or db:
  if da==db:return set()
  t=da/(da-db)
  if not 0<=t<=1:return set()
  p=add(a,mul(sub(b,a),t));return {p} if point_in_triangle(p,face) else set()
 # Both endpoints lie in the exact triangle plane. Clip the complete finite
 # segment against all three oriented triangle halfplanes in that plane.
 drop=max(range(3),key=lambda i:abs(n[i]));axes=[i for i in range(3) if i!=drop];xy=lambda p:tuple(p[i] for i in axes)
 orientation=cross2(sub(xy(face[1]),xy(face[0])),sub(xy(face[2]),xy(face[0])))
 sign=1 if orientation>0 else -1;lo,hi=0,1
 for u,v in zip(face,face[1:]+face[:1]):
  start=sign*cross2(sub(xy(v),xy(u)),sub(xy(a),xy(u)))
  end=sign*cross2(sub(xy(v),xy(u)),sub(xy(b),xy(u)));delta=end-start
  if delta==0:
   if start<0:return set()
  elif delta>0:lo=max(lo,-start/delta)
  else:hi=min(hi,-start/delta)
  if lo>hi:return set()
 return {add(a,mul(sub(b,a),t)) for t in [lo,hi]}
def segment_segment(a,b,u,v):
 d,e,offset=sub(b,a),sub(v,u),sub(u,a);normal=cross(d,e)
 if not any(normal):
  if any(cross(d,offset)):return set()
  return {p for p in [a,b,u,v] if segment_has(a,b,p) and segment_has(u,v,p)}
 drop=max(range(3),key=lambda i:abs(normal[i]));axes=[i for i in range(3) if i!=drop];xy=lambda p:tuple(p[i] for i in axes)
 den=cross2(xy(d),xy(e));t=cross2(xy(offset),xy(e))/den;s=cross2(xy(offset),xy(d))/den
 if not (0<=t<=1 and 0<=s<=1):return set()
 p,q=add(a,mul(d,t)),add(u,mul(e,s));return {p} if p==q else set()
def finite_intersection_points(a,b):
 da,db=dimension(a),dimension(b)
 if da==db==2:return intersection_points(a,b)
 if da==0:return {a[0]} if point_in_hull(a[0],b) else set()
 if db==0:return {b[0]} if point_in_hull(b[0],a) else set()
 if da==1 and db==2:return segment_triangle(min(a),max(a),b)
 if da==2 and db==1:return segment_triangle(min(b),max(b),a)
 return segment_segment(min(a),max(a),min(b),max(b))
def primitive_census(triangles):
 faces=[rational_face(f) for f in triangles];parts={d:[i for i,f in enumerate(faces) if dimension(f)==d] for d in [0,1,2]}
 assert sorted(i for ids in parts.values() for i in ids)==list(range(len(faces)))
 return dict(completeFaces=len(faces),exactPointFaceIDs=parts[0],exactSegmentFaceIDs=parts[1],exactAreaFaceIDs=parts[2],sourceFacesOmitted=0,geometryChanges=0)
def exact_finite_contacts(triangles_a,face_ids_a,triangles_b,face_ids_b,*,maximum_pairs=1000000):
 a,b=np.asarray(triangles_a),np.asarray(triangles_b);ids_b=np.asarray(face_ids_b,dtype=int)
 assert len(face_ids_a) and len(ids_b);low,high=b[ids_b].min(1),b[ids_b].max(1);ca,cb,records,tested={},{},[],0
 for fi in face_ids_a:
  fi=int(fi);hits=np.flatnonzero(np.all(high>=a[fi].min(0),axis=1)&np.all(low<=a[fi].max(0),axis=1))
  if not len(hits):continue
  if fi not in ca:ca[fi]=rational_face(a[fi])
  for ix in hits:
   fj=int(ids_b[ix]);tested+=1;assert tested<=maximum_pairs,'Explicit exact-pair resource bound exceeded'
   if fj not in cb:cb[fj]=rational_face(b[fj])
   points=finite_intersection_points(ca[fi],cb[fj])
   if points:records.append(dict(sourceFaceA=fi,sourceFaceB=fj,sourcePrimitiveDimensionA=dimension(ca[fi]),sourcePrimitiveDimensionB=dimension(cb[fj]),**contact_measure(points)))
 return dict(contacts=records,trianglePairsTested=tested,allPairsExamined=True,sourceFacesOmitted=0,geometryChanges=0,physicalSupportAccepted=False)
