"""UNEXECUTED PolyU-only source-layer core and explicitly changed5m collar.
No simplification, normal filter, automatic overlap approval or acceptance.
Uses previously reviewed exact split/analytic-alpha primitives; all gates pending.
"""
from fractions import Fraction as F
import hashlib
import numpy as np
import southside_saved_local_core_parent_adapter_v3_20261012 as exact
old=exact.old
WIDTH=F(5)
def bounds_core(bounds):
 q=np.asarray(bounds,dtype='<f8');assert q.shape==(4,2,3)and np.isfinite(q).all()and np.all(q[:,0,:]<=q[:,1,:])
 return [F(float(q[:,0,0].min())),F(float(q[:,0,2].min())),F(float(q[:,1,0].max())),F(float(q[:,1,2].max()))]
def expanded(core):
 assert len(core)==4 and core[0]<core[2]and core[1]<core[3]
 return [core[0]-WIDTH,core[1]-WIDTH,core[2]+WIDTH,core[3]+WIDTH]
def construct(selected,original_ids,core,parent_triangles,*,expected_sha256,declared_source_faces):
 source=np.asarray(selected,dtype='<f8');assert source.ndim==3 and source.shape[1:]==(3,3)and np.isfinite(source).all()and len(source)==len(original_ids)
 assert hashlib.sha256(source.tobytes()).hexdigest()==expected_sha256
 assert original_ids==sorted(set(original_ids))and all(type(i)is int and 0<=i<declared_source_faces for i in original_ids)
 assert exact.WIDTH==WIDTH==5;core=list(map(F,core));active=expanded(core);parents=[exact.points(t)for t in parent_triangles];assert parents and all(exact.normal(t)[1]for t in parents)
 pb=[min(p[0]for t in parents for p in t),min(p[2]for t in parents for p in t),max(p[0]for t in parents for p in t),max(p[2]for t in parents for p in t)]
 assert pb[0]<=active[0]<active[2]<=pb[2]and pb[1]<=active[1]<active[3]<=pb[3],'proposed-collar-outside-captured-parent'
 output=[];lineage=[];source_accounts=[];parent_accounts=[];collapsed=[]
 def emit(poly,kind,global_id=None,parent_id=None,alpha=None,parent_plane=None):
  for tri in old.fan(poly):
   proposed=[]
   for p in tri:
    if kind=='changed-five-metre-collar':
     a=exact.affine_value(alpha,p);assert 0<=a<=1;p=(p[0],a*p[1]+(1-a)*old.plane_height(parent_plane,p),p[2])
    proposed.append(p)
   packed=[[old.f32(v)for v in p]for p in proposed];index=len(output);output.append(packed);n=exact.normal([tuple(F(v)for v in p)for p in packed])
   if not any(n):collapsed.append(index)
   lineage.append(dict(outputFacet=index,classification=kind,globalOriginalTerrainFacet=global_id,capturedParentFacet=parent_id,exactOriginalPoints=[[str(v)for v in p]for p in tri],exactProposedPoints=[[str(v)for v in p]for p in proposed],actualPackedPoints=packed,packed3DCollapse=not any(n),packedVerticalProjection=n[1]==0,exactAlphaAffine=[str(v)for v in alpha]if alpha is not None else None,parentPlanePackingResidualM=[str(F(p[1])-old.plane_height(parent_plane,tuple(F(v)for v in p)))for p in packed]if parent_plane is not None else None,noHeightLayerDeleted=True))
 for global_id,tri in zip(original_ids,source):
  polygon=exact.points(tri);n=exact.normal(polygon);bound=exact.bb(polygon)
  if not any(n):
   met=bool(old.rect(polygon,active));source_accounts.append(dict(globalOriginalTerrainFacet=global_id,exactZeroOriginalTriangle=[[str(v)for v in p]for p in polygon],closedActiveContact=met,noHeightOrBridgeCredit=True))
   if met:emit(polygon,'original-source-degenerate',global_id=global_id)
   continue
  axis=max(range(3),key=lambda k:abs(n[k]));required=old.intrinsic_area(polygon,axis);inside,not_core=exact.split(polygon,exact.rect_planes(core),axis);included=F(0);outside=[]
  if old.intrinsic_area(inside,axis):
   assert all(sum(n[k]*(p[k]-polygon[0][k])for k in range(3))==0 for p in inside),'original-core-plane-changed'
   emit(inside,'original-source-core',global_id=global_id);included+=old.intrinsic_area(inside,axis)
  for p in not_core:
   collar,rest=exact.split(p,exact.rect_planes(active),axis);outside.extend(rest)
   if not old.intrinsic_area(collar,axis):continue
   pending=[collar];covered=F(0)
   for parent_id,t in enumerate(parents):
    following=[]
    for fragment in pending:
     if not old.closed_xz_touch(exact.bb(fragment),exact.bb(t)):following.append(fragment);continue
     hit,remainder=exact.split(fragment,exact.tri_planes(t),axis);following.extend(remainder)
     if not old.intrinsic_area(hit,axis):continue
     for part,alpha,branch in exact.envelope_partition(hit,[core],axis):
      area=old.intrinsic_area(part,axis);covered+=area;emit(part,'changed-five-metre-collar',global_id=global_id,parent_id=parent_id,alpha=alpha,parent_plane=t)
    pending=following
   assert sum((old.intrinsic_area(p,axis)for p in pending),F(0))==0,'collar-not-completely-covered-by-captured-parent'
   assert covered==old.intrinsic_area(collar,axis);included+=covered
  excluded=sum((old.intrinsic_area(p,axis)for p in outside),F(0));assert included+excluded==required
  source_accounts.append(dict(globalOriginalTerrainFacet=global_id,exactWholeIntrinsicArea=str(required),exactIncludedIntrinsicArea=str(included),exactExcludedOutsideActiveIntrinsicArea=str(excluded),completeExcludedOriginalFragments=[[[str(v)for v in vertex]for vertex in part]for part in outside],originalVerticalFacet=n[1]==0,completeSourcePlanePartition=True,sourceOutsideActiveReplacedByUnchangedParentNotDeletedFromInventory=True))
 for parent_id,t in enumerate(parents):
  retained,removed=exact.split(t,exact.rect_planes(active),1);parts=removed;required=old.intrinsic_area(t,1);outside=sum((old.intrinsic_area(p,1)for p in parts),F(0));assert old.intrinsic_area(retained,1)+outside==required
  for part in parts:emit(part,'retained-captured-parent-exterior',parent_id=parent_id,parent_plane=t)
  parent_accounts.append(dict(capturedParentFacet=parent_id,exactWholeCapturedTriangle=[[str(v)for v in p]for p in t],exactWholeArea=str(required),exactRemovedByActiveArea=str(old.intrinsic_area(retained,1)),exactRetainedExteriorArea=str(outside),completeRetainedExteriorFragments=[[[str(v)for v in p]for p in part]for part in parts],prepackedOriginalParentPlaneRetained=True,Float32ResidualsMeasuredNotAssumedZero=True))
 assert len(source_accounts)==len(source)and len(parent_accounts)==len(parents)
 return output,dict(declaredImmutableSourceFacets=declared_source_faces,selectedOriginalFacets=len(source),originalNominationIds=original_ids,sourceCoreExactClosedAABB=[str(v)for v in core],changedOuterClosedAABB=[str(v)for v in active],transitionWidthM=5,transitionIsNewVertexInterpolatedSurfaceNotOriginalTIN=True,completeOriginalFacetAccounts=source_accounts,completeCapturedParentAccounts=parent_accounts,completeOutputFacetLineage=lineage,outputFacets=len(output),triangleBudget=25000,triangleBudgetPass=len(output)<=25000,realFloat32CollapsedOutputFacets=collapsed,sourceLayersNeverHeightFiltered=True,noFacetsMerged=True,noOriginalSourceDecode=True,noAutomaticOverlapApproval=True,wholeCoreClosedCoverageAndProductionSeamSamplerQualificationPending=True,fullOwnedFourStreamAndWholeAffectedActorsPending=True,currentAcceptance=False,physicalAccepted=False)

