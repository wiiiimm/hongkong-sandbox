"""Generated terrain strip preserving each authored outer facet/layer."""
import numpy as np
import shapely
from source_surface_inset import plane,lower_region

def triangles(region):
 return [p for p in shapely.get_parts(shapely.constrained_delaunay_triangles(region))if p.geom_type=='Polygon'and p.area>0]

def band_regions(outer,width):
 a,b,c,d=outer;inner=[a+width,b+width,c-width,d-width];assert 0<2*width<min(c-a,d-b)
 return inner,[shapely.box(a,b,c,inner[1]),shapely.box(a,inner[3],c,d),shapely.box(a,inner[1],inner[0],inner[3]),shapely.box(inner[2],inner[1],c,inner[3])]

def height_faces(faces):
 a=np.asarray(faces,float);p=a[:,:,[0,2]];ax,az=p[:,0,0],p[:,0,1];bx,bz=p[:,1,0],p[:,1,1];cx,cz=p[:,2,0],p[:,2,1];valid=np.abs((bz-cz)*(ax-cx)+(cx-bx)*(az-cz))>=1e-10
 ids=np.flatnonzero(valid);polys=shapely.polygons(p[valid]);return ids,polys,[plane(f)for f in a[valid]]

def owner_cells(faces,regions,fallback):
 ids,polys,planes=height_faces(faces);tree=shapely.STRtree(polys);cells=[];fallback_area=0.
 for region_id,region in enumerate(regions):
  for j in tree.query(region,predicate='intersects'):
   original=region.intersection(polys[j])
   if original.area<=0:continue
   cuts=[]
   for k in tree.query(original,predicate='intersects'):
    if j==k:continue
    overlap=original.intersection(polys[k])
    if overlap.area<=0:continue
    delta=planes[k]-planes[j]
    if np.all(delta==0):
     if k<j:cuts.append(overlap)
    else:
     for part in shapely.get_parts(overlap):
      if part.geom_type=='Polygon'and part.area>0:
       cut=lower_region(part,delta)
       if cut.area>0:cuts.append(cut)
   owned=original.difference(shapely.union_all(cuts))if cuts else original
   for tri in triangles(owned):cells.append(dict(poly=tri,coeff=planes[j],sourceFacet=int(ids[j]),region=region_id))
  union=shapely.union_all([c['poly']for c in cells if c['region']==region_id]);missing=region.difference(union);fallback_area+=missing.area
  if missing.area>0:
   additions=fallback(missing)
   for i,f in enumerate(additions):
    p=shapely.Polygon(np.asarray(f)[:,[0,2]])
    if p.area>0:cells.append(dict(poly=p,coeff=plane(np.asarray(f)),sourceFacet=None,region=region_id))
 return cells,fallback_area

