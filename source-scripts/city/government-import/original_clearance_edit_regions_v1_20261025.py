"""Derive private terrain edit regions from every exact current negative face.

This chooses where to propose terrain work, never approves final source clearance.
"""
import numpy as np
import shapely
from original_clearance_exact_stream_rebind_v1_20261025 import verify_stream


def edit_regions(worlds,ground,proofs):
 assert set(worlds)==set(proofs)=={'original','literal','left','balanced'}
 required=[];bindings=[]
 for mode,tri in worlds.items():
  proof=proofs[mode];assert verify_stream(tri,ground,proof)
  ids=[r['sourceFace']for r in proof['rows']]
  assert len(ids)==len(set(ids))and all(isinstance(i,int)and 0<=i<len(tri)for i in ids)
  for i in ids:
   assert np.array_equal(np.asarray(next(r for r in proof['rows']if r['sourceFace']==i)['vertices']),tri[i]),'Changed negative-face witness'
   required.append(shapely.MultiPoint(tri[i][:,[0,2]]).convex_hull)
  bindings.append(dict(mode=mode,completeSourceFaces=len(tri),allNegativeFaces=ids,sourceWorldSHA256=proof['sourceWorldSHA256'],groundSHA256=proof['groundSHA256']))
 assert required,'No current negative face requires terrain correction'
 region=shapely.union_all(required);core=region.buffer(1,join_style='mitre');outer=core.buffer(3,join_style='mitre')
 assert core.is_valid and outer.is_valid and core.area>0 and core.covers(region)and outer.covers(core)
 return region,core,outer,bindings
