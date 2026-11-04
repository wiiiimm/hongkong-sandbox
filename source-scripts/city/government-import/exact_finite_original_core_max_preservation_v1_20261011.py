"""DRAFT full finite original native MAX preservation, including point/segment contacts."""
from fractions import Fraction as F
from exact_faithful_source_step_junction_feasibility_v2_20261011 import native_footprints,project
from exact_compute_transition_mesh_v1_20261011 import height,contains,edge_intersections
from exact_source_core_ten_metre_transition_domain_v1_20261011 import intersection
from exact_original_projection_coverage_v2_20261010 import signed_area,clean,subtract,cross
from exact_atomic_terrain_domain_boundary_ring_v1_20261011 import at,on

def finite_contains(poly,p):
 if not poly:return False
 if signed_area(poly):return contains(poly,p)
 a,b=max(((a,b)for a in poly for b in poly),key=lambda ab:sum((ab[0][k]-ab[1][k])**2 for k in[0,1]))
 return p==a if a==b else on(a,b,p)is not None

def linear_clip(poly,value):
 out=[]
 for p,q in zip(poly,poly[1:]+poly[:1]):
  vp,vq=value(p),value(q);ip,iq=vp>=0,vq>=0
  if ip:out.append(p)
  if ip!=iq:
   t=vp/(vp-vq);out.append(tuple(p[k]+t*(q[k]-p[k])for k in[0,1]))
 return clean(out)

def closed_segment_union(a,b,regions):
 if a==b:return dict(exactPoint=a,closedCovered=any(finite_contains(q,a)for q in regions),pointOnly=True)
 cuts={F(0),F(1)}
 for poly in regions:
  for p in poly:
   t=on(a,b,p)
   if t is not None:cuts.add(t)
  for u,v in zip(poly,poly[1:]+poly[:1]):
   if u!=v:
    for p in edge_intersections(a,b,u,v):cuts.add(on(a,b,p))
 cuts=sorted(cuts);points=[dict(parameter=t,allWitnessRegions=[i for i,q in enumerate(regions)if finite_contains(q,at(a,b,t))])for t in cuts];intervals=[dict(parameters=[lo,hi],allWitnessRegions=[i for i,q in enumerate(regions)if finite_contains(q,at(a,b,(lo+hi)/2))])for lo,hi in zip(cuts,cuts[1:])]
 return dict(exactEndpoints=[a,b],allClosedCutPoints=points,allPositiveAtomicIntervals=intervals,closedCovered=all(r['allWitnessRegions']for r in points+intervals),noPointOnlyIntervalCredit=True)

def closed_piece_coverage(piece,regions):
 positive=[p for p in regions if signed_area(p)>0];remaining=[piece]if signed_area(piece)>0 else []
 for p in positive:
  remaining=[q for r in remaining for q in subtract(r,p)]
  if not remaining:break
 edges=[closed_segment_union(a,b,regions)for a,b in zip(piece,piece[1:]+piece[:1])];return dict(exactCoreIntersection=piece,allUncoveredPositiveAreaPolygons=remaining,exactUncoveredPositiveArea=sum(signed_area(p)for p in remaining),allCompleteClosedBoundaryProofs=edges,wholeFiniteCovered=not remaining and all(e['closedCovered']for e in edges))

def added_native_core_max(source_triangles,added_triangles):
 source=native_footprints(source_triangles);added=native_footprints(added_triangles);rows=[]
 for gi,t in enumerate(added['tri']):
  if not added['indexed'][gi]:rows.append(dict(addedFace=gi,drawnButNativeHeightExcluded=True,unchangedNativeIndexExclusionOnly=True,drawnContactsStillUnqualified=True,coreMAXPreserved=True));continue
  ids,selection=source['ground'].select(t);ids=[int(i)for i in ids if source['indexed'][int(i)]];newpoly=added['polys'][gi];pieces=[];regions=[];witnesses=[]
  for i in ids:
   p=intersection(newpoly,source['polys'][i])
   if not p:continue
   pieces.append(dict(originalFace=i,exactFiniteProjectionIntersection=p));valid=linear_clip(p,lambda x:height(source['tri'][i],x)-height(t,x))
   if valid:witnesses.append(dict(originalFace=i,exactOriginalPlaneDominatesAddedRegion=valid));regions.append(valid)
  proofs=[dict(originalFace=p['originalFace'],proof=closed_piece_coverage(p['exactFiniteProjectionIntersection'],regions))for p in pieces];rows.append(dict(addedFace=gi,completeOriginalIndexedFacetNominations=ids,completeOriginalClosedAABBProof=selection,allFiniteOriginalCoreIntersectionProofs=proofs,allExactOriginalPlaneWitnessRegions=witnesses,coreMAXPreserved=all(p['proof']['wholeFiniteCovered']for p in proofs),sourceFacesMustRemainUnchanged=True))
 return dict(completeOriginalDrawnFaces=len(source['tri']),completeAddedDrawnFaces=len(added['tri']),allOriginalNativeExcludedFaces=[i for i,v in enumerate(source['indexed'])if not v],allAddedNativeExcludedFaces=[i for i,v in enumerate(added['indexed'])if not v],actualFloat32AndNativeExclusionRule=True,allCompleteAddedFaceCoreMAXProofs=rows,wholeOriginalClosedCoreMAXPreserved=all(r['coreMAXPreserved']for r in rows),noSourceDeletionOrTolerance=True,notContactOrSeamOrActorApproval=True,productionFloat64EvaluationNotBitwiseCertified=True,noCandidate=True)
