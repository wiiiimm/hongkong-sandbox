"""Terrain-only rectangular join between exact finite upper boundaries."""
from fractions import Fraction as F
import numpy as np
from exact_faithful_multisurface_transition_domain_v1_20261011 import upper_anchors

def ring(b):
 x,z,X,Z=map(F,b);return [(x,z),(X,z),(X,Z),(x,Z)]

def boundary(faces,bounds):
 a=np.asarray(faces,dtype='<f8');p=a[:,:,[0,2]];lo,hi=p.min(1),p.max(1);x,z,X,Z=bounds
 # Same determinant expression and filter as production nativeTerrainSurface.
 ax,az=p[:,0,0],p[:,0,1];bx,bz=p[:,1,0],p[:,1,1];cx,cz=p[:,2,0],p[:,2,1];det=(bz-cz)*(ax-cx)+(cx-bx)*(az-cz)
 vertical=np.abs(det)<1e-10;touch=np.zeros(len(a),bool)
 for axis,value,other,lower,upper in [(0,x,1,z,Z),(0,X,1,z,Z),(1,z,0,x,X),(1,Z,0,x,X)]:touch|=(lo[:,axis]<=value)&(hi[:,axis]>=value)&(lo[:,other]<=upper)&(hi[:,other]>=lower)
 ids=np.flatnonzero(touch&~vertical);assert len(ids);r=ring(bounds);edges=[dict(start=r[i],end=r[(i+1)%4])for i in range(4)];q=[[tuple(F(float(v))for v in p)for p in face]for face in a[ids]];rows=upper_anchors(edges,q)
 return rows,dict(completeInputFaces=len(a),productionHeightFilteredFaceCount=int(vertical.sum()),completeClosedBoundaryCandidateFaceIds=ids.tolist())

def value(rows,side,t):
 matches=[r for r in rows if r['sourceUnionBoundary']==side and r['exactSourceParameterInterval'][0]<=t<=r['exactSourceParameterInterval'][1]];assert matches
 values=[]
 for r in matches:
  a,b=r['exactSourceParameterInterval'];u,v=r['exactEndpointY'];values.append(u+(v-u)*(t-a)/(b-a))
 assert len(set(values))==1,'Boundary has a real height discontinuity';return values[0]

def join(old,new,domain,outer,width,clip):
 assert 0<2*width<min(outer[2]-outer[0],outer[3]-outer[1]);inner=[outer[0]+width,outer[1]+width,outer[2]-width,outer[3]-width];o,op=boundary(old,outer);n,np_=boundary(new,inner);out=[];counts={'retainedOldTriangles':0,'retainedCoreTriangles':0,'joinTriangles':0}
 def emit(face,kind):
  face=np.asarray(face,float)
  if np.any(np.cross(face[1]-face[0],face[2]-face[0])!=0):out.append(face);counts[kind]+=1
 def clipped(face,box,kind):
  p=clip.rect(list(face),box)
  for i in range(1,len(p)-1):emit([p[0],p[i],p[i+1]],kind)
 x,z,X,Z=domain;a,b,c,d=outer
 for face in old:
  q=face[:,[0,2]]
  if q[:,0].max()<=a or q[:,0].min()>=c or q[:,1].max()<=b or q[:,1].min()>=d:out.append(face.copy());counts['retainedOldTriangles']+=1;continue
  for box in [[x,z,a,Z],[c,z,X,Z],[a,z,c,b],[a,d,c,Z]]:
   if box[0]<box[2]and box[1]<box[3]:clipped(face,box,'retainedOldTriangles')
 for face in new:
  q=face[:,[0,2]]
  if(q[:,0]>=inner[0]).all()and(q[:,0]<=inner[2]).all()and(q[:,1]>=inner[1]).all()and(q[:,1]<=inner[3]).all():out.append(face.copy());counts['retainedCoreTriangles']+=1
  else:clipped(face,inner,'retainedCoreTriangles')
 oring,iring=ring(outer),ring(inner)
 for side in range(4):
  knots=sorted({p for rows in [o,n]for r in rows if r['sourceUnionBoundary']==side for p in r['exactSourceParameterInterval']});assert knots[0]==0 and knots[-1]==1
  def vertex(r,t,y):
   a,b=r[side],r[(side+1)%4];return [float(a[0]+t*(b[0]-a[0])),float(y),float(a[1]+t*(b[1]-a[1]))]
  for a,b in zip(knots,knots[1:]):
   p=[vertex(oring,a,value(o,side,a)),vertex(oring,b,value(o,side,b)),vertex(iring,b,value(n,side,b)),vertex(iring,a,value(n,side,a))];emit(p[:3],'joinTriangles');emit([p[0],p[2],p[3]],'joinTriangles')
 return np.asarray(out),dict(outer=outer,inner=inner,widthM=width,counts=counts,oldBoundarySelection=op,newBoundarySelection=np_,oldExactUpperBoundary=o,newExactUpperBoundary=n,buildingGeometryChanges=0,transitionInteriorIsNewTriangulatedTerrain=True,exactPrepackingBoundaryHeights=True,installationApproved=False)
