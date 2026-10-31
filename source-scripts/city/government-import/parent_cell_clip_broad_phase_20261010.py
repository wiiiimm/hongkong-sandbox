"""Preserve original terrain clip arithmetic/order; omit only distant parent cells.

The padding belongs only to candidate lookup. It never alters a point, clipping
predicate, output polygon, source surface, or acceptance threshold.
"""
import numpy as np,shapely
class ParentCellClipIndex:
 def __init__(self,triangles):
  self.triangles=np.asarray(triangles,float);a=self.triangles
  assert a.ndim==3 and a.shape[1:]==(3,2) and len(a) and np.isfinite(a).all()
  assert np.abs(a).max()<=1e6
  self.lo=a.min(axis=1);self.hi=a.max(axis=1);width=self.hi-self.lo
  assert (width>=.01).all(),'Only finite axis-aligned right parent triangles are supported'
  for t,l,h in zip(a,self.lo,self.hi):
   assert all(all(v[k] in [l[k],h[k]] for k in [0,1]) for v in t)
   assert len(set(map(tuple,t)))==3
  # Existing parent_clip uses cross-product epsilon1e-9. Horizontal and
  # vertical parent edges bound its admissible region by epsilon/edge-length.
  # This conservative search margin also contains floating arithmetic error.
  self.lookupPadding=max(1e-6,8e-9/float(width.min())+128*float(np.spacing(max(1.,np.abs(a).max()))))
  self.tree=shapely.STRtree(shapely.box(self.lo[:,0],self.lo[:,1],self.hi[:,0],self.hi[:,1]))
 def candidate_ids(self,poly):
  p=np.asarray(poly,float);assert p.ndim==2 and p.shape[1]==3 and np.isfinite(p).all() and np.abs(p).max()<=1e6
  if not len(p):return []
  lo=p[:,[0,2]].min(axis=0)-self.lookupPadding;hi=p[:,[0,2]].max(axis=0)+self.lookupPadding
  return sorted(map(int,self.tree.query(shapely.box(*lo,*hi))))
 def clip(self,poly,original_clip):
  if not poly:return []
  return [original_clip(poly,self.triangles[i]) for i in self.candidate_ids(poly)]
