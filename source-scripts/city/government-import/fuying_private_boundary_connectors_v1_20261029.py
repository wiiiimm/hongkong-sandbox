"""Build private derived-terrain connectors from exact existing finite mates.

No government building data is edited. This construction grants no approval;
all old derived terrain vertices/faces remain exact prefixes and every new join
requires fresh whole-node and full-scene validation.
"""
from copy import deepcopy
import numpy as np

def add_connectors(node,rows):
 out=deepcopy(node);mesh=out['nativeMesh'];beforepos=list(mesh['position']);beforeidx=list(mesh['index']);points=np.asarray(beforepos,dtype='float32').astype('float64').reshape(-1,3);records=[]
 for row in rows:
  assert row['hasLocalPlaneWithin1cm']and row['hasFiniteMateWithin1cm']
  p=np.asarray(row['point']);ids=np.flatnonzero(np.all(points==p,axis=1));assert len(ids);pidx=int(ids[0])
  plane=row['closestPlaneCandidates'][0];assert abs(plane['sourcePlaneDeltaY'])<.01 and plane['distanceXZ']<.01
  mate=min((m for m in row['mateCurves']if abs(m['pointDeltaM'])<.01),key=lambda m:abs(m['pointDeltaM']))
  a,b,c=beforeidx[3*plane['faceIndex']:3*plane['faceIndex']+3];axis=mate['axis'];coordinate=mate['coordinate'];start=len(mesh['index'])//3
  if p[axis]==coordinate:
   mesh['index'].extend([pidx,a,b,pidx,b,c,pidx,c,a]);mode='exact-boundary-source-point-to-existing-source-plane'
  else:
   assert abs(p[axis]-coordinate)<.002
   q=p.copy();q[axis]=coordinate;q[1]=mate['expectedMateY'];q=q.astype('float32').astype('float64');assert q[axis]==coordinate and abs(q[1]-p[1])<.01 and abs(q[1]-mate['expectedMateY'])<.01
   qidx=len(mesh['position'])//3;mesh['position'].extend(q.tolist());mesh['index'].extend([pidx,qidx,a,pidx,qidx,b,pidx,qidx,c]);mode='existing-finite-mate-boundary-vertex'
  tris=np.asarray(mesh['position'],dtype='float32').reshape(-1,3)[np.asarray(mesh['index'][start*3:]).reshape(-1,3)];cross=np.cross(tris[:,1].astype('float64')-tris[:,0],tris[:,2].astype('float64')-tris[:,0]);assert np.any(np.abs(cross[:,1])>=1e-10)
  records.append(dict(point=p.tolist(),mode=mode,ownSourceFaceIndex=plane['faceIndex'],finiteMate=mate,newFaceIndices=list(range(start,len(mesh['index'])//3)),sourcePlaneDistanceXZ=plane['distanceXZ'],sourcePlaneDeltaY=plane['sourcePlaneDeltaY']))
 assert mesh['position'][:len(beforepos)]==beforepos and mesh['index'][:len(beforeidx)]==beforeidx
 assert len(mesh['index'])//3<=25000
 mesh['source']['privateDerivedBoundaryConnectors']=dict(policy='exact-finite-mate-derived-join-experiment-v1',allPriorPositionsAndIndicesPreserved=True,sourceGeometryChanges=0,connectors=records,approval=False)
 return out
