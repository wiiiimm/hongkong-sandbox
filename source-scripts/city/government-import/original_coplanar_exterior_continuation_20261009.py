"""Exact original coplanar exterior sheet connectivity; diagnosis only.

An authored triangulation cut is not geometric evidence that a whole exterior
sheet is below ground. Near-coplanar faces and corner-only contacts never count.
"""
import collections,numpy as np
from fractions import Fraction
from exact_original_shell_intersections_20261009 import rational_face,intersection_points

def plane(face):
 a,b,c=rational_face(face);u=tuple(b[k]-a[k] for k in range(3));v=tuple(c[k]-a[k] for k in range(3));n=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])
 if not any(n):return None
 d=-sum(n[k]*a[k] for k in range(3));scale=next(x for x in n if x);return tuple(x/scale for x in (*n,d))
def diagnose(triangles,contexts,affected):
 tri=np.asarray(triangles,float);assert tri.ndim==3 and tri.shape[1:]==(3,3) and np.isfinite(tri).all()
 assert len(contexts)==len(tri) and [c['sourceFace'] for c in contexts]==list(range(len(tri)))
 normal=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);length=np.linalg.norm(normal,axis=1);ratio=np.divide(normal[:,1],length,out=np.zeros(len(tri)),where=length>0)
 groups=collections.defaultdict(list);keys=[]
 for i,f in enumerate(tri):
  key=plane(f) if length[i]>0 and abs(ratio[i])<=.25 else None;keys.append(key)
  if key:groups[key].append(i)
 out=[];lo=tri.min(axis=1);hi=tri.max(axis=1)
 for i in affected:
  assert type(i)is int and 0<=i<len(tri) and keys[i]
  candidates=groups[keys[i]];adj={j:set() for j in candidates};contacts=[]
  for k,a in enumerate(candidates):
   for b in candidates[k+1:]:
    if np.any(hi[a]<lo[b]) or np.any(hi[b]<lo[a]):continue
    points=intersection_points(rational_face(tri[a]),rational_face(tri[b]))
    if len(points)>1:adj[a].add(b);adj[b].add(a);contacts.append({'originalFaces':[a,b],'exactContactPoints':[[str(v) for v in p] for p in sorted(points)]})
  reached={i};previous={i:None};todo=[i]
  while todo:
   for j in sorted(adj[todo.pop()]):
    if j not in reached:reached.add(j);previous[j]=next(k for k in sorted(adj[j]) if k in reached);todo.append(j)
  exposed=[j for j in sorted(reached) if contexts[j]['groundProjectionCovered'] and contexts[j]['minimum'] and contexts[j]['maximumObservedGapM']>0]
  out.append({'sourceFace':i,'exactPlane':[str(x) for x in keys[i]],'completeCoplanarOriginalCandidateFaces':candidates,'exactConnectedCoplanarSheetFaces':sorted(reached),'exposedOriginalSheetFaces':exposed,'hasActualAboveGroundExteriorContinuation':bool(exposed),'rawSourceFaceExposureGapRetained':contexts[i]['maximumObservedGapM'],'exactPositiveDimensionContacts':[c for c in contacts if set(c['originalFaces'])<=reached],'originalGeometryChanges':0,'installationApproved':False})
 return {'wholeOriginalFacesAccounted':len(tri),'rows':out,'closedSolidCertified':False,'installationApproved':False,'diagnosticOnly':True}
