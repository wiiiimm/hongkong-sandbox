"""Replay exact original wall paths through strictly clear original cap facets.

Geometric connection evidence only: no structural root, burial, or full physical
acceptance. Every credited non-wall facet independently keeps ordinary clearance.
"""
import collections, hashlib, json
import numpy as np
from exact_original_shell_intersections_20261009 import rational_face,intersection_points
from exact_original_component_contacts_20261009 import contact_measure
def verify(triangles,contexts,contacts,*,expected_binding,current_binding):
 tri=np.asarray(triangles,dtype=np.float64)
 assert tri.ndim==3 and tri.shape[1:]==(3,3) and len(tri) and np.isfinite(tri).all()
 assert expected_binding==current_binding and current_binding['completeOriginalWorldTrianglesSHA256']==hashlib.sha256(tri.tobytes()).hexdigest(),'Complete original source binding differs'
 canonical=lambda v:hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
 assert current_binding['completeCurrentFacetContextsSHA256']==canonical(contexts),'Complete original face contexts differ'
 assert current_binding['exactOriginalContactListSHA256']==canonical(list(contacts)),'Exact original contact inventory differs'
 assert len(contexts)==len(tri) and [r['sourceFace'] for r in contexts]==list(range(len(tri))),'Missing or repeated original face context'
 for r in contexts:
  assert r['groundProjectionCovered'] is True and r['minimum'] is not None and np.isfinite(r['minimum']['minimumGapM']),'Incomplete current original ground coverage'
 normals=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);size=np.linalg.norm(normals,axis=1);valid=size>0
 ratio=np.divide(normals[:,1],size,out=np.zeros(len(tri)),where=valid)
 affected={i for i,c in enumerate(contexts) if c['minimum']['minimumGapM']<-.5}
 walls={i for i in affected if valid[i] and abs(ratio[i])<=.25}
 assert affected==walls,'Non-wall source clearance failure cannot receive cap/wall path credit'
 eligible={i for i in range(len(tri)) if valid[i] and (abs(ratio[i])<=.25 or contexts[i]['minimum']['minimumGapM']>=-.5)}
 roofs={i for i in eligible if ratio[i]>.25}
 adjacency={i:set() for i in eligible};edges=collections.defaultdict(list)
 for i in sorted(eligible):
  for a,b in zip(tri[i],np.roll(tri[i],-1,axis=0)):
   if tuple(a)!=tuple(b):edges[tuple(sorted((tuple(a),tuple(b))))].append(i)
 for members in edges.values():
  for i in members:adjacency[i].update(set(members)-{i})
 seen=set();replayed=[];rational={}
 def face(i):
  if i not in rational:rational[i]=rational_face(tri[i])
  return rational[i]
 for pair in contacts:
  assert isinstance(pair,(list,tuple)) and len(pair)==2 and all(type(i) is int and 0<=i<len(tri) for i in pair),'Malformed original contact'
  i,j=pair;key=tuple(sorted(pair));assert i!=j and key not in seen;seen.add(key)
  assert valid[i] and valid[j],'Collapsed original faces cannot bridge'
  points=intersection_points(face(i),face(j));assert points,'Detached original contact'
  measured=contact_measure(points);assert measured['dimension']>0,'Point-only contact cannot bridge'
  credited=i in eligible and j in eligible
  replayed.append(dict(originalFaces=list(pair),**measured,credited=credited))
  if credited:adjacency[i].add(j);adjacency[j].add(i)
 previous={i:None for i in sorted(roofs)};todo=collections.deque(sorted(roofs))
 while todo:
  i=todo.popleft()
  for j in sorted(adjacency[i]):
   if j not in previous:previous[j]=i;todo.append(j)
 paths=[]
 for i in sorted(walls):
  path=[i]
  while path[-1] in previous and previous[path[-1]] is not None:path.append(previous[path[-1]])
  bridges=[j for j in path if abs(ratio[j])>.25]
  paths.append(dict(sourceFace=i,originalPath=path,hasExactOriginalStrictClearCapRoofPath=path[-1] in roofs,strictClearNonWallFaces=bridges,minimumNonWallClearanceM=min((contexts[j]['minimum']['minimumGapM'] for j in bridges),default=None),rawFaceExposurePositive=contexts[i].get('maximumObservedGapM') is not None and contexts[i]['maximumObservedGapM']>0))
 return dict(contract='original-strict-clear-cap-wall-paths-v1',completeOriginalFaces=len(tri),affectedOriginalWallFaces=sorted(walls),paths=paths,replayedOriginalContacts=replayed,allAffectedHavePaths=all(p['hasExactOriginalStrictClearCapRoofPath'] for p in paths),rawExposureFailures=[p['sourceFace'] for p in paths if not p['rawFaceExposurePositive']],collapsedOriginalFaces=np.flatnonzero(~valid).tolist(),sourceGeometryChanges=0,groundRootCredit=False,closedSolidCertified=False,burialRoleAccepted=False,fullAcceptance=False,installationApproved=False,qualification='Every credited exact original non-wall cap remains ordinary-clear across its complete finite facet. Positive-dimensional original contacts are recomputed, point/degenerate contacts cannot bridge. Full current roles, actual grade exposure/structural roots, all foreign/foundation/runtime/browser checks remain independent.')
