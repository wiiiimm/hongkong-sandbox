"""Bounded candidate construction helpers, never source/support acceptance.

Exact dyadic enclosure, inclusive binary-coordinate separation, multiset union
of literal snapshots and complete aligned scalar-grid identity. No tolerance.
"""
from collections import Counter
from fractions import Fraction as F
import copy,math
import numpy as np

def clip_new_planes_outside(ground,protected):
 """Construction only: clip on each complete input plane, never sample Y.

 GEOS floating overlay/triangulation is not an exact coverage/seam certificate.
 Keep every positive-area fragment, and check literal packing separately.
 """
 import shapely
 output=[]
 for face in np.asarray(ground,float).reshape(-1,3,3):
  assert np.isfinite(face).all()
  poly=shapely.Polygon(face[:,[0,2]])
  assert poly.is_valid and poly.area>0,'New terrain has collapsed projected facet'
  normal=np.cross(face[1]-face[0],face[2]-face[0]);assert normal[1]!=0
  remaining=poly.difference(protected)
  for part in shapely.get_parts(shapely.constrained_delaunay_triangles(remaining)):
   if part.geom_type!='Polygon' or part.area==0:continue
   xz=np.asarray(part.exterior.coords)[:3]
   xyz=np.asarray([[x,face[0,1]-(normal[0]*(x-face[0,0])+normal[2]*(z-face[0,2]))/normal[1],z]for x,z in xz])
   if np.dot(np.cross(xyz[1]-xyz[0],xyz[2]-xyz[0]),normal)<0:xyz=xyz[[0,2,1]]
   output.append(xyz)
 assert output,'Protected region removed every new terrain facet'
 return np.asarray(output,float)

def dyadic_facet_boxes(worlds,scale=1024,collar_cells=0):
 assert scale==1024 and isinstance(collar_cells,int)and collar_cells>=0
 boxes=set()
 for world in worlds:
  a=np.asarray(world,float);assert a.ndim==3 and a.shape[1:]==(3,3)and np.isfinite(a).all()
  for face in a:
   lo=face[:,[0,2]].min(axis=0);hi=face[:,[0,2]].max(axis=0)
   lower=[math.floor(F(float(v))*scale)-collar_cells for v in lo]
   upper=[math.ceil(F(float(v))*scale)+collar_cells for v in hi]
   for k in range(2):
    if upper[k]==lower[k]:upper[k]+=1
    assert F(lower[k],scale)<=F(float(lo[k]))<=F(float(hi[k]))<=F(upper[k],scale)
   boxes.add(tuple(float(F(v,scale))for v in lower+upper))
 return np.asarray(sorted(boxes),float).reshape(-1,4)

def strictly_separate_boxes_from_owned(boxes,worlds):
 b=np.asarray(boxes,float);assert b.ndim==2 and b.shape[1]==4 and len(b)and np.isfinite(b).all();assert np.all(b[:,:2]<b[:,2:])
 omitted=0
 for world in worlds:
  a=np.asarray(world,float);assert a.ndim==3 and a.shape[1:]==(3,3)and np.isfinite(a).all()
  lo=a[:,:,[0,2]].min(axis=1);hi=a[:,:,[0,2]].max(axis=1)
  for rectangle in b:
   hits=np.all(lo<=rectangle[2:],axis=1)&np.all(hi>=rectangle[:2],axis=1)
   assert not hits.any(),('Retained dyadic protection overlaps/touches owned facet box',rectangle.tolist(),np.flatnonzero(hits).tolist())
   omitted+=len(a)
 return dict(allClosedBoxesStrictlySeparated=True,completeFacetRectanglePairs=omitted,noTolerance=True)

