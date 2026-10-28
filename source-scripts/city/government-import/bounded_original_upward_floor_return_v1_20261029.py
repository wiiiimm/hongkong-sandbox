"""Private lower-only return, bounded by unchanged source heights with 0.25m clearance."""
import numpy as np
import shapely
from ronsdale_local_inset_v2_20261022 import plane,lift,lower_region,parent_fragment_lift
from affine_terrain_blend_v1 import sector,evaluate

def inset(terrain,ramps,core_margin=1.,return_width=3.):
 terrain=np.asarray(terrain,float);ramps=np.asarray(ramps,float)
 assert np.isfinite(terrain).all()and np.isfinite(ramps).all()and core_margin==1. and return_width==3.
 ramp_polys=shapely.polygons(ramps[:,:,[0,2]]);assert np.all(shapely.area(ramp_polys)>1e-10)
 footprint=shapely.union_all(ramp_polys);core=footprint.buffer(core_margin,join_style='mitre');outer=core.buffer(return_width,join_style='mitre')
 clearance=.25;source_floor=float(ramps[:,:,1].min())-clearance;assert source_floor>=1.2
 coeffs=[plane(t)-np.array([0.,0.,clearance])for t in ramps];field_polys=[];field_planes=[]
 # Partition the entire bounded extension by the minimum authored ramp plane.
 # All source building vertices remain untouched; only this derived terrain field
 # is extended, and only inside the explicit return domain.
 for part in shapely.get_parts(shapely.constrained_delaunay_triangles(outer)):
  if part.geom_type!='Polygon'or part.area<=0:continue
  for i,coeff in enumerate(coeffs):
   cuts=[]
   for j,other in enumerate(coeffs):
    if i==j:continue
    if np.array_equal(coeff,other):
     if j<i:cuts.append(part)
    else:cuts.append(lower_region(part,coeff-other))
   kept=part.difference(shapely.union_all(cuts))if cuts else part
   for t in lift(kept,coeff):field_polys.append(shapely.Polygon(t[:,[0,2]]));field_planes.append(coeff)
 # Bound plane extrapolation outside the actual source triangles. The floor
 # cannot exceed any nominated source vertex minus the fixed clearance.
 bounded_polys=[];bounded_planes=[];floor=np.array([0.,0.,source_floor])
 for polygon,coeff in zip(field_polys,field_planes):
  below=lower_region(polygon,floor-coeff)
  for region,target in [(below,floor),(polygon.difference(below),coeff)]:
   for face in lift(region,target):
    bounded_polys.append(shapely.Polygon(face[:,[0,2]]));bounded_planes.append(target)
 field_polys,field_planes=bounded_polys,bounded_planes
 union=shapely.union_all(field_polys)
 assert union.symmetric_difference(outer).area<1e-6 and abs(sum(p.area for p in field_polys)-union.area)<1e-6
 bands=[(core,None)]
 for p in shapely.get_parts(shapely.constrained_delaunay_triangles(outer.difference(core))):
  if p.geom_type!='Polygon'or p.area<=0:continue
  xz=np.asarray(p.exterior.coords[:3]);weights=[]
  for point in xz:
   q=shapely.Point(point);inside=q.distance(core.boundary)<1e-8;outside=q.distance(outer.boundary)<1e-8;assert inside!=outside;weights.append(0. if inside else 1.)
  bands.append((p,sector(xz,weights)))
 tree=shapely.STRtree(field_polys);output=[];lineage=[];changed=[];removed=inserted=0.;max_lowering=0.
 for i,t in enumerate(terrain):
  p=shapely.Polygon(t[:,[0,2]])
  if p.area<=1e-10 or not p.intersects(outer):output.append(t);lineage.append(dict(kind='unchanged',parentFace=i));continue
  tp=plane(t);cuts=[];added=[]
  for j in tree.query(p,predicate='intersects'):
   q=p.intersection(field_polys[j])
   if q.area<=1e-10:continue
   lower=lower_region(q,tp-field_planes[j])
   if lower.area<=1e-10:continue
   cuts.append(lower)
   for region,weight in bands:
    for face in lift(lower.intersection(region),field_planes[j]):
     old=face[:,[0,2]]@tp[:2]+tp[2]
     if weight is not None:
      w=evaluate(face[:,[0,2]],weight);face[:,1]=face[:,1]*(1-w)+old*w
     assert np.all(face[:,1]<=old+1e-9)and face[:,1].min()>=1.2
     max_lowering=max(max_lowering,float((old-face[:,1]).max()));added.append((face,int(j),weight is not None))
  if not cuts:output.append(t);lineage.append(dict(kind='unchanged',parentFace=i));continue
  cut=shapely.union_all(cuts);removed+=cut.area;changed.append(i)
  for f in parent_fragment_lift(p.difference(cut),tp):output.append(f);lineage.append(dict(kind='parent-fragment',parentFace=i))
  for f,j,blended in added:output.append(f);lineage.append(dict(kind='ramp-derived-return'if blended else'ramp-plane-core',parentFace=i,fieldFace=j));inserted+=shapely.Polygon(f[:,[0,2]]).area
 assert abs(removed-inserted)<1e-6 and len(output)<=25000
 return np.asarray(output),dict(sourceMinimumY=float(ramps[:,:,1].min()),sourceDerivedMinimumTerrainY=source_floor,sourceClearanceM=clearance,coreWKT=core.wkt,outerWKT=outer.wkt,footprintWKT=footprint.wkt,changedTerrainFaceIndices=changed,removedProjectedAreaM2=removed,insertedProjectedAreaM2=inserted,maximumLoweringM=max_lowering,fieldPlanes=[p.tolist()for p in field_planes],fieldPolygonsWKT=[p.wkt for p in field_polys],outputLineage=lineage,coreMarginM=core_margin,returnWidthM=return_width,sourceGeometryChanges=0,policy='Private lower-only return from original planes offset down0.25m, clamped below by the original source minimum minus0.25m, with existing1m core/3m affine return. Original geometry/pose immutable; all source, terrain, neighbour, visual and publication checks remain separate.')
