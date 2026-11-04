"""DRAFT faithful all-originals+3joins renderer terrain nomination.
Source existing boundaries/crossings are raw context, not generated seam failures.
All introduced band edges require full genuine exact3D/F32 positive-edge incidence.
"""
from fractions import Fraction as F
import numpy as np
from exact_faithful_multisurface_transition_domain_v1_20261011 import upper_anchors,closed_pairs
from exact_compute_transition_mesh_v1_20261011 import faces,project,height,outer_segments,interpolated,split,fan,require
from exact_source_core_ten_metre_transition_domain_v1_20261011 import separated,intersection
from exact_original_projection_coverage_v2_20261010 import subtract,signed_area
from exact_original_3d_directed_edge_atom_census_v1_20261011 import census
from exact_original_finite_triangle_contacts_20261010 import finite_intersection_points
from exact_original_component_contacts_20261009 import contact_measure
from exact_closed_ground_aabb_pruning_v1_20261011 import CompleteGround

def union_clip(current,polys,checkpoints):
 cp=[project(f)for f in current];pairs=closed_pairs(cp,polys);by={i:[]for i in range(len(current))}
 for i,j in pairs:by[i].append(j)
 def compute(part):
  rows=[]
  for i in part:
   remaining=[cp[i]]
   for j in sorted(by[i]):
    remaining=[v for q in remaining for v in([q]if separated(q,polys[j])else subtract(q,polys[j]))]
    if not remaining:break
   rows.append(dict(currentPlane=i,allRemainingExactPositiveCells=remaining,allCompleteClosedBucketDomainPieces=sorted(by[i]),changed=sum(signed_area(q)for q in remaining)!=signed_area(cp[i])))
  return rows
 return checkpoints.map('complete-current-clip-to-source-bound-domain',list(range(len(current))),compute)

def production_faces(exact):
 world=np.asarray(exact,dtype='<f4');assert world.shape[1:]==(3,3)and np.isfinite(world).all();out=faces(world)
 # Literal makeNativeTerrain orientation rule, no altered source winding claim.
 for f in out:
  y=(f[1][2]-f[0][2])*(f[2][0]-f[0][0])-(f[1][0]-f[0][0])*(f[2][2]-f[0][2])
  if y<0:f[1],f[2]=f[2],f[1]
 return out

def generated_seams(allfaces,band_start,band_end,checkpoints=None,label="introduced-band-seams"):
 if checkpoints:
  from exact_resumable_projected_inventory_v1_20261011 import Checkpoints
  checkpoints=Checkpoints(checkpoints.folder/label,allfaces,checkpoints.contract["inputBindings"],checkpoints.check_inputs)
 d=census(allfaces,checkpoints);bad=[]
 for i,r in enumerate(d['allExact3DAtomicEdges']):
  if any(band_start<=e['face']<band_end for e in r['allDirectedIncidences']):
   if r['incidenceCount']!=2 or not r['exactOpposedTwoIncidences']:bad.append(dict(atomicEdge=i,completeActualIncidences=r))
 require(not bad,'Introduced compute band has unmatched/nonmanifold/same-directed exact finite seam',bad)
 return d

