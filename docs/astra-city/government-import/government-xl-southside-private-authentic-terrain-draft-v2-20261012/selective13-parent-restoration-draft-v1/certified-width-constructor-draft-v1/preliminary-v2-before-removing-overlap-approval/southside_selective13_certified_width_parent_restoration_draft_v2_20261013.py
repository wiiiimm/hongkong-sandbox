"""UNEXECUTED Southside-only local parent routing; no source decode/acceptance.
Preserve the saved v4 exterior and all original terrain lineage. The thirteen
core interiors route to actual parent once; every routed fragment is recorded.
"""
from fractions import Fraction as F
from collections import defaultdict
import copy,hashlib,struct
import numpy as np
from southside_saved_local_core_parent_adapter_v3_20261012 import old,normal,split,tri_planes,bb,affine_value
from southside_selective13_parent_retention_affine_collar_draft_v1_20261013 import _support_planes,_hull,partition_retention_alpha
from exact_original_projection_coverage_v2_20261010 import subtract,signed_area,cross

def literal_json_ready(value):
 """Exact rational strings at the output boundary; packed floats stay floats."""
 if isinstance(value,F):return str(value)
 if isinstance(value,dict):return {k:literal_json_ready(v)for k,v in value.items()}
 if isinstance(value,(list,tuple)):return [literal_json_ready(v)for v in value]
 return value

def alpha_terms(core,width):
 width=F(width);assert width>0
 return [(F(0),F(0),F(1))]+[(a/(width*(abs(a)+abs(b))),b/(width*(abs(a)+abs(b))),F(1)+d/(width*(abs(a)+abs(b))))for a,b,d in _support_planes(core)]

def proposed_point(p,kind,alpha,parent):
 a=affine_value(alpha,p);assert 0<=a<=1
 if kind=='unchanged-v4-exterior':return p
 y=old.plane_height(parent,p)
 return (p[0],y,p[2])if kind=='actual-parent-core-once'else(p[0],(1-a)*p[1]+a*y,p[2])

def prepare_branches(mask_certificate):
 c=mask_certificate['sourceBoundMaskCertificate'];width=F(c['exactDerivedUniformWidthM'])
 assert width==F(c['exactGlobalDistanceInfimumM'])/2 and c['all4784ClosedRegionsSeparatedFromPackedMask']
 branches=[]
 for r in c['completeClosedCoreMinkowskiMaskPrimitives']:
  core=[tuple(F(v)for v in p)for p in r['completeCoreHull']];outer=[tuple(F(v)for v in p)for p in r['completeExactClosedMinkowskiOuterHull']]
  assert outer==_hull([(x+dx,z+dz)for x,z in core for dx in [-width,width]for dz in [-width,width]])
  terms=alpha_terms(core,width)
  branches.append(dict(coreHull=core,closedOuterHull=outer,closedOuterBounds=[min(p[0]for p in outer),min(p[1]for p in outer),max(p[0]for p in outer),max(p[1]for p in outer)],alphaTerms=terms,completeOriginalDomainLineage=r['completeOriginalCoreDomainLineage']))
 assert len(branches)==831 and sum(len(r['completeOriginalDomainLineage'])for r in branches)==3653
 return branches,width

def rational_closed_coverage(points,triangles):
 """Existing exact subtract/interval/point rules, without rational-to-double loss."""
 p=_hull([tuple(F(v)for v in q)for q in points]);ts=[]
 for t in triangles:
  q=[(F(v[0]),F(v[2]))for v in t];a=signed_area(q)
  if a:ts.append(q if a>0 else list(reversed(q)))
 if signed_area(p):
  remaining=[p]
  for t in ts:
   remaining=[q for r in remaining for q in subtract(r,t)]
   if not remaining:break
  area=sum((abs(signed_area(r))for r in remaining),F(0))
  return dict(covered=area==0,kind='complete-closed-area',exactUncoveredAreaM2=str(area),completeUncoveredPolygons=remaining)
 if len(p)==1:return dict(covered=any(all(cross(a,b,p[0])>=0 for a,b in zip(t,t[1:]+t[:1]))for t in ts),kind='complete-closed-point')
 a,b=p[0],p[-1];intervals=[]
 for t in ts:
  lo,hi=F(0),F(1)
  for u,v in zip(t,t[1:]+t[:1]):
   start,end=cross(u,v,a),cross(u,v,b);delta=end-start
   if not delta:
    if start<0:lo,hi=F(1),F(0);break
   elif delta>0:lo=max(lo,-start/delta)
   else:hi=min(hi,-start/delta)
  if lo<=hi:intervals.append((lo,hi))
 reach=F(0);gaps=[]
 for lo,hi in sorted(intervals):
  if lo>reach:gaps.append((reach,lo))
  reach=max(reach,hi)
 if reach<1:gaps.append((reach,F(1)))
 return dict(covered=not gaps and reach>=1,kind='complete-closed-segment',exactIntervals=intervals,exactUncoveredIntervals=gaps)

