"""DRAFT Southside-only saved-source local core; no source decode/acceptance.
Exact 5m closed projection cells and a declared 5m one-cell analytic-distance collar.
UNEXECUTED v3: union containment avoids internal mask cuts; original facets
remain separate. Collar interpolation changes and all physical gates remain. Original
source layers are retained; original parent planes fill the exterior.
"""
from fractions import Fraction as F
import hashlib, math
import numpy as np
import southside_exact_private_terrain_adapter_v1_20261012 as old
MODES=('providerOriginal','actualLiteral','explicitLeftAssociatedF32ModelMatrix','explicitBalancedF32ModelMatrix')
STEP=F(5);WIDTH=F(5)
def points(t):return [tuple(F(v)for v in p)for p in t]
def normal(t):
 a,b,c=t;u=[b[k]-a[k]for k in range(3)];v=[c[k]-a[k]for k in range(3)]
 return (u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])
def bb(poly):return [min(p[0]for p in poly),min(p[2]for p in poly),max(p[0]for p in poly),max(p[2]for p in poly)]
def rect_planes(r):
 x0,z0,x1,z1=r;return [(F(1),F(0),-x0),(F(0),F(1),-z0),(-F(1),F(0),x1),(F(0),-F(1),z1)]
def tri_planes(t):
 p=[(v[0],v[2])for v in t];a=(p[1][0]-p[0][0])*(p[2][1]-p[0][1])-(p[1][1]-p[0][1])*(p[2][0]-p[0][0]);assert a
 if a<0:p.reverse()
 return [(-(b[1]-a[1]),b[0]-a[0],(b[1]-a[1])*a[0]-(b[0]-a[0])*a[1])for a,b in zip(p,p[1:]+p[:1])]
def split(poly,planes,axis):
 """Closed inside owns a surface lying wholly on a boundary; no skin duplication."""
 required=old.intrinsic_area(poly,axis);remaining=poly;outside=[]
 for plane in planes:
  if not remaining:break
  values=[plane[0]*p[0]+plane[1]*p[2]+plane[2]for p in remaining]
  if any(v<0 for v in values):
   part=old.clip(remaining,tuple(-v for v in plane))
   if old.intrinsic_area(part,axis):outside.append(part)
  remaining=old.clip(remaining,plane)
 assert required==sum((old.intrinsic_area(p,axis)for p in outside),F(0))+old.intrinsic_area(remaining,axis),'incomplete-exact-local-partition'
 return remaining,outside
def cell_rect(cell,domain):
 c,r=cell;x=F(domain[0])+c*STEP;z=F(domain[1])+r*STEP;return [x,z,x+STEP,z+STEP]
def rectangles(cells,domain):
 """Exact mask union in maximal equal row runs; no terrain facet simplification."""
 by={}
 for c,r in sorted(cells):by.setdefault(r,[]).append(c)
 runs=[]
 for r,cols in sorted(by.items()):
  start=previous=cols[0]
  for c in cols[1:]:
   if c!=previous+1:runs.append((start,previous+1,r,r+1));start=c
   previous=c
  runs.append((start,previous+1,r,r+1))
 active={};done=[]
 for r in sorted(by):
  current={(a,b):(a,b,y0,r+1)for a,b,y0,y1 in runs if y0==r}
  for key,v in list(active.items()):
   if key in current and v[3]==r:current[key]=(v[0],v[1],v[2],r+1)
   else:done.append(v)
  active=current
 done.extend(active.values())
 return [[F(domain[0])+a*STEP,F(domain[1])+c*STEP,F(domain[0])+b*STEP,F(domain[1])+d*STEP]for a,b,c,d in sorted(done)]
def bind_positions(worlds,captures):
 assert set(worlds)==set(captures)
 for uid,item in worlds.items():
  saved=captures[uid];proof=saved['completeOriginalPOSITIONProof'];index=np.asarray(saved['completeOriginalIndex'],dtype=np.int64)
  # Actual immutable Southside proof has zero unused vertices. Reject a changed
  # source with unaccounted unused vertices rather than substituting a bbox.
  assert proof['originalUnreferencedPositionVertices']==0 and proof['allOriginalPositionVerticesAccounted']is True
  assert set(index.tolist())==set(range(proof['completeOriginalPositionVertices']))
  assert set(item['completeWorldStreams'])==set(MODES)and item['sourceSHA256']==saved['sourceSHA256']
  for mode,stream in item['completeWorldStreams'].items():
   t=np.asarray(stream['completeWorldTriangles'],dtype='<f8');assert t.shape==(saved['completeFaces'],3,3)and np.isfinite(t).all()
   assert hashlib.sha256(t.tobytes()).hexdigest()==stream['completeWorldTriangleSHA256']
   if mode=='providerOriginal':assert stream['completeWorldTriangleSHA256']==proof['worldTrianglesSHA256']
   else:
    key={'actualLiteral':'completeLiteralWorldPosition','explicitLeftAssociatedF32ModelMatrix':'completeExplicitLeftAssociatedFloat32WorldPosition','explicitBalancedF32ModelMatrix':'completeExplicitBalancedFloat32WorldPosition'}[mode]
    v=np.asarray(saved[key],dtype='<f8').reshape(-1,3);assert len(v)==proof['completeOriginalPositionVertices']and np.isfinite(v).all()
    assert np.array_equal(t,v[index.reshape(-1,3)])
 return True
