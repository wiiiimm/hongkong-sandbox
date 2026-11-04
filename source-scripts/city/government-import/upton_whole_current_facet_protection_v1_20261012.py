"""UNEXECUTED whole-current-facet nomination; no acceptance or tolerance change."""
from fractions import Fraction as F
from upton_two_original_six_mask_partition_v1_20261012 import mask,clip
from upton_original_tin_current_ring_join_nomination_v1_20261012 import point
from upton_six_basic_preserved_ground_feasibility_v1_20261012 import projected_mask,area
from upton_inherited_overlap_boundary_v1_20261012 import intersection,plane,height,exact_ranges,projected_dimension

def closed_mask_meets(face,m):
 p=[point(x)for x in face]
 assert len(p)==3 and len(m)==3 and area(m)>0
 # Exact closed broadphase; strict outside only. Degenerate incident faces kept.
 if any(max(v[c]for v in p)<min(v[k]for v in m)or min(v[c]for v in p)>max(v[k]for v in m)for k,c in [(0,0),(1,2)]):return False
 for a,b in zip(m,m[1:]+m[:1]):
  p=clip(p,a,b,True)
  if not p:return False
 return True

def nominate(current,masks,domain):
 assert len(domain)==4 and domain[0]<domain[2]and domain[1]<domain[3]
 selected=[];outside=[];crossing=[];expanded=list(masks)
 for i,face in enumerate(current):
  hits=[j for j,m in enumerate(masks)if closed_mask_meets(face,m)]
  if not hits:outside.append(i);continue
  p=[point(x)for x in face];contained=all(F(domain[0])<=q[0]<=F(domain[2])and F(domain[1])<=q[2]<=F(domain[3])for q in p)
  projection=projected_mask(face);positive=area(projection)>0
  row=dict(currentFace=i,completeOriginalMaskIDs=hits,completeTripletInsideCapturedDomain=contained,projectedCollapsedUncredited=not positive,expandedMask=None)
  if positive:row['expandedMask']=len(expanded);expanded.append(projection)
  if not contained:crossing.append(i)
  selected.append(row)
 assert len(selected)+len(outside)==len(current)
 return dict(selected=selected,allOtherCurrentFaceIDs=outside,wholeFacetOutsideCapturedDomainHolds=crossing,expandedMasks=expanded,originalMaskCount=len(masks),noRecursiveWholeFacetFlood=True,noCoverageRootOrAcceptanceCredit=True)

def exact_overlap_attribution(left,right,old_left=None,old_right=None):
 a=projected_mask(left);b=projected_mask(right)
 if area(a)==0 or area(b)==0:return dict(collapsedProjectedFacetUncredited=True)
 poly=intersection(a,b)
 if not poly:return dict(exactProjectedDisjoint=True)
 ha,hb=plane(left),plane(right);assert ha is not None and hb is not None
 result=dict(exactProjectedDimension=projected_dimension(poly),exactDoubledAreaM2=str(abs(area(poly))),exactClosedPolygonXZ=[[str(v)for v in p]for p in poly],exactLeftHeightRangeM=exact_ranges(poly,ha),exactRightHeightRangeM=exact_ranges(poly,hb),exactSignedLeftMinusRightRangeM=exact_ranges(poly,tuple(x-y for x,y in zip(ha,hb))),notSamplerMAXOrApproval=True)
 if old_left is not None and old_right is not None:
  oa,ob=projected_mask(old_left),projected_mask(old_right)
  if area(oa)==0 or area(ob)==0:result['oldAncestorProjectedCollapsedUncredited']=True
  else:
   op=intersection(oa,ob);result['oldAncestorExactProjectedDimension']=projected_dimension(op)if op else 'disjoint'
 return result
