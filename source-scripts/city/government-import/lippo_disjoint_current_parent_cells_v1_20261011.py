"""Exact bounded-cell proposal for two complete Lippo originals.

The default 20 m padding crosses the existing Hullett child. This proposed
rectangle removes one padded row only; all source bounds plus the full 1 m
native core remain inside it. No terrain/model/support acceptance is supplied.
"""
import math
import numpy as np
from lippo_pair_current_identity_v1_20261011 import UIDS
from lippo_three_original_current_inventory_20261010 import EXPECTED
from run import digest
PARENT_URL='city/data/terrain-government-xl-caine-road-original-pair-installed-v2-20261010.json'
CELLS=[531,0,559,25]
def overlap(a,b):return a[0]<b[2] and b[0]<a[2] and a[1]<b[3] and b[1]<a[3]
def extent(cells,parent):
 g=parent['meta']['georef'];c0,r0,c1,r1=cells
 return [g['bE']+c0*g['aE']-834500,816500-g['bN']-r0*g['aN'],g['bE']+c1*g['aE']-834500,816500-g['bN']-r1*g['aN']]
def proposed_cells(rows,parent):
 assert len(rows)==2 and {r['uid'] for r in rows}==UIDS
 a=np.asarray([r['native']['model']['worldBounds'] for r in rows],dtype=float)
 assert a.shape==(2,2,3) and np.isfinite(a).all() and (a[:,0]<a[:,1]).all()
 assert len(parent['patches'])==10 and len({p['id'] for p in parent['patches']})==10
 assert parent['meta']['georef']['aE']==5 and parent['meta']['georef']['aN']==-5
 assert 0<=CELLS[0]<CELLS[2]<parent['w'] and 0<=CELLS[1]<CELLS[3]<parent['h']
 bounds=extent(CELLS,parent);lo=a[:,0].min(0);hi=a[:,1].max(0)
 core=[lo[0]-1,lo[2]-1,hi[0]+1,hi[2]+1]
 assert bounds[0]<core[0]<core[2]<bounds[2] and bounds[1]<core[1]<core[3]<bounds[3], 'Complete original/core outside proposal'
 assert not any(overlap(CELLS,c['coarseCells']) for c in parent['patches']), 'Existing child overlap'
 # At the reduced upper-z edge retain the complete original core and the
 # unchanged builder's entire 10 m transition width. The lower-z boundary is
 # the existing regional parent boundary, already truncated by its grid.
 assert bounds[3]-core[3]>=10,'Reduced edge would truncate source transition'
 return list(CELLS)

def complete_geometry_containment(rows,parent,representations):
 cells=proposed_cells(rows,parent);bounds=extent(cells,parent)
 a=np.asarray([r['native']['model']['worldBounds'] for r in rows],dtype=float)
 lo=a[:,0].min(0);hi=a[:,1].max(0);core=[lo[0]-1,lo[2]-1,hi[0]+1,hi[2]+1]
 assert set(representations)=={'completeOriginal','literalWorldFloat64','roundedWorldPositionFloat32','explicitFloat32ModelMatrixWorldPosition'}
 results=[]
 for kind,actors in sorted(representations.items()):
  assert set(actors)==UIDS
  for uid,t in sorted(actors.items()):
   t=np.asarray(t,dtype='<f8');assert t.shape==(EXPECTED[uid][2],3,3) and np.isfinite(t).all()
   low=t.min((0,1));high=t.max((0,1))
   assert core[0]<=low[0]<=high[0]<=core[2] and core[1]<=low[2]<=high[2]<=core[3], 'Complete source/render geometry outside native core'
   results.append(dict(representation=kind,uid=uid,completeFaces=len(t),worldTrianglesSHA256=digest(t.tobytes()),wholeBounds=[low.tolist(),high.tolist()],completeNativeCoreContainment=True))
 return dict(cells=cells,bounds=bounds,core=core,completeFourRepresentationBindings=results,physicalAccepted=False,terrainAccepted=False,sourceGeometryChanges=0)