def mask(worlds,captures,domain):
 bind_positions(worlds,captures);x0,z0,x1,z1=map(F,domain);cols=(x1-x0)/STEP;rows=(z1-z0)/STEP;assert cols.denominator==rows.denominator==1
 cols,rows=int(cols),int(rows);core=set();records=[]
 for uid,item in sorted(worlds.items()):
  for mode in MODES:
   stream=item['completeWorldStreams'][mode]
   for face_id,t in enumerate(stream['completeWorldTriangles']):
    polygon=points(t);bounds=bb(polygon);assert x0<=bounds[0]<=bounds[2]<=x1 and z0<=bounds[1]<=bounds[3]<=z1
    found=[]
    for r in range(max(0,math.floor((bounds[1]-z0)/STEP)-1),min(rows-1,math.floor((bounds[3]-z0)/STEP))+1):
     for c in range(max(0,math.floor((bounds[0]-x0)/STEP)-1),min(cols-1,math.floor((bounds[2]-x0)/STEP))+1):
      cell=(c,r)
      if old.rect(polygon,cell_rect(cell,domain)):found.append(cell);core.add(cell)
    assert found,'complete-original-face-has-no-closed-core-cell'
    n=normal(polygon);records.append(dict(uid=uid,arithmetic=mode,sourceFace=face_id,sourceSHA256=item['sourceSHA256'],worldSHA256=stream['completeWorldTriangleSHA256'],wholeFacetSHA256=hashlib.sha256(np.asarray(t,dtype='<f8').tobytes()).hexdigest(),completeClosedIntersectingCoreCells=found,zero3DArea=not any(n),zeroXZArea=n[1]==0,qualification='Exact complete closed projection nomination, including vertical/zero cases; no root or grade credit'))
 assert core
 active={(c+dx,r+dz)for c,r in core for dx in range(-1,2)for dz in range(-1,2)}
 assert all(0<=c<cols and 0<=r<rows for c,r in active),'five-metre-collar-outside-existing-domain'
 collar=active-core
 boundary=[]
 for c,r in sorted(core):
  x0,z0,x1,z1=cell_rect((c,r),domain)
  for neighbor,edge in [((c,r-1),[(x0,z0),(x1,z0)]),((c+1,r),[(x1,z0),(x1,z1)]),((c,r+1),[(x1,z1),(x0,z1)]),((c-1,r),[(x0,z1),(x0,z0)])]:
   if neighbor not in core:boundary.append(dict(cell=[c,r],missingNeighbor=list(neighbor),exactOrientedXZEdge=[[str(v)for v in p]for p in edge]))
 return core,collar,dict(completeSourceFaceModeRecords=records,completeSourceFaceSlots=len(records),coreCells=sorted(core),collarCells=sorted(collar),completeCoreBoundaryEdgesIncludingEveryInteriorHole=boundary,allClosedProjectionsCovered=True,allPOSITIONVerticesIncludingUnusedBound=True,actualUnusedPositionVertices={u:captures[u]['completeOriginalPOSITIONProof']['originalUnreferencedPositionVertices']for u in captures},stepM=5,collarM=5,GEOSNotUsedForOmission=True,sourceGeometryChanges=0,physicalAccepted=False)
def alpha_at(x,z,core_rectangles):
 distance=min(max(F(0),r[0]-x,x-r[2],r[1]-z,z-r[3])for r in core_rectangles)
 return max(F(0),F(1)-distance/WIDTH)
