"""Changed terrain proposal: retained parent core, 8mm blend and 2mm zero-alpha collar.

This never changes buildings or accepts terrain. Packed clips are expressly
retessellated terrain, not exact original planes. Complete actual actor/source,
finite domain/height/seam/runtime/foreign guards remain independent.
"""
import copy
from fractions import Fraction as F
import numpy as np,shapely
from run import digest
from native_parent_child_flat_composition_20261010 import faces
from whole_source_disjoint_literal_parent_facets_20261010 import finite_projection,form_polygon
from actual_native_parent_transition_v3_20261010 import rational,triangle_clip,nondegenerate,cross,parent_plane_height
from exact_original_polygon_triangle_partition_20261010 import exact_partition,on_segment

def parts(region):
 assert region.geom_type=='Polygon'and region.is_valid and region.area>0
 triangles=[list(t.exterior.coords)[:3]for t in shapely.get_parts(shapely.constrained_delaunay_triangles(region))]
 rings=[list(region.exterior.coords),*[list(r.coords)for r in region.interiors]]
 return triangles,rings,exact_partition(rings,triangles)
def boundary(point,rings):
 p=(point[0],point[2])
 for r in rings:
  rr=[tuple(F(float(v))for v in q)for q in r]
  if rr[0]==rr[-1]:rr.pop()
  if any(on_segment(a,b,p)for a,b in zip(rr,rr[1:]+rr[:1])):return True
 return False

