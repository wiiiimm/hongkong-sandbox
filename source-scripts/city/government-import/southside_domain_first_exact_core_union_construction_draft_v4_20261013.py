"""UNEXECUTED acquisition partition draft, never existing terrain consolidation.
Original source/parent facets stay separate; only mask-internal boundaries are
excluded before original-facet partitioning. Changed triangulation is explicit.
"""
from fractions import Fraction as F
from collections import defaultdict
import copy,struct
import numpy as np
import southside_selective13_certified_width_parent_restoration_draft_v2_20261013 as reviewed
from southside_selective13_parent_retention_affine_collar_draft_v1_20261013 import _hull,_support_planes,alpha_at
from southside_saved_local_core_parent_adapter_v3_20261012 import old,normal,split,tri_planes,bb,affine_value,min_branch_partition
from exact_original_projection_coverage_v2_20261010 import signed_area,cross
from southside_selective13_certified_width_parent_restoration_draft_v2_20261013 import prepare_branches,rational_closed_coverage,conform_boundaries,proposed_point,packed_vertex,source_plane_correspondence,closed_inside,literal_json_ready,nominate_current_natives,interface_runtime_probes,projection_coverage_context

def parameter(a,b,p):
 axis=0 if a[0]!=b[0]else 1;assert a!=b
 return (p[axis]-a[axis])/(b[axis]-a[axis])
def on_segment(a,b,p):return cross(a,b,p)==0 and min(a[0],b[0])<=p[0]<=max(a[0],b[0])and min(a[1],b[1])<=p[1]<=max(a[1],b[1])
def intersection_knots(a,b,c,d):
 """All closed intersections, collinear endpoints included, exact fractions."""
 u=(b[0]-a[0],b[1]-a[1]);v=(d[0]-c[0],d[1]-c[1]);den=u[0]*v[1]-u[1]*v[0]
 if den:
  t=((c[0]-a[0])*v[1]-(c[1]-a[1])*v[0])/den;s=((c[0]-a[0])*u[1]-(c[1]-a[1])*u[0])/den
  return [(a[0]+t*u[0],a[1]+t*u[1])]if 0<=t<=1 and 0<=s<=1 else []
 return sorted({p for p in [a,b,c,d]if on_segment(a,b,p)and on_segment(c,d,p)})
def contains_closed(p,hull):
 if not hull:return False
 if len(hull)==1:return p==hull[0]
 if len(hull)==2:return on_segment(hull[0],hull[1],p)
 return all(cross(a,b,p)>=0 for a,b in zip(hull,hull[1:]+hull[:1]))
def closed_segment_union_coverage(a,b,hulls):
 """Exact closed interval union; endpoints alone never certify a segment."""
 if a==b:return dict(covered=any(contains_closed(a,h)for h in hulls),completePoint=a,completeIntervals=[])
 intervals=[]
 for owner,h in enumerate(hulls):
  if not h:continue
  if len(h)==1:
   if on_segment(a,b,h[0]):t=parameter(a,b,h[0]);intervals.append((t,t,owner))
   continue
  if len(h)==2:
   knots=intersection_knots(a,b,h[0],h[1])
   if knots:
    ts=sorted(parameter(a,b,p)for p in knots);intervals.append((ts[0],ts[-1],owner))
   continue
  lo,hi=F(0),F(1)
  for u,v in zip(h,h[1:]+h[:1]):
   start,end=cross(u,v,a),cross(u,v,b);delta=end-start
   if not delta:
    if start<0:lo,hi=F(1),F(0);break
   elif delta>0:lo=max(lo,-start/delta)
   else:hi=min(hi,-start/delta)
  if lo<=hi:intervals.append((lo,hi,owner))
 intervals.sort();end=F(0);covered=bool(intervals)and intervals[0][0]==0
 if covered:
  for lo,hi,_ in intervals:
   if lo>end:covered=False;break
   end=max(end,hi)
  covered=covered and end==1
 return dict(covered=covered,completeOriginalSegment=[a,b],completeIntervals=[dict(lo=lo,hi=hi,originalCorePrimitive=owner)for lo,hi,owner in intervals],lastCoveredParameter=end)

def directional_inside(p,direction,hull):
 """Exact symbolic one-sided membership; no finite epsilon or sampled mask fit."""
 assert len(hull)>=3 and signed_area(hull)>0
 for a,b in zip(hull,hull[1:]+hull[:1]):
  value=cross(a,b,p);derivative=(b[0]-a[0])*direction[1]-(b[1]-a[1])*direction[0]
  if value<0 or value==0 and derivative<0:return False
 return True