def nominate(core,joins,current,d,checkpoints):
 original=faces(core);joins=[[tuple(F(v)for v in p)for p in t]for t in joins];current=faces(current);assert len(original)==14798 and len(joins)==3
 inner=upper_anchors(d['sourceUnionBoundarySegments'],original);outerstructure=dict(allBoundaryAtoms=[dict(incidences=[e])for e in d['completeOuterBoundarySegments']]);outer=outer_segments(outerstructure,current)
 polygons=d['scratchOriginalProjectionUnionCells']+d['computeBandPolygons'];clips=union_clip(current,polygons,checkpoints);points={p for q in polygons for p in q}|{p for r in clips for q in r['allRemainingExactPositiveCells']for p in q}|{p for e in inner+outer for p in[e['start'],e['end']]}|{(p[0],p[2])for f in original+joins for p in f};cache={}
 def generated(p):
  if p not in cache:cache[p]=interpolated(p,inner,outer)
  return cache[p]
 band=[];roles=[]
 for i,p in enumerate(d['computeBandPolygons']):
  tri=fan(split(p,points),generated);band.extend(tri);roles.extend(dict(role='compute-generated-ten-metre-L1-band',bandPiece=i)for _ in tri)
 retained=[];retroles=[]
 for r in clips:
  for p in r['allRemainingExactPositiveCells']:
   tri=fan(split(p,points),lambda q:height(current[r['currentPlane']],q))if r['changed']else[current[r['currentPlane']]];retained.extend(tri);retroles.extend(dict(role='exact-clipped-retained-current-plane'if r['changed']else'byte-coordinate-unchanged-restored-parent-face',currentPlane=r['currentPlane'])for _ in tri)
 # Source projected overlaps are retained, not tested against 2.5D disjointness.
 # Every new band positive-projection overlap is forbidden, including originals.
 bandpoly=[project(f)for f in band];others=[project(f)for f in original+retained];pairs=closed_pairs(bandpoly,others);overlaps=[]
 for i,j in pairs:
  a=signed_area(intersection(bandpoly[i],others[j]))
  if a:overlaps.append(dict(bandFace=i,otherFace=j,exactAreaM2=a))
 pairs=closed_pairs(bandpoly,bandpoly)
 for i,j in pairs:
  if j<i:
   a=signed_area(intersection(bandpoly[i],bandpoly[j]))
   if a:overlaps.append(dict(bandFaces=[j,i],exactAreaM2=a))
 require(not overlaps,'Introduced band positive projected overlap',overlaps)
 literal=original+joins+band+retained;start=len(original)+len(joins);end=start+len(band);exact=generated_seams(literal,start,end,checkpoints,"exact-literal-integrated-seams");rendered=production_faces(literal);actual=generated_seams(rendered,start,end,checkpoints,"actual-Float32-integrated-seams")
 # Entire actualFloat32 band/source/retained projection is independently gated.
 actualband=[project(t)for t in rendered[start:end]];actualothers=[project(t)for t in rendered[:len(original)]+rendered[end:]];pairs=closed_pairs(actualband,actualothers);actualoverlaps=[]
 def compute_overlap(part):
  return [dict(bandFace=i,otherFace=j,exactPositiveAreaM2=area)for i,j in part if(area:=signed_area(intersection(actualband[i],actualothers[j])))>0]
 actualoverlaps.extend(checkpoints.map('actual-Float32-band-original-retained-overlaps',pairs,compute_overlap));selfpairs=closed_pairs(actualband,actualband);selfpairs=[(i,j)for i,j in selfpairs if j<i]
 def compute_self(part):return [dict(bandFaces=[j,i],exactPositiveAreaM2=area)for i,j in part if(area:=signed_area(intersection(actualband[i],actualband[j])))>0]
 actualoverlaps.extend(checkpoints.map('actual-Float32-band-self-overlaps',selfpairs,compute_self));require(not actualoverlaps,'Introduced actualFloat32 band positive projected overlap',actualoverlaps)
 # Complete finite generated-band/source/joins contact census. AABBs are closed
 # exact Fraction predicates; point contacts don't prove support or hide crossings.
 alloriginal=original+joins;ground=CompleteGround(np.asarray(alloriginal,dtype='<f8'))
 def finite_compute(part):
  result=[]
  for i in part:
   f=band[i];ids,proof=ground.select(f);contacts=[]
   for j in map(int,ids):
    g=alloriginal[j]
    if any(max(p[k]for p in f)<min(p[k]for p in g)or max(p[k]for p in g)<min(p[k]for p in f)for k in range(3)):continue
    points=finite_intersection_points(f,g)
    if points:contacts.append(dict(sourceOrJoinFace=j,**contact_measure(points)))
   result.append(dict(bandFace=i,completeClosedSourceAndJoinSelection=proof,allExactFiniteContacts=contacts))
  return result
 finite=checkpoints.map('complete-new-band-original-join-finite-contacts',list(range(len(band))),finite_compute)
 # Contact flags retained for reviewed qualification, never intersection=>support.
 return dict(allExactLiteralCandidateFacets=literal,completeUnchangedOriginal3DFaces=len(original),completeUnchangedGeneratedJoinFaces=len(joins),allExactGeneratedBandFacets=band,allExactRetainedClippedCurrentFacets=retained,allGeneratedBandFacetRoles=roles,allRetainedCurrentFacetRoles=retroles,completeCurrentClipProof=clips,allExactAuthenticUpperEnvelopeBoundaryIntervals=inner,allExactRetainedCurrentOuterIntervals=outer,completeExactIntegratedAtoms=exact,completeActualFloat32ProductionIntegratedAtoms=actual,completeActualFloat32ProductionFaces=rendered,allNewBandFiniteOriginalAndJoinContacts=finite,sourceCrossingsAndSourceOpenBoundariesNotReclassified=True,terrainCandidateApproved=False)