def union_partition(poly,rects,axis):
 """Exact real-area accounting first; whole containment returns original poly.
 No original facets are combined. Closed boundaries retain vertical skins.
 """
 required=old.intrinsic_area(poly,axis);assert required
 remaining=[poly];inside_parts=[]
 for r in rects:
  following=[]
  for p in remaining:
   if not old.closed_xz_touch(bb(p),r):following.append(p);continue
   inside,outside=split(p,rect_planes(r),axis);following.extend(outside)
   if old.intrinsic_area(inside,axis):inside_parts.append(inside)
  remaining=following
 assert required==sum((old.intrinsic_area(p,axis)for p in inside_parts+remaining),F(0))
 if not remaining:return [poly],[],True
 return inside_parts,remaining,False
def affine_value(a,p):return a[0]*p[0]+a[1]*p[2]+a[2]
def rectangle_alpha_terms(r):
 x0,z0,x1,z1=r
 return [(F(1)/WIDTH,F(0),F(1)-x0/WIDTH),(-F(1)/WIDTH,F(0),F(1)+x1/WIDTH),(F(0),F(1)/WIDTH,F(1)-z0/WIDTH),(F(0),-F(1)/WIDTH,F(1)+z1/WIDTH),(F(0),F(0),F(1))]
def min_branch_partition(poly,terms,axis):
 parts=[]
 for i,a in enumerate(terms):
  part=poly
  for j,b in enumerate(terms):
   if i!=j:part=old.clip(part,tuple(b[k]-a[k]for k in range(3)))
   if not part:break
  if not old.intrinsic_area(part,axis):continue
  if any(j<i and all(affine_value(tuple(terms[j][k]-a[k]for k in range(3)),p)==0 for p in part)for j in range(len(terms))):continue
  parts.append((part,a,i))
 assert sum((old.intrinsic_area(p,axis)for p,_,_ in parts),F(0))==old.intrinsic_area(poly,axis),'incomplete-min-envelope-branches'
 return parts
def envelope_partition(poly,core_rects,axis):
 """Exact continuous alpha=max(0,max_rect min_affine), before packing.
 A losing rectangle leaves a whole existing region uncut. Positive regions
 retain deterministic exact ownership on vertical branch ties. Changed
 triangle interpolation is explicit; this is not the previous grid surface.
 """
 regions=[(poly,(F(0),F(0),F(0)),None)]
 for ri,r in enumerate(core_rects):
  expanded=[r[0]-WIDTH,r[1]-WIDTH,r[2]+WIDTH,r[3]+WIDTH]
  next_regions=[]
  for region,current,owner in regions:
   if not old.closed_xz_touch(bb(region),expanded):next_regions.append((region,current,owner));continue
   candidates=min_branch_partition(region,rectangle_alpha_terms(r),axis)
   replacements=[];improved=False
   for p,candidate,term in candidates:
    diff=tuple(candidate[k]-current[k]for k in range(3))
    # Entire tie owns the earlier region; never duplicate a vertical skin.
    if not any(affine_value(diff,v)>0 for v in p):replacements.append((p,current,owner));continue
    positive,negative=split(p,[diff],axis)
    for q in negative:replacements.append((q,current,owner))
    if old.intrinsic_area(positive,axis):replacements.append((positive,candidate,[ri,term]));improved=True
   if not improved:next_regions.append((region,current,owner))
   else:next_regions.extend(replacements)
  assert sum((old.intrinsic_area(p,axis)for p,_,_ in next_regions),F(0))==old.intrinsic_area(poly,axis)
  regions=next_regions
 for p,a,branch in regions:
  assert all(F(0)<=affine_value(a,v)<=F(1)for v in p)
  assert all(affine_value(a,v)==alpha_at(v[0],v[2],core_rects)for v in p),'incorrect-distance-envelope'
 return regions
