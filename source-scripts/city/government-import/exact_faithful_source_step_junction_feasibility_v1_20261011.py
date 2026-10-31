"""DRAFT exact actual-native footprints and source-step vertical junction context."""
from fractions import Fraction as F
import numpy as np
from exact_closed_ground_aabb_pruning_v1_20261011 import CompleteGround
from exact_compute_transition_mesh_v1_20261011 import faces,project,height,contains,edge_intersections
from exact_source_core_ten_metre_transition_domain_v1_20261011 import polygon
from exact_original_projection_coverage_v2_20261010 import signed_area
from exact_original_3d_directed_edge_atom_census_v1_20261011 import parameter
from exact_original_shell_intersections_20261009 import cross,sub
from exact_faithful_multisurface_transition_domain_v1_20261011 import closed_pairs
from exact_atomic_terrain_domain_boundary_ring_v1_20261011 import on,at

def native_footprints(literal):
 a=np.asarray(literal,dtype='<f8');assert a.ndim==3 and a.shape[1:]==(3,3)and np.isfinite(a).all();actual=a.astype('<f4').astype('<f8');tri=faces(actual);polys=[];indexed=[];det=[]
 for t in actual:
  aa,bb,cc=t;v=(bb[2]-cc[2])*(aa[0]-cc[0])+(cc[0]-bb[0])*(aa[2]-cc[2]);det.append(float(v));q=project(t);polys.append(polygon(q)if signed_area(q)else q);indexed.append(bool(abs(v)>=1e-10))
 return dict(actual=actual,tri=tri,polys=polys,indexed=indexed,determinants=det,ground=CompleteGround(actual))

def native_query_inventory(native,point):
 p=tuple(F(v)for v in point);assert len(p)==2;ids,proof=native['ground'].select([(p[0],F(0),p[1])]);rows=[];owners=[]
 for i in map(int,ids):
  t=native['tri'][i];q=project(t);area=signed_area(q)
  if not area:rows.append(dict(face=i,indexed=False,projectedZero=True));continue
  poly=native['polys'][i];inside=contains(poly,p);row=dict(face=i,indexed=native['indexed'][i],exactClosedProjectionContainsQuery=inside,actualTriangle=t,exactHeight=height(t,p)if inside else None);rows.append(row)
  if inside and native['indexed'][i]:owners.append(i)
 return dict(exactBinaryQueryXZ=p,completeActualFiniteNominations=rows,allIndexedFiniteOwners=owners,allDrawnNonzeroProjectionOwners=[r['face']for r in rows if r.get('exactClosedProjectionContainsQuery')],completeClosedActualAABBProof=proof)

def whole_actual_source_edge(native,face,a,b):
 a=tuple(F(float(np.float32(float(v))))for v in a);b=tuple(F(float(np.float32(float(v))))for v in b);t=native['tri'][face];hits=[]
 for i,(u,v)in enumerate(zip(t,t[1:]+t[:1])):
  x,y=parameter(u,v,a),parameter(u,v,b)
  if x is not None and y is not None and x!=y:hits.append(dict(originalActualDirectedEdge=i,exactWholeParameters=[x,y]))
 return dict(actualCastEndpoints=[a,b],positiveActual3DEdge=a!=b,allExactFiniteOriginalEdgeOwners=hits,wholeEdgeQualified=bool(hits))

def bounded_outer_corner_ray(p,outer_edges,core_polys,band_polys):
 """Finite deterministic outer vertices <=10mL1; exact whole-ray coverage."""
 p=tuple(map(F,p));nodes=sorted({tuple(e[k])for e in outer_edges for k in ['start','end']if tuple(e[k])!=p and sum(abs(e[k][i]-p[i])for i in[0,1])<=10},key=lambda q:(sum((q[i]-p[i])**2 for i in[0,1]),q));allpolys=core_polys+band_polys;pairs=closed_pairs([[p,q]for q in nodes],allpolys);nominations={i:[]for i in range(len(nodes))}
 for i,j in pairs:nominations[i].append(j)
 rejected=[]
 for i,q in enumerate(nodes):
  ids=nominations[i];cuts={F(0),F(1)}
  for j in ids:
   poly=allpolys[j]
   for a,b in zip(poly,poly[1:]+poly[:1]):
    for x in edge_intersections(p,q,a,b):cuts.add(on(p,q,x))
  intervals=[];valid=True
  for lo,hi in zip(sorted(cuts),sorted(cuts)[1:]):
   witness=at(p,q,(lo+hi)/2);active=[j for j in ids if contains(allpolys[j],witness)];core=[j for j in active if j<len(core_polys)];band=[j-len(core_polys)for j in active if j>=len(core_polys)];intervals.append(dict(parameters=[lo,hi],witness=witness,allCoreOwners=core,allBandOwners=band))
   if core or not band:valid=False
  if valid:return dict(exactInnerPointXZ=p,exactRetainedOuterPointXZ=q,exactL1Length=sum(abs(q[k]-p[k])for k in[0,1]),allCompleteOpenRayIntervals=intervals,allClosedBucketPolygonCandidates=ids,earlierRejectedOuterNodes=rejected,finiteOuterNodesEnumerated=len(nodes),wholeBandRayCoverageOnlyNotTwoSidedConnectivity=True)
  rejected.append(dict(outer=q,allCompleteOpenRayIntervals=intervals))
 return dict(noBoundedWholeBandOnlyRay=True,allRejectedOuterNodes=rejected,finiteOuterNodesEnumerated=len(nodes),wholeBandRayCoverageOnlyNotTwoSidedConnectivity=True)

def vertical_junction(p,high,low,outer):
 p=tuple(map(F,p));high,low=F(high),F(low);outer=tuple(map(F,outer));assert len(p)==2 and len(outer)==3 and high>low and(p[0],p[1])!=(outer[0],outer[2]);triangle=[(p[0],high,p[1]),(p[0],low,p[1]),outer];normal=cross(sub(triangle[1],triangle[0]),sub(triangle[2],triangle[0]));assert any(normal)and signed_area(project(triangle))==0
 return dict(computeOnlyVerticalJunctionTriangle=triangle,exactPositive3DAreaSquared=sum(v*v for v in normal)/4,exactProjectedArea=F(0),exactSourceHeightGap=high-low,sourceHeightChanges=0,sourceCoreInnerVerticalTerminationUnpaired=True,notSourceAuthoredOrStructuralBridge=True,noCandidate=True,requiresWholeIntroducedBranchAndOuterSeams=True)