def propose(candidate,parent,source_streams,basic,current_rings,*,margin=.01,budget=100000):
 assert margin==.01 and budget==100000,'Existing margin and budget remain fixed'
 assert set(source_streams)=={'providerOriginal','actualLiteral','explicitLeftAssociatedF32ModelMatrix','explicitBalancedF32ModelMatrix'}
 base=faces(candidate);old=faces(parent);basic=np.asarray(basic,dtype=float);assert np.isfinite(base).all()and np.isfinite(old).all()and np.isfinite(basic).all()
 core=finite_projection(basic).union(form_polygon(current_rings));outer=core.buffer(margin,join_style='mitre');apron=outer.difference(core)
 sources={k:finite_projection(v)for k,v in source_streams.items()}
 assert all(not outer.intersects(p)for p in sources.values()),'Actual protected envelope intersects a complete source arithmetic stream'
 blend_outer=core.buffer(margin-.002,join_style='mitre');blend=blend_outer.difference(core);collar=outer.difference(blend_outer)
 core_tri,core_rings,core_part=parts(core);apron_tri,apron_rings,apron_part=parts(blend);collar_tri,collar_rings,collar_part=parts(collar);_,outer_rings,_=parts(outer)
 projected=[];ground_ids=[]
 for i,t in enumerate(base):
  if cross(*[rational(p)for p in t])!=0:projected.append(shapely.Polygon(t[:,[0,2]]));ground_ids.append(i)
 tree=shapely.STRtree(projected);out=copy.deepcopy(candidate);mesh=out['nativeMesh'];old_position=copy.deepcopy(mesh['position']);old_index=copy.deepcopy(mesh['index']);records=[];added=[];height_errors=[];nonheight=[];packed_degenerate=[]
 def append(poly,parent_face,region,candidate_face=None):
  if len(poly)<3:return []
  vertices=[];vertex_records=[]
  for p in poly:
   if region=='core' or candidate_face is None:alpha=1.0;y=float(p[1])
   elif region=='zero-collar' or boundary(p,outer_rings):alpha=0.0;y=float(parent_plane_height(p,candidate_face))
   elif boundary(p,core_rings):alpha=1.0;y=float(p[1])
   else:
    alpha=max(0.0,min(1.0,1.0-shapely.Point(float(p[0]),float(p[2])).distance(core)/(margin-.002)));y=float(p[1])*alpha+float(parent_plane_height(p,candidate_face))*(1-alpha)
   packed=np.asarray([float(p[0]),y,float(p[2])],dtype=np.float32).astype(float);assert np.isfinite(packed).all();vertices.append(packed)
   before=[str(v)for v in p];err=None
   if region=='core'and cross(*[rational(q)for q in parent_face])!=0:
    err=F(float(packed[1]))-parent_plane_height(rational(packed),parent_face);height_errors.append(float(abs(err)))
   vertex_records.append(dict(exactParentClipVertex=before,blendAlpha=alpha,packedFloat32Vertex=packed.tolist(),corePackedParentHeightDeviationM=str(err)if err is not None else None))
  ids=[]
  for j in range(1,len(poly)-1):
   if not nondegenerate([poly[0],poly[j],poly[j+1]]):continue
   tri=np.asarray([vertices[0],vertices[j],vertices[j+1]],dtype=float)
   first=len(mesh['position'])//3;mesh['position'].extend(tri.reshape(-1).tolist());mesh['index'].extend([first,first+1,first+2]);assert len(mesh['index'])//3<=budget
   faceid=len(mesh['index'])//3-1;ids.append(faceid);added.append(tri)
   if not nondegenerate([rational(p)for p in tri]):packed_degenerate.append(faceid)
  return dict(completePrepackVertices=vertex_records,newCandidateFaceIds=ids)
 for i,t in enumerate(old):
  original=[rational(p)for p in t];clips=[]
  for label,triangles in [('core',core_tri),('apron',apron_tri),('zero-collar',collar_tri)]:
   for j,q in enumerate(triangles):
    if t[:,0].max()<min(p[0]for p in q)or t[:,0].min()>max(p[0]for p in q)or t[:,2].max()<min(p[1]for p in q)or t[:,2].min()>max(p[1]for p in q):continue
    clipped=triangle_clip(original,[[p[0],0,p[1]]for p in q])
    if not clipped:continue
    if label=='core'or cross(*original)==0:
     result=append(clipped,t,label);clips.append(dict(region=label,regionTriangle=j,exactFiniteClipVertices=[[str(v)for v in p]for p in clipped],output=result))
     if cross(*original)==0:nonheight.append(i)
    else:
     xy=np.asarray(clipped,float)[:,[0,2]];lo=np.nextafter(xy.min(0),-np.inf);hi=np.nextafter(xy.max(0),np.inf)
     for k in sorted(map(int,tree.query(shapely.box(*lo,*hi)))):
      gid=ground_ids[k];fragment=triangle_clip(clipped,base[gid])
      if not fragment:continue
      result=append(fragment,t,label,base[gid]);clips.append(dict(region=label,regionTriangle=j,candidatePlaneFace=gid,exactFiniteClipVertices=[[str(v)for v in p]for p in fragment],output=result))
  records.append(dict(originalParentFace=i,exactZeroProjectedArea=cross(*original)==0,exactDegenerate3D=not nondegenerate(original),completeFiniteClipDispositions=clips))
 assert added and mesh['position'][:len(old_position)]==old_position and mesh['index'][:len(old_index)]==old_index
 actual=np.asarray(added,dtype='<f8');projection=finite_projection(actual)
 assert all(not projection.intersects(p)for p in sources.values()),'Packed appended terrain intersects a source arithmetic stream'
 proof=dict(completeOriginalCandidateFaces=len(base),completeActualParentFaces=len(old),completeAddedTerrainFaces=len(actual),finalTerrainFacets=len(mesh['index'])//3,originalCandidatePositionAndIndexPrefixesUnchanged=True,completeOriginalParentFacetDispositions=records,exactCoreRegionPartition=core_part,exactApronRegionPartition=apron_part,exactZeroAlphaCollarRegionPartition=collar_part,declaredZeroAlphaCollarWidthM=.002,declaredBlendWidthM=margin-.002,actualProtectedCoreGeoJSON=shapely.to_geojson(core),declaredOuterEnvelopeGeoJSON=shapely.to_geojson(outer),sourceStreamDistancesM={k:outer.distance(p)for k,p in sources.items()},completeAddedFloat32TriangleSHA256=digest(actual.tobytes()),maxCorePackedParentHeightDeviationM=max(height_errors,default=0),exactParentPlanePreservationClaimed=False,allParentNonheightClipFaceIds=sorted(set(nonheight)),packedDegenerateAddedFaceIds=packed_degenerate,unchangedTerrainBudget=budget,declaredTransitionWidthM=margin,terrainRepresentationChanges=True,governmentBuildingGeometryChanges=0,physicalAccepted=False,installationApproved=False,qualification='Separately labelled scripted terrain proposal. Original candidate streams remain literal; clipped parent core is explicitly Float32-retessellated, apron is constrained by actual candidate finite planes and has declared alpha1/alpha0 boundaries and a constrained2mm zero-alpha collar INSIDE the same1cm envelope (no seam tolerance change). Exact packed actor coverage, all finite seams/heights/upper-branch continuity, source original/literal/F32 clearance, complete BASIC/native/foreign/runtime gates remain mandatory. No original-plane equivalence or numeric waiver.')
 return out,proof