def line_key(a,b):
 x,z=b[0]-a[0],b[2]-a[2]
 if not(x or z):return ('vertical',a[0],a[2])
 coefficients=(-z,x,z*a[0]-x*a[2]);pivot=next(v for v in coefficients if v)
 return ('xz-line',*[v/pivot for v in coefficients])

def conform_boundaries(records):
 """Propagate exact boundary knots; never combine facets or change source planes."""
 knots=defaultdict(set)
 for r in records:
  p=r['prePolygon']
  for a,b in zip(p,p[1:]+p[:1]):
   key=line_key(a,b)
   if key[0]=='vertical':knots[key].update([a[1],b[1]])
   else:knots[key].update([(a[0],a[2]),(b[0],b[2])])
 out=[]
 for r in records:
  # Preserve retained exterior partition polygons. Whole untouched prior
  # triangles keep their exact packed vertices/order; clipped exterior pieces
  # explicitly retain the prior source plane and record new packing residuals.
  if r['kind']=='unchanged-v4-exterior':
   out.append({**r,'originalPartitionPolygon':r['prePolygon'],'exteriorKnotsNotRetessellated':True});continue
  p=r['prePolygon'];ring=[]
  for a,b in zip(p,p[1:]+p[:1]):
   ring.append(a);key=line_key(a,b)
   if a==b:continue
   axis=1 if key[0]=='vertical'else 0 if a[0]!=b[0]else 2
   values=knots[key]if axis==1 else [q[0 if axis==0 else 1]for q in knots[key]]
   parameters=sorted({(v-a[axis])/(b[axis]-a[axis])for v in values if 0<(v-a[axis])/(b[axis]-a[axis])<1})
   ring.extend(tuple(a[k]+t*(b[k]-a[k])for k in range(3))for t in parameters)
  out.append({**r,'prePolygon':old.clean(ring),'originalPartitionPolygon':p})
 return out

def packed_vertex(p):
 result=[];errors=[];bits=[]
 for v in p:
  raw=struct.pack('<f',float(v));q=struct.unpack('<f',raw)[0];result.append(q);errors.append(abs(F(q)-v));bits.append(raw.hex())
 return result,errors,bits

def source_plane_correspondence(before,after,packed,kind):
 n=normal(before);d=sum(n[k]*before[0][k]for k in range(3));pre_residual=[sum(n[k]*p[k]for k in range(3))-d for p in after];packed_residual=[sum(n[k]*F(p[k])for k in range(3))-d for p in packed]
 if kind=='unchanged-v4-exterior':assert all(v==0 for v in pre_residual)
 return dict(exactPriorPlaneNormal=n,exactPriorPlaneConstant=d,exactProposedVertexPlaneResiduals=pre_residual,exactPackedVertexPlaneResiduals=packed_residual,exactUnchangedPlaneBeforePacking=kind=='unchanged-v4-exterior',transitionInteriorIsNewTriangulatedSurfaceNotAnalyticEquality=True)

def closed_inside(point,hull):return all(cross(a,b,point)>=0 for a,b in zip(hull,hull[1:]+hull[:1]))