def captured_parent_grid(parent,captured):
 """Grid bounds from captured coordinates; mesh index ordinals never imply cells."""
 triangles=np.asarray(captured,dtype='<f8');assert triangles.shape==(12,3,3)and np.isfinite(triangles).all()
 g=parent['meta']['georef'];assert parent['w']==g['W']and parent['h']==g['H']and F(g['aE'])>0 and F(g['aN'])<0
 domain=[F(float(triangles[:,:,0].min())),F(float(triangles[:,:,2].min())),F(float(triangles[:,:,0].max())),F(float(triangles[:,:,2].max()))]
 columns=[(domain[k]+old.ORIGIN[0]-F(g['bE']))/F(g['aE'])for k in [0,2]];rows=[(old.ORIGIN[1]-domain[k]-F(g['bN']))/F(g['aN'])for k in [1,3]]
 assert all(q.denominator==1 for q in columns+rows),'captured-parent-boundary-not-original-grid-node'
 cells=[int(columns[0]),int(rows[0]),int(columns[1]),int(rows[1])];assert 0<=cells[0]<cells[2]<parent['w']and 0<=cells[1]<cells[3]<parent['h']
 reconstructed=[[[old.f32(v)for v in p]for p in t]for t in old.parent_faces(parent,cells)]
 canonical=lambda ts:sorted(tuple(sorted(tuple(p)for p in t))for t in ts)
 assert len(reconstructed)==len(triangles)and canonical(reconstructed)==canonical(triangles.tolist()),'reconstructed-parent-not-exact-captured-packed-set'
 return cells,domain,dict(derivedFromExactGeoreferencedCapturedCoordinates=True,meshIndexOrdinalsNotUsedAsRasterIndices=True,completeCapturedFacets=len(triangles),reconstructedPackedTriangleSetsExactlyEqual=True,capturedOrientationRetainedForConstruction=True,capturedFloat64TriangleBytesSHA256=hashlib.sha256(triangles.tobytes()).hexdigest())