def exact_core_union_boundary(branches):
 assert branches;hulls=[_hull(r['coreHull'])for r in branches];area=[h for h in hulls if len(h)>=3 and signed_area(h)>0];segments=[]
 for owner,h in enumerate(hulls):
  if len(h)<3:continue
  for edge,(a,b)in enumerate(zip(h,h[1:]+h[:1])):segments.append((owner,edge,a,b))
 result={};internal=[]
 for owner,edge,a,b in segments:
  knots={a,b}
  for _,_,c,d in segments:knots.update(intersection_knots(a,b,c,d))
  ordered=sorted(knots,key=lambda p:parameter(a,b,p))
  for u,v in zip(ordered,ordered[1:]):
   if u==v:continue
   mid=((u[0]+v[0])/2,(u[1]+v[1])/2);left=(-(v[1]-u[1]),v[0]-u[0]);right=(-left[0],-left[1]);li=any(directional_inside(mid,left,h)for h in area);ri=any(directional_inside(mid,right,h)for h in area)
   account=dict(originalCorePrimitive=owner,originalPrimitiveEdge=edge,completeClosedSegment=[u,v],leftInsideUnion=li,rightInsideUnion=ri)
   if li==ri:internal.append(account);continue
   if not li:u,v=v,u
   key=tuple(sorted((u,v)));r=result.setdefault(key,dict(completeClosedSegment=[u,v],completeOriginalEdgeLineages=[]));assert r['completeClosedSegment']==[u,v];r['completeOriginalEdgeLineages'].append(account)
 return dict(completeCoreHulls=hulls,completeTrueAreaUnionBoundary=[result[k]for k in sorted(result)],excludedInternalMaskEdgesNotTerrainFacets=internal,completeLowerDimensionalPrimitives=[dict(originalCorePrimitive=i,completeClosedPoints=h)for i,h in enumerate(hulls)if len(h)<3],originalMaskPrimitiveCount=len(branches),maskGeometryNotSimplified=True,noTerrainFacetsCombined=True)

def segment_touches_projection(a,b,poly):
 h=_hull([(p[0],p[2])for p in poly])
 if len(h)==1:return on_segment(a,b,h[0])
 if len(h)==2:return bool(intersection_knots(a,b,h[0],h[1]))
 lo,hi=F(0),F(1)
 for u,v in zip(h,h[1:]+h[:1]):
  start,end=cross(u,v,a),cross(u,v,b);delta=end-start
  if not delta:
   if start<0:return False
  elif delta>0:lo=max(lo,-start/delta)
  else:hi=min(hi,-start/delta)
 return lo<=hi

def partition_complete_core_union(poly,axis,union):
 """Partition each original surface independently at actual closed mask edges."""
 regions=[poly]
 for row in union['completeTrueAreaUnionBoundary']:
  a,b=row['completeClosedSegment'];plane=(-(b[1]-a[1]),b[0]-a[0],(b[1]-a[1])*a[0]-(b[0]-a[0])*a[1]);following=[]
  for p in regions:
   if not segment_touches_projection(a,b,p):following.append(p);continue
   inside,outside=split(p,[plane],axis);following.extend(outside)
   if old.intrinsic_area(inside,axis):following.append(inside)
  assert sum((old.intrinsic_area(q,axis)for q in following),F(0))==old.intrinsic_area(poly,axis);regions=following
 out=[]
 for p in regions:
  centre=(sum(v[0]for v in p)/len(p),sum(v[2]for v in p)/len(p));inside=any(contains_closed(centre,h)for h in union['completeCoreHulls'])
  if inside:
   # Full closed coverage, not centre-only membership, qualifies the core piece.
   triangles=[]
   for h in union['completeCoreHulls']:
    if len(h)>=3:
     triangles.extend([[(q[0],F(0),q[1])for q in [h[0],h[i],h[i+1]]]for i in range(1,len(h)-1)])
   projected=[(v[0],v[2])for v in p]
   if signed_area(_hull(projected)):assert rational_closed_coverage(projected,triangles)['covered'],'new-core-piece-not-whole-union-covered'
   else:
    h=_hull(projected);assert h
    coverage=closed_segment_union_coverage(h[0],h[-1],union['completeCoreHulls'])
    assert coverage['covered'],'lower-dimensional-core-piece-not-closed-covered'
  out.append((p,inside))
 return out

