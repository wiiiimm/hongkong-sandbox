"""Source-defined coplanar full-edge patches inside one original host body.

The complete supplied body is partitioned by the existing exact Fraction plane
key and exact shared full original edges. This supplies no approximate welding,
hole, role, supporting roof or structural credit. Unused zero-area facets and
all original body/patch boundary incidences remain explicit.
"""
from collections import defaultdict
import hashlib,json
import numpy as np
from original_coplanar_exterior_continuation_20261009 import plane
from exact_original_body_boundary_group_census_v1_20261011 import census
from exact_original_shell_intersections_20261009 import rational_face

def canonical(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def upward(face):
 a,b,c=rational_face(face);u=[b[i]-a[i]for i in range(3)];v=[c[i]-a[i]for i in range(3)];return u[2]*v[0]-u[0]*v[2]>0
def verify(world,source_faces,*,expected_binding=None):
 w=np.asarray(world,float);assert w.ndim==3 and w.shape[1:]==(3,3)and np.isfinite(w).all();ids=list(map(int,source_faces));assert ids and ids==sorted(set(ids))and min(ids)>=0 and max(ids)<len(w)
 binding=dict(completeWorldSHA256=hashlib.sha256(w.tobytes()).hexdigest(),completeOriginalBodyFacesSHA256=canonical(ids))
 if expected_binding is not None:assert expected_binding==binding,'Original complete body changed'
 keys={f:plane(w[f])for f in ids};zeros=[f for f in ids if keys[f]is None];edgefaces=defaultdict(list)
 for f in ids:
  if keys[f]is None:continue
  vertices=list(map(tuple,w[f]))
  for a,b in zip(vertices,vertices[1:]+vertices[:1]):assert a!=b;edgefaces[tuple(sorted((a,b)))].append(f)
 adj={f:set()for f in ids if keys[f]is not None}
 for faces in edgefaces.values():
  for f in faces:
   for other in faces:
    if f!=other and keys[f]==keys[other]:adj[f].add(other)
 remaining=set(adj);patches=[]
 while remaining:
  start=min(remaining);seen={start};todo=[start]
  while todo:
   for f in adj[todo.pop()]:
    if f not in seen:seen.add(f);todo.append(f)
  remaining-=seen;patch=sorted(seen);assert all(keys[f]==keys[start]for f in patch)
  patches.append(dict(completeOriginalPatchFaces=patch,exactOriginalPlane=[str(v)for v in keys[start]],allPatchFacesExactUpward=all(upward(w[f])for f in patch),completePatchBoundaryInventory=census(w,patch),completePatchBoundaryOriginalBodyIncidences=[dict(completeActualEdge=e,allOriginalBodyIncidentFaces=edgefaces[e])for e in sorted(edgefaces)if len([f for f in edgefaces[e]if f in seen])==1],originalSurfacePatchOnly=True,originalOpeningOrRoofRoleCertified=False))
 assert sorted(zeros+[f for p in patches for f in p['completeOriginalPatchFaces']])==ids
 return dict(binding=binding,completeOriginalBodyFaces=ids,exactZeroAreaOriginalFaces=zeros,allSourceDefinedFullEdgeCoplanarPatches=patches,allOriginalBodyNonzeroEdges=[dict(completeActualEdge=e,allOriginalBodyIncidentFaces=edgefaces[e])for e in sorted(edgefaces)],completeSourcePartition=True,noNearCoplanarJoining=True,noPointOnlyJoining=True,zeroAreaFacesReceiveNoSupportCredit=True,visualRoleAccepted=False,structuralRootOrBridgeCredit=False)
