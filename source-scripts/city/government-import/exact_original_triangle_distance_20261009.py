"""Exact rational distance witnesses between two complete original facets.

Diagnostic only: a near miss is not exact attachment, mounting or support.
Degenerate triangles retain their finite original edges/points.
"""
from exact_original_shell_intersections_20261009 import rational_face,sub,add,mul,dot,cross,intersection_points
def point_segment(p,a,b):
 u=sub(b,a);den=dot(u,u);t=max(0,min(1,dot(sub(p,a),u)/den)) if den else 0;q=add(a,mul(u,t));return dot(sub(p,q),sub(p,q)),p,q
def point_face(p,face):
 a,b,c=face;n=cross(sub(b,a),sub(c,a));den=dot(n,n);values=[point_segment(p,x,y) for x,y in zip(face,face[1:]+face[:1])]
 if den:
  q=sub(p,mul(n,dot(sub(p,a),n)/den));inside=[dot(cross(sub(y,x),sub(q,x)),n) for x,y in zip(face,face[1:]+face[:1])]
  if all(d>=0 for d in inside):values.append((dot(sub(p,q),sub(p,q)),p,q))
 return min(values,key=lambda r:r[0])
def segment_segment(a,b,c,d):
 values=[point_segment(a,c,d),point_segment(b,c,d)]+[(r[0],r[2],r[1]) for r in [point_segment(c,a,b),point_segment(d,a,b)]]
 u,v,w=sub(b,a),sub(d,c),sub(a,c);A,B,C,D,E=dot(u,u),dot(u,v),dot(v,v),dot(u,w),dot(v,w);den=A*C-B*B
 if den:
  s,t=(B*E-C*D)/den,(A*E-B*D)/den
  if 0<=s<=1 and 0<=t<=1:
   p,q=add(a,mul(u,s)),add(c,mul(v,t));values.append((dot(sub(p,q),sub(p,q)),p,q))
 return min(values,key=lambda r:r[0])
def triangle_distance(first,second):
 a,b=rational_face(first),rational_face(second);na=cross(sub(a[1],a[0]),sub(a[2],a[0]));nb=cross(sub(b[1],b[0]),sub(b[2],b[0]));values=[]
 if any(na) and any(nb):
  points=intersection_points(a,b)
  if points:
   p=min(points);return dict(exactSquaredDistanceM2='0',firstOriginalWitness=[str(x) for x in p],secondOriginalWitness=[str(x) for x in p],exactOriginalContact=True,supportCredit=False)
 values.extend(point_face(p,b) for p in a);values.extend((r[0],r[2],r[1]) for r in [point_face(p,a) for p in b])
 values.extend(segment_segment(p,q,r,s) for p,q in zip(a,a[1:]+a[:1]) for r,s in zip(b,b[1:]+b[:1]));dist,p,q=min(values,key=lambda r:r[0])
 return dict(exactSquaredDistanceM2=str(dist),firstOriginalWitness=[str(x) for x in p],secondOriginalWitness=[str(x) for x in q],exactOriginalContact=dist==0,supportCredit=False)