def domain_first_partition(poly,branches,axis,union):
 """Max/min unchanged; only true core/outer domain boundaries scheduled first."""
 result=[]
 for source_part,inside_core in partition_complete_core_union(poly,axis,union):
  if inside_core:result.append((source_part,(F(0),F(0),F(1)),[-1,-1]));continue
  regions=[(source_part,(F(0),F(0),F(0)),None)]
  for i,r in enumerate(branches):
   following=[]
   for p,current,owner in regions:
    if not old.closed_xz_touch(bb(p),r['closedOuterBounds']):following.append((p,current,owner));continue
    inside,outside=split(p,_support_planes(r['closedOuterHull']),axis);following.extend((q,current,owner)for q in outside)
    if not old.intrinsic_area(inside,axis):continue
    replacement=[];improved=False
    for part,candidate,term in min_branch_partition(inside,r['alphaTerms'],axis):
     delta=tuple(candidate[k]-current[k]for k in range(3))
     if not any(affine_value(delta,v)>0 for v in part):replacement.append((part,current,owner));continue
     positive,negative=split(part,[delta],axis);replacement.extend((q,current,owner)for q in negative)
     if old.intrinsic_area(positive,axis):replacement.append((positive,candidate,[i,term]));improved=True
    following.extend(replacement if improved else [(inside,current,owner)])
   assert sum((old.intrinsic_area(q,axis)for q,_,_ in following),F(0))==old.intrinsic_area(source_part,axis);regions=following
  result.extend(regions)
 assert sum((old.intrinsic_area(q,axis)for q,_,_ in result),F(0))==old.intrinsic_area(poly,axis)
 for q,a,owner in result:assert all(0<=affine_value(a,v)<=1 and affine_value(a,v)==alpha_at(v[0],v[2],branches)for v in q)
 return result