def construction(saved_account,parent,old_patch,worlds,captures):
 assert saved_account['completeInputFacets']==774477 and old_patch['cell']==5 and saved_account['triangleBudget']==25000
 cells=old_patch['coarseCells'];g=old_patch['meta']['georef'];domain=[F(g['bE'])-old.ORIGIN[0],old.ORIGIN[1]-F(g['bN']),F(g['bE'])-old.ORIGIN[0]+(old_patch['w']-1)*STEP,old.ORIGIN[1]-F(g['bN'])+(old_patch['h']-1)*STEP]
 core,collar,mask_proof=mask(worlds,captures,domain);core_rects=rectangles(core,domain);active_rects=rectangles(core|collar,domain)
 parent_regions=[(i,t,bb(t))for i,t in enumerate(old.parent_faces(parent,cells))]
 output=[];lineage=[];partition=[];whole_core_outputs=[];parent_partition=[];collapsed=[];parent_packing=[];source_packing=[];zero_touch=[]
 for q in saved_account['completeSelectedOriginalFacetAccounts']:
  if q['sourceKind']not in ['exact-zero-area','domain-boundary-touch-only']:continue
  polygon=points(q.get('originalTriangle',q.get('exactClippedSourcePoints',[])));assert polygon
  met=[list(cell)for cell in sorted(core|collar)if old.rect(polygon,cell_rect(cell,domain))]
  zero_touch.append(dict(savedSourceRecordVerbatim=q,completeClosedLocalMaskContacts=met,renderHeightOrBridgeCredit=False))
 def emit(poly,classification,global_id=None,prior_output=None,parent_id=None,parent_plane=None,alpha_plane=None):
  for t in old.fan(poly):
   n=normal(t)
   if not any(n):continue
   before=[tuple(p)for p in t]
   if classification=='changed-local-collar':
    after=[]
    for p in t:
     a=affine_value(alpha_plane,p);assert 0<=a<=1
     after.append((p[0],a*p[1]+(1-a)*old.plane_height(parent_plane,p),p[2]))
   else:after=before
   packed=[[old.f32(v)for v in p]for p in after];k=len(output);output.append(packed)
   if not old.area_real(packed):collapsed.append(k)
   if classification=='retained-parent-exterior':
    deviations=[F(p[1])-old.plane_height(parent_plane,tuple(F(v)for v in p))for p in packed]
    if any(deviations):parent_packing.append(dict(outputFacet=k,exactPackedHeightPlaneResidualM=[str(v)for v in deviations]))
   elif classification=='source-core'and packed!=[[float(v)for v in p]for p in before]:source_packing.append(k)
   lineage.append(dict(outputFacet=k,classification=classification,globalOriginalFacetId=global_id,savedOriginalFragmentOutput=prior_output,parentFacet=parent_id,exactOriginalPoints=[[str(v)for v in p]for p in before],exactProposedPoints=[[str(v)for v in p]for p in after],packedZero3DArea=not old.area_real(packed),exactAlphaAffine=[str(v)for v in alpha_plane]if alpha_plane is not None else None))
 for q in saved_account['completeOutputFacetLineage']:
  polygon=points(q['exactOriginalSourceFragment']);n=normal(polygon);assert any(n);axis=max(range(3),key=lambda k:abs(n[k]));required=old.intrinsic_area(polygon,axis);remaining=[polygon];covered=F(0)
  bounds=bb(polygon)
  relevant_core=[r for r in core_rects if old.closed_xz_touch(bounds,r)]
  core_parts,remaining,whole_core=union_partition(polygon,relevant_core,axis)
  if whole_core:
   whole_core_outputs.append(q['outputFacet']);covered=required;emit(polygon,'source-core',q['globalOriginalFacetId'],q['outputFacet'])
  else:
   for inside in core_parts:
    covered+=old.intrinsic_area(inside,axis);emit(inside,'source-core',q['globalOriginalFacetId'],q['outputFacet'])
  collar_parts=[];outside_active=[]
  relevant_active=[r for r in active_rects if old.closed_xz_touch(bounds,r)]
  for p in remaining:
   inside,outside,_=union_partition(p,relevant_active,axis)
   collar_parts.extend(inside);outside_active.extend(outside)
  remaining=outside_active
  for collar_poly in collar_parts:
   pending=[collar_poly];parent_covered=F(0)
   for parent_id,parent_t,parent_bb in parent_regions:
    following=[]
    for p in pending:
     if not old.closed_xz_touch(bb(p),parent_bb):following.append(p);continue
     inside,outside=split(p,tri_planes(parent_t),axis);following.extend(outside)
     if not old.intrinsic_area(inside,axis):continue
     # Partition only at actual parent facet boundaries and genuine affine
     # distance-envelope branches; no arbitrary refined 5m triangle grid.
     for part,alpha,branch in envelope_partition(inside,core_rects,axis):
      area=old.intrinsic_area(part,axis);parent_covered+=area;covered+=area
      emit(part,'changed-local-collar',q['globalOriginalFacetId'],q['outputFacet'],parent_id=parent_id,parent_plane=parent_t,alpha_plane=alpha)
    pending=following
   assert not sum((old.intrinsic_area(p,axis)for p in pending),F(0)),'collar-outside-actual-parent-domain'
   assert parent_covered==old.intrinsic_area(collar_poly,axis)
  excluded=sum((old.intrinsic_area(p,axis)for p in remaining),F(0));assert covered+excluded==required
  partition.append(dict(savedFragmentOutput=q['outputFacet'],globalOriginalFacetId=q['globalOriginalFacetId'],exactWholeIntrinsicArea=str(required),exactLocalIncludedIntrinsicArea=str(covered),exactOutsideLocalSourceIntrinsicArea=str(excluded),outsideLocalSourceReason='Actual parent retained outside explicitly changed5m active union; every excluded original fragment remains in immutable inventory/lineage',completeExactOutsideLocalSourceFragments=[[[str(v)for v in vertex]for vertex in part]for part in remaining],wholeFragmentPartitionComplete=True))
 for parent_id,t in enumerate(old.parent_faces(parent,cells)):
  remaining=[list(t)];required=old.intrinsic_area(list(t),1);removed=F(0)
  for r in active_rects:
   next_remaining=[]
   for p in remaining:
    if not old.closed_xz_touch(bb(p),r):next_remaining.append(p);continue
    inside,outside=split(p,rect_planes(r),1);removed+=old.intrinsic_area(inside,1);next_remaining.extend(outside)
   remaining=next_remaining
  retained=sum((old.intrinsic_area(p,1)for p in remaining),F(0));assert required==removed+retained
  parent_partition.append(dict(parentFacet=parent_id,exactWholeOriginalParentTriangle=[[str(v)for v in vertex]for vertex in t],exactWholeProjectedArea=str(required),exactRemovedByActiveUnionArea=str(removed),exactRetainedExteriorArea=str(retained),completeExactRetainedParentFragments=[[[str(v)for v in vertex]for vertex in part]for part in remaining],wholeParentTrianglePartitionComplete=True))
  for p in remaining:emit(p,'retained-parent-exterior',parent_id=parent_id,parent_plane=t)
 step,w,h,nodes,raw,display,vegetation=old.refined_parent_grid(parent,cells,[float(v)for v in domain])
 patch=dict(id='government-native-southside-pair-source-local-private-v3',w=w,h=h,cell=float(step),elev=raw,renderedElev=display,vegetation=vegetation,coarseCells=cells,meta=dict(georef=dict(aE=float(step),aN=-float(step),bE=float(domain[0])+old.ORIGIN[0],bN=old.ORIGIN[1]-float(domain[1]),W=w,H=h),targetUids=['landsd/315025:0','landsd/300867:0']),nativeMesh=dict(position=[v for t in output for p in t for v in p],index=list(range(3*len(output))),source=dict(verticalDatum='HKPD',verticalScale=1,policy='Saved original layers in exact closed projection-cell core; explicitly changed5m one-cell analytic-distance vertex-interpolated collar; original parent-plane exterior; all physical qualification pending.')))
 account=dict(completeInputFacets=774477,completeInputSHA256=saved_account['completeInputSHA256'],savedFullSourceInventoryRequired=True,allOriginalZeroAndVerticalIdsRetainedVerbatim=dict(exactZeroOriginalFacetIds=saved_account['exactZeroOriginalFacetIds'],allVerticalRealOriginalFacetIds=saved_account['allVerticalRealOriginalFacetIds']),completeSelectedZeroAndTouchLocalMaskAccount=zero_touch,mask=mask_proof,coreRectangles=[[str(v)for v in r]for r in core_rects],activeRectangles=[[str(v)for v in r]for r in active_rects],completeSavedFragmentPartition=partition,wholeCoreOriginalFragmentsEmittedWithoutInternalMaskCuts=whole_core_outputs,completeParentExteriorPartition=parent_partition,completeOutputFacetLineage=lineage,realOutputFacetsCollapsedByFloat32=collapsed,parentExteriorPackingResiduals=parent_packing,sourceCorePackingChanges=source_packing,wholeAlteredDomainAllPackedAndUnusedGridBounds=old.bbox([*output,*[[[float(v)for v in p]]*3 for p in nodes]]),triangleBudget=25000,triangleBudgetPass=len(output)<=25000,outputFacets=len(output),sourceLayersNeverHeightFiltered=True,noGEOSSourceOmission=True,noSourceDecode=True,noSimplification=True,noOriginalFacetsMerged=True,internalCoreCutsAvoidedOnlyByExactUnionContainment=True,collarInterpolationChangedFromV1=True,collarWidthChangedFromV2M=[10,5],packedSurfaceEqualityToV2Claim=False,packedSurfaceEqualityToV1Claim=False,alphaPolicy='max over core rectangles of min(1, four outward-distance affine terms), clamped below at zero',completeFiniteSeamCoverageAndSamplerQualificationPending=True,sourceGeometryChanges=0,currentAcceptance=False,physicalAccepted=False,installationApproved=False)
 return patch,account