def whole_edge_max_envelope(a,b,triangles):
 """Complete closed edge against actual packed facets; no source role inference.
 Renderer height-field determinant filter is retained explicitly, not a geometry
 omission: every source/candidate facet remains in the mesh/account.
 """
 a,b=tuple(map(F,a)),tuple(map(F,b));rows=[];filtered=[]
 for facet,t in triangles:
  t=[tuple(F(v)for v in p)for p in t];projection=[(p[0],p[2])for p in t]
  determinant=(t[1][2]-t[2][2])*(t[0][0]-t[2][0])+(t[2][0]-t[1][0])*(t[0][2]-t[2][2])
  if abs(float(determinant))<1e-10:filtered.append(facet);continue
  if signed_area(projection)<0:projection.reverse()
  lo,hi=F(0),F(1)
  for u,v in zip(projection,projection[1:]+projection[:1]):
   start,end=cross(u,v,(a[0],a[2])),cross(u,v,(b[0],b[2]));delta=end-start
   if not delta:
    if start<0:lo,hi=F(1),F(0);break
   elif delta>0:lo=max(lo,-start/delta)
   else:hi=min(hi,-start/delta)
  if lo>hi:continue
  h0,h1=old.plane_height(t,a),old.plane_height(t,b);rows.append(dict(facet=facet,lo=lo,hi=hi,height0=h0,slope=h1-h0))
 knots={F(0),F(1)}
 for r in rows:knots.update([r['lo'],r['hi']])
 for i,r in enumerate(rows):
  for s in rows[i+1:]:
   denominator=r['slope']-s['slope']
   if denominator:
    t=(s['height0']-r['height0'])/denominator
    if max(r['lo'],s['lo'])<=t<=min(r['hi'],s['hi']):knots.add(t)
 def at(t):
  candidates=[r for r in rows if r['lo']<=t<=r['hi']]
  if not candidates:return dict(parameter=t,covered=False)
  height=max(r['height0']+r['slope']*t for r in candidates);winners=[r for r in candidates if r['height0']+r['slope']*t==height]
  return dict(parameter=t,covered=True,exactHighestHeightM=height,completeHighestFacetTies=[r['facet']for r in winners],completeActiveFacetCount=len(candidates))
 ordered=sorted(knots);points=[at(t)for t in ordered];intervals=[dict(closedInterval=[lo,hi],interiorWitness=at((lo+hi)/2))for lo,hi in zip(ordered,ordered[1:])]
 return dict(completeProjectedFiniteFacetIntervals=rows,allOriginalClosedEndpointAndPlaneCrossoverKnots=points,allCompleteOpenIntervalMaximumBranches=intervals,allClosedEdgeCovered=all(p['covered']for p in points)and all(r['interiorWitness']['covered']for r in intervals),actualProductionHeightFieldFilteredFacetIDs=filtered,productionDeterminantFilter=1e-10,meshFacetsNotRemoved=True,noToleranceAdded=True)