def construct(base_patch,base_account,parent,mask_certificate):
 assert base_account['outputFacets']==24580 and base_account['completeInputFacets']==774477 and base_account['triangleBudget']==25000
 vertices=np.asarray(base_patch['nativeMesh']['position'],dtype='<f4').astype('<f8').reshape(-1,3);indices=np.asarray(base_patch['nativeMesh']['index'],dtype=np.int64).reshape(-1,3);triangles=vertices[indices]
 assert len(triangles)==24580 and len(base_account['completeOutputFacetLineage'])==24580 and np.isfinite(vertices).all()
 assert set(indices.ravel())==set(range(len(vertices))),'unused candidate POSITION must remain explicitly accounted'
 branches,width=prepare_branches(mask_certificate);core_union=exact_core_union_boundary(branches);parents=[tuple(t)for t in old.parent_faces(parent,base_patch['coarseCells'])];records=[];partitions=[];descriptors=[]
 coverage=[dict(corePrimitive=i,completeClosedOuterProjectionProof=rational_closed_coverage(b['closedOuterHull'],parents))for i,b in enumerate(branches)]
 assert all(r['completeClosedOuterProjectionProof']['covered']for r in coverage),'certified collar leaves actual parent finite domain'
 for i,triangle in enumerate(triangles):
  polygon=[tuple(F(float(v))for v in p)for p in triangle];n=normal(polygon);lineage=base_account['completeOutputFacetLineage'][i];assert lineage['outputFacet']==i
  if not any(n):descriptors.append(dict(priorCandidateFacet=i,triangle=triangle.tolist(),fullPriorLineage=lineage,descriptorOnlyNoCoverageOrRootCredit=True));continue
  axis=max(range(3),key=lambda k:abs(n[k]));required=old.intrinsic_area(polygon,axis);routed=kept=changed=F(0);piece_records=[]
  for poly,alpha,owner in domain_first_partition(polygon,branches,axis,core_union):
   area=old.intrinsic_area(poly,axis);values=[affine_value(alpha,p)for p in poly]
   if all(v==1 for v in values):routed+=area;piece_records.append(dict(kind='routed-to-actual-parent-core-once',prePolygon=poly,alpha=alpha,owner=owner));continue
   if not any(values):
    kept+=area;records.append(dict(kind='unchanged-v4-exterior',priorCandidateFacet=i,fullPriorLineage=lineage,prePolygon=poly,alpha=alpha,owner=owner,parentFacet=None));piece_records.append(dict(kind='unchanged-v4-exterior',prePolygon=poly));continue
   pending=[poly]
   for parent_id,pt in enumerate(parents):
    following=[]
    for p in pending:
     if not old.closed_xz_touch(bb(p),bb(pt)):following.append(p);continue
     cut,outside=split(p,tri_planes(pt),axis);following.extend(outside)
     if old.intrinsic_area(cut,axis):
      changed+=old.intrinsic_area(cut,axis);records.append(dict(kind='changed-certified-width-parent-transition',priorCandidateFacet=i,fullPriorLineage=lineage,prePolygon=cut,alpha=alpha,owner=owner,parentFacet=parent_id));piece_records.append(dict(kind='changed-certified-width-parent-transition',prePolygon=cut,alpha=alpha,owner=owner,parentFacet=parent_id))
    pending=following
   assert not sum((old.intrinsic_area(p,axis)for p in pending),F(0)),'transition has no finite parent coverage'
  assert routed+kept+changed==required
  partitions.append(dict(priorCandidateFacet=i,fullPriorLineage=lineage,exactWholeIntrinsicAreaM2=required,exactRoutedToParentCoreAreaM2=routed,exactUnchangedExteriorAreaM2=kept,exactChangedTransitionAreaM2=changed,completePartitionPieces=piece_records))
 parent_partitions=[]
 for parent_id,pt in enumerate(parents):
  required=old.intrinsic_area(pt,1);core_area=F(0);remaining_area=F(0);pieces=[]
  for poly,alpha,owner in domain_first_partition(list(pt),branches,1,core_union):
   area=old.intrinsic_area(poly,1)
   if all(affine_value(alpha,p)==1 for p in poly):
    core_area+=area;records.append(dict(kind='actual-parent-core-once',priorCandidateFacet=None,prePolygon=poly,alpha=alpha,owner=owner,parentFacet=parent_id));pieces.append(poly)
   else:remaining_area+=area
  assert core_area+remaining_area==required;parent_partitions.append(dict(parentFacet=parent_id,originalWholeParentTriangle=pt,exactWholeAreaM2=required,exactCoreAreaM2=core_area,exactUnemittedExteriorAreaM2=remaining_area,completeCorePolygons=pieces))
 records=conform_boundaries(records);output=[];output_lineage=[];collapsed=[];packing=[];max_xz_error=F(0);seams=defaultdict(list)
 for ri,r in enumerate(records):
  pre=r['prePolygon'];proposed=[]
  for p in pre:
   proposed.append(proposed_point(p,r['kind'],r['alpha'],parents[r['parentFacet']]if r['parentFacet']is not None else None))
  if r['kind']!='unchanged-v4-exterior':
   assert r['owner']is not None;h=branches[r['owner'][0]]['closedOuterHull']if r['owner'][0]>=0 else None;assert h is None or all(closed_inside((p[0],p[2]),h)for p in proposed),'new terrain leaves certified closed branch'
  for j in range(1,len(pre)-1):
   ids=[0,j,j+1];before=[pre[k]for k in ids];after=[proposed[k]for k in ids];packed=[];errors=[];bits=[]
   for p in after:
    value,error,raw=packed_vertex(p);packed.append(value);errors.append(error);bits.append(raw);max_xz_error=max(max_xz_error,error[0],error[2])
   index=len(output);output.append(packed)
   if not old.area_real(packed):collapsed.append(index)
   output_lineage.append(dict(outputFacet=index,kind=r['kind'],priorCandidateFacet=r['priorCandidateFacet'],fullPriorLineage=r.get('fullPriorLineage'),parentFacet=r['parentFacet'],exactPrePoints=before,exactProposedPoints=after,exactAlphaPlane=r['alpha'],maskOwner=r['owner'],priorPackedPlaneCorrespondence=source_plane_correspondence(before,after,packed,r['kind']),unchangedWholePriorTriangleBytes=r['kind']=='unchanged-v4-exterior' and before==[tuple(F(float(v))for v in p)for p in triangles[r['priorCandidateFacet']]]))
   packing.append(dict(outputFacet=index,actualFloat32BytesLE=bits,exactAxisDisplacementsM=errors))
  # Only new core/transition interfaces are classified here. Inherited source
  # layer/open boundaries remain verbatim context, not a new all-edges-closed gate.
  for k,(a,b)in enumerate(zip(proposed,proposed[1:]+proposed[:1])):
   va,vb=affine_value(r['alpha'],pre[k]),affine_value(r['alpha'],pre[(k+1)%len(pre)])
   if va==vb and va in [0,1]:
    pa,pb=packed_vertex(a)[0],packed_vertex(b)[0];key=tuple(sorted([tuple(pa),tuple(pb)]));seams[key].append(dict(record=ri,kind=r['kind'],alpha=va,parentFacet=r['parentFacet'],priorCandidateFacet=r['priorCandidateFacet']))
 for d in descriptors:
  index=len(output);output.append(d['triangle']);collapsed.append(index);output_lineage.append(dict(outputFacet=index,kind='unchanged-prior-packed-collapse-descriptor',priorCandidateFacet=d['priorCandidateFacet'],fullPriorLineage=d['fullPriorLineage'],noSurfaceCoverageOrRootCredit=True))
 patch=copy.deepcopy(base_patch);patch['id']='government-native-southside-selective13-domain-first-private-draft-v3';inherited_approval_metadata=dict(sourceOverlap=patch['nativeMesh'].pop('sourceOverlap',None),numericalProjectionOverlap=patch['nativeMesh']['source'].pop('numericalProjectionOverlap',None),numericalCoverageGap=patch['nativeMesh']['source'].pop('numericalCoverageGap',None));patch['nativeMesh']['position']=[v for t in output for p in t for v in p];patch['nativeMesh']['index']=list(range(3*len(output)))
 patch['nativeMesh']['source']['policy']='Saved v4 authentic layers outside exact thirteen-form restoration; actual parent in closed core; new exact certified-width transition. No source-building geometry or pose changes.'
 g=patch['meta']['georef'];grid=[(F(g['bE'])+c*F(g['aE'])-old.ORIGIN[0],old.rendered_height(patch,r*patch['w']+c),old.ORIGIN[1]-F(g['bN'])-r*F(g['aN']))for r in range(patch['h'])for c in range(patch['w'])]
 grid_packing=[dict(position=i,actualFloat32BytesLE=packed_vertex(p)[2],exactAxisDisplacementsM=packed_vertex(p)[1])for i,p in enumerate(grid)]
 for row in grid_packing:max_xz_error=max(max_xz_error,row['exactAxisDisplacementsM'][0],row['exactAxisDisplacementsM'][2])
 region_certificates=[]
 for row in mask_certificate['sourceBoundMaskCertificate']['all8SourceWorldRows']:
  for r in row['completeRegionCertificates']:
   d=F(r['certificate']['exactSavedNegativeRegionToWholeCoreDistanceM']);margin=d-width-max_xz_error;region_certificates.append(dict(uid=row['uid'],arithmetic=row['arithmetic'],sourceFace=r['sourceFace'],savedPieceID=r['savedPieceID'],exactFullTerrainPackingSeparationLowerBoundM=margin,strict=margin>0,originalSavedDistanceM=d))
 assert len(region_certificates)==4784
 bounds=old.bbox([*output,*[[[float(v)for v in p]]*3 for p in grid]])
 edges=[dict(actualPackedEdge=list(k),allIncidentRecords=v,hasExactPositiveLengthCounterpart=len(v)>1 and k[0]!=k[1])for k,v in seams.items()]
 account=dict(domainFirstExactClosedUnionBoundary=core_union,corePlaneAndSourceExteriorCorrespondenceRetained=True,changedTriangulationNotClaimedEqualToPriorCandidate=True,inheritedPriorApprovalMetadataHistoricalOnly=inherited_approval_metadata,noOverlapOrCoverageApprovalTransferred=True,completeOriginalTerrainInventoryFacets=774477,completeOriginalInventorySHA256=base_account['completeInputSHA256'],allOriginalZeroAndVerticalIdsVerbatim=base_account['allOriginalZeroAndVerticalIdsRetainedVerbatim'],allPrior24580FacetPartitions=partitions,allPriorPackedCollapseDescriptors=descriptors,allFiniteParentCorePartitions=parent_partitions,completeOuterClosedParentCoverage=coverage,completeOriginal13BranchLineage=branches,exactCertifiedUniformWidthM=width,completeOutputFacetLineage=output_lineage,completeActualClippedAndInterpolatedPacking=packing,completeFallbackGridPackingIncludingUnused=grid_packing,exactMaxActualOutputAndGridXZPackingErrorM=max_xz_error,all4784FullTerrainPackingEnclosureCertificates=region_certificates,all4784PackedRestorationRegionsRemainSourceSeparated=all(r['strict']for r in region_certificates),completeNewInterfaceEdgeInventory=edges,completePreAndPackedProjectionCoverageDiagnosticsPending=True,completeProductionMAXSamplerAndExistingJoinGuardPending=True,unchangedExteriorNotGloballyRetessellated=True,clippedExteriorPackingIsExplicitChangedRepresentation=True,packedMaskSeparationDoesNotProveWholeTerrainHeightEquality=True,outputFacets=len(output),triangleBudget=25000,triangleBudgetPass=len(output)<=25000,packedCollapsedOutputFacetIDs=collapsed,wholeAlteredDomainAllActualAndUnusedBounds=bounds,all19RolesAndStationForeign34Independent=True,noSourceDecode=True,noOriginalBuildingGeometryOrPoseChanges=True,noOriginalTerrainLayersHeightFiltered=True,noCandidateFacetsMergedOrSimplified=True,currentAcceptance=False,physicalAccepted=False)
 return patch,literal_json_ready(account)