def merge_literal_ground_snapshots(arrays):
 counts=Counter();ordered={}
 for array in arrays:
  a=np.asarray(array,float).reshape(-1,3,3);assert len(a)and np.isfinite(a).all()
  f32=a.astype(np.float32);assert np.array_equal(a,f32.astype(float)),'Captured terrain is not literal Float32'
  local=Counter()
  for face in f32:
   key=face.tobytes();local[key]+=1;ordered.setdefault(key,face.copy())
  for key,count in local.items():counts[key]=max(counts[key],count)
 result=np.asarray([ordered[key]for key,count in counts.items()for _ in range(count)],np.float32).astype(float)
 assert len(result)==sum(counts.values());return result

def whole_ground_faces_touching_boxes(ground,boxes):
 g=np.asarray(ground,float);b=np.asarray(boxes,float);assert g.ndim==3 and g.shape[1:]==(3,3)and np.isfinite(g).all();assert b.ndim==2 and b.shape[1]==4 and np.isfinite(b).all()
 lo=g[:,:,[0,2]].min(axis=1);hi=g[:,:,[0,2]].max(axis=1);selected=np.zeros(len(g),bool)
 for rectangle in b:selected|=np.all(lo<=rectangle[2:],axis=1)&np.all(hi>=rectangle[:2],axis=1)
 assert selected.any(),'No literal current terrain covers retained region'
 return np.flatnonzero(selected),g[selected].copy()

def copy_complete_aligned_old_grid(candidate,old):
 """Copy all old scalar nodes with exact global node/cell correspondence.

Pitch and orientation match; every old absolute node matches its mapped new
node. Thus every old cell's complete corner tuple and diagonal convention are
identical, proving the scalar piecewise-affine fallback function unchanged.
This does not claim unchanged new native terrain elsewhere in that region.
 """
 result=copy.deepcopy(candidate);og=old['meta']['georef'];ng=result['meta']['georef']
 for obj,g in [(old,og),(result,ng)]:
  assert g['W']==obj['w']and g['H']==obj['h']and obj['w']>1 and obj['h']>1
  assert g['aE']>0 and g['aN']<0 and obj['cell']==g['aE']==-g['aN']
 assert F(og['aE'])==F(ng['aE'])and F(og['aN'])==F(ng['aN']),'Old/new fine-grid pitch differs'
 col=(F(og['bE'])-F(ng['bE']))/F(ng['aE']);row=(F(og['bN'])-F(ng['bN']))/F(ng['aN'])
 assert col.denominator==row.denominator==1,'Old fine-grid origin not aligned';col=int(col);row=int(row)
 assert 0<=col and 0<=row and col+old['w']<=result['w']and row+old['h']<=result['h'],'Old scalar-grid region outside candidate'
 keys=['elev','renderedElev','vegetation'];mapping=[]
 for key in keys:
  assert key in old and key in result and len(old[key])==old['w']*old['h']and len(result[key])==result['w']*result['h']
  assert all(math.isfinite(float(v))for v in old[key]+result[key])
 for r in range(old['h']):
  for c in range(old['w']):
   oi=r*old['w']+c;nr,nc=r+row,c+col;ni=nr*result['w']+nc
   assert F(og['bE'])+c*F(og['aE'])==F(ng['bE'])+nc*F(ng['aE'])
   assert F(og['bN'])+r*F(og['aN'])==F(ng['bN'])+nr*F(ng['aN'])
   for key in keys:result[key][ni]=old[key][oi]
   mapping.append([oi,ni])
 for oi,ni in mapping:
  for key in keys:assert result[key][ni]==old[key][oi]
 return result,dict(copiedKeys=keys,oldColumnOffset=col,oldRowOffset=row,completeOldNodeIndexMapping=mapping,completeOldNodes=len(mapping),completeOldCells=(old['w']-1)*(old['h']-1),allAbsoluteNodesAndCellCornerTuplesEqual=True,scalarGridFallbackPiecewiseAffineFunctionUnchanged=True,sameTriangleDiagonalAndFiniteRenderedOverrideRequired=True,arbitraryPointIEEEOutputBitIdentityNotClaimed=True,newNativeSurfaceElsewhereNotClaimedUnchanged=True)
