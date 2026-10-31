"""Apply the existing bounded ramp return independently to disjoint domains.

Planes from a distant ramp must not be extrapolated into another ramp's domain.
All V1 lowering, area conservation, height and complexity guards remain active.
"""
import numpy as np
import shapely
from bounded_original_upward_floor_return_v2_20261031 import inset as single_inset

def inset(terrain,ramps,core_margin=1.,return_width=3.):
 terrain=np.asarray(terrain,float);ramps=np.asarray(ramps,float)
 assert np.isfinite(terrain).all() and np.isfinite(ramps).all()
 assert core_margin==1. and return_width==3.
 polygons=shapely.polygons(ramps[:,:,[0,2]])
 assert len(polygons) and np.all(shapely.area(polygons)>1e-10)
 domains=[p.buffer(core_margin,join_style='mitre').buffer(return_width,join_style='mitre')for p in polygons]
 outer=shapely.union_all(polygons).buffer(core_margin,join_style='mitre').buffer(return_width,join_style='mitre')
 components=list(shapely.get_parts(outer));assert all(p.geom_type=='Polygon'for p in components)
 out=terrain.copy();proofs=[];assigned=[];origins=list(range(len(terrain)));changed=set()
 for component in sorted(components,key=lambda p:p.bounds):
  indices=[i for i,p in enumerate(polygons)if component.intersection(p).area>1e-10]
  assert indices;assigned.extend(indices)
  before=out;out,proof=single_inset(before,ramps[indices],core_margin,return_width)
  changed.update(origins[i]for i in proof['changedTerrainFaceIndices'])
  origins=[origins[r['parentFace']]for r in proof['outputLineage']]
  assert shapely.from_wkt(proof['outerWKT']).symmetric_difference(component).area<1e-6
  proofs.append(dict(sourceRampIndices=indices,inputTriangles=len(before),outputTriangles=len(out),**proof))
 assert sorted(assigned)==list(range(len(ramps))) and len(out)<=25000 and out[:,:,1].min()>=1.2
 return out,dict(changedTerrainFaceIndices=sorted(changed),componentProofs=proofs,removedProjectedAreaM2=sum(p['removedProjectedAreaM2']for p in proofs),insertedProjectedAreaM2=sum(p['insertedProjectedAreaM2']for p in proofs),outerWKT=outer.wkt,outputOriginalParentFaceIndices=origins,maximumLoweringM=max(p['maximumLoweringM']for p in proofs),sourceGeometryChanges=0,policy='Lower-only source-floor-bounded0.25m-clearance return, independently per disconnected domain. Existing1m core/3m return, area/height/25k guards retained. No source edit or acceptance.')