def interface_runtime_probes(output,edge_inventory):
 """Exact closed AABB bins schedule only; all touches and layer ties retained."""
 triangles=[(i,[tuple(F(v)for v in p)for p in t])for i,t in enumerate(output)];bins=defaultdict(set);step=20
 for i,t in triangles:
  bounds=bb(t)
  for x in range(int(bounds[0]//step),int(bounds[2]//step)+1):
   for z in range(int(bounds[1]//step),int(bounds[3]//step)+1):bins[x,z].add(i)
 records=[];probes={}
 for edge_id,edge in enumerate(edge_inventory):
  if not any(r['kind']!='unchanged-v4-exterior'for r in edge['allIncidentRecords']):continue
  a,b=[tuple(F(v)for v in p)for p in edge['actualPackedEdge']];bounds=bb([a,b]);ids=set()
  for x in range(int(bounds[0]//step),int(bounds[2]//step)+1):
   for z in range(int(bounds[1]//step),int(bounds[3]//step)+1):ids.update(bins.get((x,z),set()))
  candidates=[triangles[i]for i in sorted(ids)if old.closed_xz_touch(bounds,bb(triangles[i][1]))];proof=whole_edge_max_envelope(a,b,candidates);records.append(dict(edgeInventoryID=edge_id,completeActualPackedEdge=[a,b],completeMaxHeightEnvelope=proof,allNominatedFacetIDs=[i for i,_ in candidates]))
  for point in [*proof['allOriginalClosedEndpointAndPlaneCrossoverKnots'],*[r['interiorWitness']for r in proof['allCompleteOpenIntervalMaximumBranches']]]:
   t=point['parameter'];xz=(a[0]+t*(b[0]-a[0]),a[2]+t*(b[2]-a[2]));probes.setdefault(xz,dict(exactXZ=xz,x=float(xz[0]),z=float(xz[1]),completeExactEnvelopeWitnesses=[]))['completeExactEnvelopeWitnesses'].append(dict(edgeInventoryID=edge_id,**point))
 return literal_json_ready(dict(completeNewInterfaceEdgeMAXEnvelopes=records,allClosedNewInterfacesHaveHeightFieldCoverage=all(r['completeMaxHeightEnvelope']['allClosedEdgeCovered']for r in records),runtimeProbes=list(probes.values()),runtimeSamplesAreNotUniversalFieldArithmeticProof=True))

def nominate_current_natives(domain,rows):
 assert len(rows)==len({r['uid']for r in rows})==6650
 fields={'providerOriginal':'originalWholeSourceBounds','actualLiteral':'completeLiteralBounds','explicitLeftAssociatedF32ModelMatrix':'completeLeftAssociatedF32Bounds','explicitBalancedF32ModelMatrix':'completeBalancedF32Bounds'};nominated=[];excluded=[]
 for r in rows:
  assert r['wholeUnusedPositionVerticesIncluded']and r['sourceFacesOmitted']==0 and r['completeOriginalPOSITIONProof']['allOriginalPositionVerticesAccounted']
  assert r['actualRenderMeshes']and all(m['wholePositionVerticesIncludingUnused']for m in r['actualRenderMeshes'])
  assert sum(m['completePositionVertices']for m in r['actualRenderMeshes'])==r['completePositionVertices']and sum(m['completeIndexedFaces']for m in r['actualRenderMeshes'])==r['completeFaces']
  gaps=[];touch=[]
  for mode,key in fields.items():
   b=r['completeOriginalPOSITIONProof'][key]if mode=='providerOriginal'else r[key]
   if mode!='providerOriginal':assert b==[[min(m[key][0][k]for m in r['actualRenderMeshes'])for k in range(3)],[max(m[key][1][k]for m in r['actualRenderMeshes'])for k in range(3)]]
   proof=None
   for axis in [0,2]:
    if F(domain[1][axis])<F(b[0][axis]):proof=dict(axis=axis,exactGapM=str(F(b[0][axis])-F(domain[1][axis])));break
    if F(b[1][axis])<F(domain[0][axis]):proof=dict(axis=axis,exactGapM=str(F(domain[0][axis])-F(b[1][axis])));break
   if proof is None:touch.append(mode)
   else:gaps.append(dict(arithmetic=mode,**proof))
  if touch:nominated.append(dict(uid=r['uid'],sourceSHA256=r['sourceSHA256'],touchingModes=touch,fullCurrentActorObligation=True))
  else:excluded.append(dict(uid=r['uid'],sourceSHA256=r['sourceSHA256'],allFourStrictBoundsGaps=gaps))
 return dict(completeActorsAccounted=6650,nominated=nominated,excluded=excluded,touchesRetained=True,nativeApprovalTransferred=False)

def construct(base_patch,base_account,parent,mask_certificate):
 assert base_account['outputFacets']==24580 and base_account['completeInputFacets']==774477 and base_account['triangleBudget']==25000
 vertices=np.asarray(base_patch['nativeMesh']['position'],dtype='<f4').astype('<f8').reshape(-1,3);indices=np.asarray(base_patch['nativeMesh']['index'],dtype=np.int64).reshape(-1,3);triangles=vertices[indices]
 assert len(triangles)==24580 and len(base_account['completeOutputFacetLineage'])==24580 and np.isfinite(vertices).all()
 assert set(indices.ravel())==set(range(len(vertices))),'unused candidate POSITION must remain explicitly accounted'
 branches,width=prepare_branches(mask_certificate);parents=[tuple(t)for t in old.parent_faces(parent,base_patch['coarseCells'])];records=[];partitions=[];descriptors=[]
 coverage=[dict(corePrimitive=i,completeClosedOuterProjectionProof=rational_closed_coverage(b['closedOuterHull'],parents))for i,b in enumerate(branches)]
 assert all(r['completeClosedOuterProjectionProof']['covered']for r in coverage),'certified collar leaves actual parent finite domain'
 for i,triangle in enumerate(triangles):
  polygon=[tuple(F(float(v))for v in p)for p in triangle];n=normal(polygon);lineage=base_account['completeOutputFacetLineage'][i];assert lineage['outputFacet']==i
  if not any(n):descriptors.append(dict(priorCandidateFacet=i,triangle=triangle.tolist(),fullPriorLineage=lineage,descriptorOnlyNoCoverageOrRootCredit=True));continue
  axis=max(range(3),key=lambda k:abs(n[k]));required=old.intrinsic_area(polygon,axis);routed=kept=changed=F(0);piece_records=[]
  for poly,alpha,owner in partition_retention_alpha(polygon,branches,axis):
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
  for poly,alpha,owner in partition_retention_alpha(list(pt),branches,1):
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
   assert r['owner']is not None;h=branches[r['owner'][0]]['closedOuterHull'];assert all(closed_inside((p[0],p[2]),h)for p in proposed),'new terrain leaves certified closed branch'
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
 patch=copy.deepcopy(base_patch);patch['id']='government-native-southside-selective13-certified-width-private-v1';patch['nativeMesh'].pop('sourceOverlap',None);patch['nativeMesh']['position']=[v for t in output for p in t for v in p];patch['nativeMesh']['index']=list(range(3*len(output)))
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
 account=dict(completeOriginalTerrainInventoryFacets=774477,completeOriginalInventorySHA256=base_account['completeInputSHA256'],allOriginalZeroAndVerticalIdsVerbatim=base_account['allOriginalZeroAndVerticalIdsRetainedVerbatim'],allPrior24580FacetPartitions=partitions,allPriorPackedCollapseDescriptors=descriptors,allFiniteParentCorePartitions=parent_partitions,completeOuterClosedParentCoverage=coverage,completeOriginal13BranchLineage=branches,exactCertifiedUniformWidthM=width,completeOutputFacetLineage=output_lineage,completeActualClippedAndInterpolatedPacking=packing,completeFallbackGridPackingIncludingUnused=grid_packing,exactMaxActualOutputAndGridXZPackingErrorM=max_xz_error,all4784FullTerrainPackingEnclosureCertificates=region_certificates,all4784PackedRestorationRegionsRemainSourceSeparated=all(r['strict']for r in region_certificates),completeNewInterfaceEdgeInventory=edges,completePreAndPackedProjectionCoverageDiagnosticsPending=True,completeProductionMAXSamplerAndExistingJoinGuardPending=True,unchangedExteriorNotGloballyRetessellated=True,clippedExteriorPackingIsExplicitChangedRepresentation=True,packedMaskSeparationDoesNotProveWholeTerrainHeightEquality=True,outputFacets=len(output),triangleBudget=25000,triangleBudgetPass=len(output)<=25000,packedCollapsedOutputFacetIDs=collapsed,wholeAlteredDomainAllActualAndUnusedBounds=bounds,all19RolesAndStationForeign34Independent=True,noSourceDecode=True,noOriginalBuildingGeometryOrPoseChanges=True,noOriginalTerrainLayersHeightFiltered=True,noCandidateFacetsMergedOrSimplified=True,currentAcceptance=False,physicalAccepted=False)
 return patch,literal_json_ready(account)


def projection_coverage_context(patch,account,mask_certificate):
 """Complete rational diagnostics, never a new zero-gap publication threshold."""
 p=np.asarray(patch['nativeMesh']['position'],dtype='<f4').astype('<f8').reshape(-1,3);ix=np.asarray(patch['nativeMesh']['index'],dtype=np.int64).reshape(-1,3);triangles=p[ix];bins=defaultdict(set);step=20
 for i,t in enumerate(triangles):
  b=bb(t)
  for x in range(int(b[0]//step),int(b[2]//step)+1):
   for z in range(int(b[1]//step),int(b[3]//step)+1):bins[x,z].add(i)
 proofs=[]
 for i,r in enumerate(mask_certificate['sourceBoundMaskCertificate']['completeClosedCoreMinkowskiMaskPrimitives']):
  for kind,key in [('closed-core','completeCoreHull'),('closed-outer-collar','completeExactClosedMinkowskiOuterHull')]:
   hull=[tuple(F(v)for v in q)for q in r[key]];b=[min(q[0]for q in hull),min(q[1]for q in hull),max(q[0]for q in hull),max(q[1]for q in hull)];ids=set()
   for x in range(int(b[0]//step),int(b[2]//step)+1):
    for z in range(int(b[1]//step),int(b[3]//step)+1):ids.update(bins.get((x,z),set()))
   nominated=[j for j in sorted(ids)if old.closed_xz_touch(b,bb(triangles[j]))];proofs.append(dict(corePrimitive=i,kind=kind,completeNominatedPackedFacets=nominated,exactClosedProjectionCoverage=rational_closed_coverage(hull,[triangles[j]for j in nominated])))
 return literal_json_ready(dict(completeCoreAndOuterPackedCoverageDiagnostics=proofs,completeAreaSegmentPointCasesRetained=True,allExactClosedMasksCovered=all(r['exactClosedProjectionCoverage']['covered']for r in proofs),diagnosticOnlyNoNewExactZeroGapGuard=True,existingOrdinaryValidatorToleranceUnchanged=True))