def join(old,new,domain,outer,width,clip,fallback):
 old,new=np.asarray(old,float),np.asarray(new,float);inner,regions=band_regions(outer,width);cells,new_missing=owner_cells(new,regions,fallback);polys=[c['poly']for c in cells];tree=shapely.STRtree(polys);out=[];proof=dict(outer=outer,inner=inner,widthM=width,newFieldFallbackAreaM2=float(new_missing),oldFieldFallbackAreaM2=0.,oldInputFaces=len(old),newInputFaces=len(new),outerFacetsRetained=0,coreFacetsRetained=0,bandFacetsGenerated=0,verticalBandFragments=0,buildingGeometryChanges=0,singleContinuousUpperGraphRequired=False,exactUpperGraphProofClaimed=False,transitionInteriorIsNewTriangulatedTerrain=True);band_projected=[];generated=set();lineage=[];origin={};proof['outputLineage']=lineage;proof['exactDuplicateGeneratedFacesRemoved']=0
 def emit(f,kind):
  f=np.asarray(f,float);assert np.isfinite(f).all()
  if not np.any(np.cross(f[1]-f[0],f[2]-f[0])!=0):return
  if kind=='bandFacetsGenerated':
   key=tuple(sorted(map(tuple,f.astype('<f4').astype(float))))
   if key in generated:proof['exactDuplicateGeneratedFacesRemoved']+=1;return
   generated.add(key)
  out.append(f);proof[kind]+=1;lineage.append(dict(origin,kind=kind))
 def fragment(face,box,kind):
  p=clip.rect(list(face),box)
  for i in range(1,len(p)-1):emit([p[0],p[i],p[i+1]],kind)
 x,z,X,Z=domain;a,b,c,d=outer
 for source_index,face in enumerate(old):
  origin.clear();origin.update(source='prior-native',sourceFace=int(source_index))
  q=face[:,[0,2]]
  if q[:,0].max()<=a or q[:,0].min()>=c or q[:,1].max()<=b or q[:,1].min()>=d:out.append(face.copy());proof['outerFacetsRetained']+=1;lineage.append(dict(origin,kind='unchanged-outer-native'));continue
  for box in [[x,z,a,Z],[c,z,X,Z],[a,z,c,b],[a,d,c,Z]]:
   if box[0]<box[2]and box[1]<box[3]:fragment(face,box,'outerFacetsRetained')
 for source_index,face in enumerate(new):
  origin.clear();origin.update(source='narrow-native',sourceFace=int(source_index))
  q=face[:,[0,2]]
  if(q[:,0]>=inner[0]).all()and(q[:,0]<=inner[2]).all()and(q[:,1]>=inner[1]).all()and(q[:,1]<=inner[3]).all():out.append(face.copy());proof['coreFacetsRetained']+=1;lineage.append(dict(origin,kind='unchanged-native-core'))
  else:fragment(face,inner,'coreFacetsRetained')
 def blend(poly,co):
  vertices=[]
  for value in poly:
   v=np.asarray(value,float).copy();w=max(0.,min(1.,min(v[0]-a,c-v[0],v[2]-b,d-v[2])/width));v[1]=v[1]*(1-w)+(v[[0,2]]@co[:2]+co[2])*w;vertices.append(v)
  for i in range(1,len(vertices)-1):emit([vertices[0],vertices[i],vertices[i+1]],'bandFacetsGenerated')
 def process(face,region,source_index=None):
  origin.clear();origin.update(source='prior-native-band'if source_index is not None else'rendered-root-gap-in-band',sourceFace=source_index)
  poly=clip.rect(list(face),list(region.bounds))
  if len(poly)<3:return
  p=shapely.Polygon(np.asarray(poly)[:,[0,2]])
  if p.area>0:
   band_projected.append(p);co=plane(face)
   for j in tree.query(p,predicate='intersects'):
    intersection=p.intersection(polys[j])
    for t in triangles(intersection):
     q=np.asarray(t.exterior.coords[:3]);ys=q@co[:2]+co[2];origin['fieldOwnerSourceFace']=cells[j]['sourceFacet'];blend(np.column_stack([q[:,0],ys,q[:,1]]),cells[j]['coeff'])
  else:
   line=shapely.LineString(np.asarray(poly)[:,[0,2]])
   for j in tree.query(line,predicate='intersects'):
    tri=np.asarray(polys[j].exterior.coords[:3]);piece=clip.parent_clip(poly,tri)
    if len(piece)>=3:origin['fieldOwnerSourceFace']=cells[j]['sourceFacet'];blend(piece,cells[j]['coeff']);proof['verticalBandFragments']+=1
 for region in regions:
  lo=np.array(region.bounds[:2]);hi=np.array(region.bounds[2:]);q=old[:,:,[0,2]];ids=np.flatnonzero((q.max(1)>=lo).all(1)&(q.min(1)<=hi).all(1))
  for i in ids:process(old[i],region,int(i))
 missing=shapely.union_all(regions).difference(shapely.union_all(band_projected));proof['oldFieldFallbackAreaM2']=float(missing.area)
 for face in fallback(missing):
  for region in regions:process(np.asarray(face,float),region)
 proof['outputFaces']=len(out);assert len(lineage)==len(out);return np.asarray(out),proof
