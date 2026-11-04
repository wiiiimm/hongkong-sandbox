"""DRAFT branch-aware exact nodes and full actual finite 3D seam intervals."""
from fractions import Fraction as F
import numpy as np
from exact_source_planar_domain_recovery_seams_v1_20261011 import interval_covered

def actual_point(p):
 assert len(p)==3 and all(np.isfinite(float(v))for v in p);a=np.asarray([float(v)for v in p],dtype='<f4');assert np.isfinite(a).all();return tuple(F(float(v))for v in a)

def whole_rendered_seam(a,b,neighbours,require_opposite=True):
 a,b=actual_point(a),actual_point(b);assert a!=b;delta=tuple(b[k]-a[k]for k in range(3));axis=max(range(3),key=lambda k:abs(delta[k]));rows=[];covered=[]
 for i,(u,v)in enumerate(neighbours):
  u,v=actual_point(u),actual_point(v)
  if u==v:continue
  ts=[(p[axis]-a[axis])/delta[axis]for p in[u,v]]
  if any(tuple(a[k]+t*delta[k]for k in range(3))!=p for t,p in zip(ts,[u,v])):continue
  lo,hi=max(F(0),min(ts)),min(F(1),max(ts))
  if lo>=hi:continue
  opposite=ts[0]>ts[1];rows.append(dict(neighbour=i,exactPositiveOriginalParameters=[lo,hi],oppositeDirected=opposite))
  if opposite or not require_opposite:covered.append((lo,hi))
 return dict(actualEndpoints=[a,b],allExactPositiveRenderedIntervals=rows,wholeFiniteRenderedSeamCovered=interval_covered(covered),requireOpposite=require_opposite,noPointOnlyNearOrWrongHeightCredit=True)

class BranchNodes:
 def __init__(self,source_step_bindings=None):self.bindings=source_step_bindings or {};self.nodes={};self.byxz={}
 def add(self,logical_xz,branch,exact_y):
  xz=tuple(map(F,logical_xz));assert len(xz)==2;key=(xz,str(branch));point=(xz[0],F(exact_y),xz[1])
  if key in self.nodes:assert self.nodes[key]['exactPoint']==point,'Conflicting heights within intended shared branch';return self.nodes[key]
  previous=self.byxz.get(xz,[])
  if previous:
   bound=self.bindings.get(xz);assert bound is not None and bound['sourceInducedDifferentBranches']is True and bound['sourceFacetIDs'] and str(branch)in bound['exactBranchHeights'],'Unauthorised split-height node'
   assert F(bound['exactBranchHeights'][str(branch)])==point[1]and all(F(bound['exactBranchHeights'][r['branch']])==r['exactPoint'][1]for r in previous),'Branch height not exactly bound to authentic/derived step'
  row=dict(exactLogicalXZ=xz,branch=str(branch),exactPoint=point,actualFloat32Point=actual_point(point),sourceStepBinding=self.bindings.get(xz),splitHeightsNotStructuralOrSeamCredit=True);self.nodes[key]=row;self.byxz.setdefault(xz,[]).append(row);return row
