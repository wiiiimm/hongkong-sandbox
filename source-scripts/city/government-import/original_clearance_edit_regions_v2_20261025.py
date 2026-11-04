"""Nominate private earth fixes for negative floors and walls without a clear cap.

Every original face remains; capped grade-intersecting walls retain their exact
negative proofs for separate source-role review. This never approves a model.
"""
import numpy as np
import shapely
from original_clearance_exact_stream_rebind_v1_20261025 import verify_stream


def edit_regions(worlds,ground,proofs,caps):
 assert set(worlds)==set(proofs)==set(caps)=={'original','literal','left','balanced'}
 required=[];bindings=[]
 for mode,tri in worlds.items():
  proof=proofs[mode];cap=caps[mode];assert verify_stream(tri,ground,proof)
  assert cap['sourceWorldSHA256']==proof['sourceWorldSHA256']and cap['actualGroundSHA256']==cap['compoundGroundSHA256']==proof['groundSHA256']
  ids=[r['sourceFace']for r in proof['rows']];assert len(ids)==len(set(ids))and all(isinstance(i,int)and 0<=i<len(tri)for i in ids)
  cp=cap['proof'];assert cp['completeSourceFaces']==len(tri)and set(cp['negativeSourceFaces'])==set(ids)
  nonrendering=set(cp['nonrenderingSourceFaces']);assert all(isinstance(i,int)and 0<=i<len(tri)for i in nonrendering)
  paths={r['sourceFace']:r for r in cp['paths']};assert len(paths)==len(cp['paths'])and paths.keys()|set(cp['negativeNonWallFaces'])|(nonrendering&set(ids))==set(ids)
  needed=[];retained=[]
  for row in proof['rows']:
   i=row['sourceFace'];assert np.array_equal(np.asarray(row['vertices']),tri[i]),'Changed negative-face witness'
   wall=row['absoluteNormalYRatio']is not None and row['absoluteNormalYRatio']<.25
   if wall and i in paths and paths[i]['hasExactSharedEdgeClearCapPath']:
    retained.append(i);continue
   needed.append(i);required.append(shapely.MultiPoint(tri[i][:,[0,2]]).convex_hull)
  assert set(needed).isdisjoint(retained)and set(needed)|set(retained)==set(ids)
  bindings.append(dict(mode=mode,completeSourceFaces=len(tri),allNegativeFaces=ids,requiredEarthFixFaces=needed,retainedNegativeWallsWithExactClearCap=retained,sourceWorldSHA256=proof['sourceWorldSHA256'],groundSHA256=proof['groundSHA256']))
 assert required,'No uncapped/floor negative face requires earth correction'
 region=shapely.union_all(required);core=region.buffer(1,join_style='mitre');outer=core.buffer(3,join_style='mitre')
 assert core.is_valid and outer.is_valid and core.area>0 and core.covers(region)and outer.covers(core)
 return region,core,outer,bindings


def verify_domain_sources(context,receipt,primary,rows,wanted):
 requested=list(wanted);uids=set(requested);assert len(requested)==len(uids)
 parent_uids=context['uids'];assert len(parent_uids)==len(set(parent_uids))and set(parent_uids)<=uids and primary in parent_uids
 assert len(receipt['uids'])==len(uids)and set(receipt['uids'])==uids
 expected={r['uid']:r['sourceSHA256']for r in rows if r['uid']in uids}
 assert set(expected)==uids and receipt['sourceSHA256ByUid']==expected,'Full source-domain receipt changed'
 return True
