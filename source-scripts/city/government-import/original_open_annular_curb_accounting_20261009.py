"""Bounded original low annular exterior curb, not a building/supporting solid.

Every non-wall facet keeps ordinary clearance. Grade contact is recomputed on
the actual upper ground envelope. This feature cannot root or support others.
Source-specific provenance/current foreign scope and all independent physical
checks remain mandatory in the caller; this kernel cannot install a model.
"""
import collections,hashlib,json
from fractions import Fraction
import numpy as np,shapely
from exact_original_shell_intersections_20261009 import rational_face,intersection_points,shell_self_intersections
from exact_original_component_contacts_20261009 import contact_measure
from exact_original_upper_ground_interfaces_20261009 import exact_upper_ground_interfaces
def canonical(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def verify(triangles,contexts,part_faces,drawn_ground,*,expected_binding,current_binding):
 tri=np.asarray(triangles,float);ground=np.asarray(drawn_ground,float)
 assert tri.ndim==3 and tri.shape[1:]==(3,3) and len(tri) and np.isfinite(tri).all()
 assert ground.ndim==3 and ground.shape[1:]==(3,3) and len(ground) and np.isfinite(ground).all()
 assert expected_binding==current_binding
 assert current_binding['completeOriginalWorldTrianglesSHA256']==hashlib.sha256(tri.tobytes()).hexdigest()
 assert current_binding['currentDrawnGroundSHA256']==hashlib.sha256(ground.tobytes()).hexdigest()
 assert current_binding['completeCurrentFacetContextsSHA256']==canonical(contexts)
 ids=list(part_faces);assert ids==sorted(set(ids)) and all(type(i) is int and 0<=i<len(tri) for i in ids) and 12<=len(ids)<=100
 assert current_binding['completeOriginalPartFacesSHA256']==canonical(ids)
 assert len(contexts)==len(tri) and [c['sourceFace'] for c in contexts]==list(range(len(tri)))
 t=tri[ids];normal=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);size=np.linalg.norm(normal,axis=1);assert (size>0).all(),'Collapsed curb facet'
 ratio=normal[:,1]/size;walls={ids[k] for k in range(len(ids)) if abs(ratio[k])<=.25};caps={ids[k] for k in range(len(ids)) if ratio[k]>.25}
 assert walls and caps,'No actual original wall/cap part'
 assert 0<float(np.ptp(t[:,:,1]))<=1 and float(np.ptp(t[:,:,0]))<=30 and float(np.ptp(t[:,:,2]))<=30,'Part exceeds bounded low exterior role'
 polygons=shapely.polygons(tri[sorted(caps)][:,:,[0,2]]);cap=shapely.union_all(polygons)
 assert cap.geom_type=='Polygon' and cap.is_valid and len(cap.interiors)==1,'Original upper cap must form one complete annular plan'
 hole=shapely.Polygon(cap.interiors[0]);assert 0<cap.area<=10 and cap.area<hole.area,'Broad solid cap is not a narrow low curb'
 edges=collections.defaultdict(list);adj={i:set() for i in ids}
 for i in ids:
  for a,b in zip(tri[i],np.roll(tri[i],-1,axis=0)):
   edges[tuple(sorted((tuple(a),tuple(b))))].append((i,1 if tuple(a)<tuple(b) else -1))
 boundary=[]
 for key,members in edges.items():
  assert len(members)<=2,'Nonmanifold original curb'
  if len(members)==2:
   (i,a),(j,b)=members;assert a!=b,'Reversed original curb winding';adj[i].add(j);adj[j].add(i)
  else:assert members[0][0] in walls,'Upper cap is detached/open';boundary.append(key)
 assert boundary,'Closed building solid is not open curb role'
 boundary_adj=collections.defaultdict(set)
 for a,b in boundary:boundary_adj[a].add(b);boundary_adj[b].add(a)
 assert all(len(v)==2 for v in boundary_adj.values()),'Original lower boundary is not closed perimeter loops'
 remaining=set(boundary_adj);loops=0
 while remaining:
  seed=min(remaining);seen={seed};todo=[seed]
  while todo:
   for j in boundary_adj[todo.pop()]:
    if j not in seen:seen.add(j);todo.append(j)
  remaining-=seen;loops+=1
 assert loops==2,'Original lower boundary must retain both annular sides'
 seen={ids[0]};todo=[ids[0]]
 while todo:
  for j in adj[todo.pop()]:
   if j not in seen:seen.add(j);todo.append(j)
 assert seen==set(ids),'Detached original curb part'
 self_test=shell_self_intersections(t);assert self_test['selfIntersectionFree'],'Self-intersecting original curb'
 affected=[]
 for i in ids:
  c=contexts[i];assert c['groundProjectionCovered'] is True and c['minimum'] and np.isfinite(c['minimum']['minimumGapM'])
  if i not in walls:assert c['minimum']['minimumGapM']>=-.5,'Buried original upward/non-wall surface'
  if c['minimum']['minimumGapM']<-.5:assert i in walls;affected.append(i)
 exposed={i for i in caps if contexts[i]['maximumObservedGapM'] is not None and contexts[i]['maximumObservedGapM']>0};assert exposed,'No original exposed upper cap'
 previous={i:None for i in exposed};todo=list(exposed)
 while todo:
  i=todo.pop()
  for j in adj[i]:
   if j not in previous:previous[j]=i;todo.append(j)
 paths=[]
 for i in affected:
  path=[i]
  while previous[path[-1]] is not None:path.append(previous[path[-1]])
  paths.append(dict(sourceFace=i,exactOriginalExposedCapPath=path))
 witnesses=exact_upper_ground_interfaces(tri,sorted(walls),ground)
 assert witnesses,'No exact positive-dimensional original wall/current upper-ground contact'
 return dict(contract='bounded-original-open-annular-curb-v1',originalPartFaces=ids,affectedOriginalWallFaces=affected,originalCapFaces=sorted(caps),annularCapAreaM2=float(cap.area),innerVoidAreaM2=float(hole.area),openLowerPerimeterLoops=loops,selfIntersectionProof=self_test,exactOriginalExposedCapPaths=paths,exactActualGradeInterfaces=witnesses,originalLowExteriorRoleVerified=True,structuralRootCredit=False,maySupportOtherComponents=False,closedSolidCertified=False,sourceGeometryChanges=0,fullAcceptance=False,installationApproved=False)
