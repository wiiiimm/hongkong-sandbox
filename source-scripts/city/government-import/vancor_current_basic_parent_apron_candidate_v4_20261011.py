"""Changed terrain proposal: conforming exact upper-envelope cells before Float32 packing.

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
from exact_finite_upper_surface_cells_20261011 import partition as upper_cells,area as exact_projected_area,plane as exact_plane,height as branch_height,inside as branch_contains

def json_safe(value):
 if isinstance(value,F):return str(value)
 if isinstance(value,dict):return {k:json_safe(v)for k,v in value.items()}
 if isinstance(value,(list,tuple)):return [json_safe(v)for v in value]
 return value

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
 base=faces(candidate);assert len(base)<budget,'No capacity for required added terrain within unchanged budget';old=faces(parent);basic=np.asarray(basic,dtype=float);assert np.isfinite(base).all()and np.isfinite(old).all()and np.isfinite(basic).all()
 core=finite_projection(basic).union(form_polygon(current_rings));outer=core.buffer(margin,join_style='mitre');apron=outer.difference(core)
 sources={k:finite_projection(v)for k,v in source_streams.items()}
 assert all(not outer.intersects(p)for p in sources.values()),'Actual protected envelope intersects a complete source arithmetic stream'
 blend_outer=core.buffer(margin-.002,join_style='mitre');blend=blend_outer.difference(core);collar=outer.difference(blend_outer)
 core_tri,core_rings,core_part=parts(core);apron_tri,apron_rings,apron_part=parts(blend);collar_tri,collar_rings,collar_part=parts(collar);_,outer_rings,_=parts(outer)
 projected=[];ground_ids=[]
 for i,t in enumerate(base):
  if cross(*[rational(p)for p in t])!=0:projected.append(shapely.Polygon(t[:,[0,2]]));ground_ids.append(i)
 tree=shapely.STRtree(projected);out=copy.deepcopy(candidate);mesh=out['nativeMesh'];old_position=copy.deepcopy(mesh['position']);old_index=copy.deepcopy(mesh['index']);records=[];added=[];height_errors=[];nonheight=[];packed_degenerate=[];pending=[];upper_cell_proofs=[]
 def append(poly,parent_face,region,candidate_face=None):
  if len(poly)<3:return []
  output={};pending.append((poly,parent_face,region,candidate_face,output));return output
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
     if exact_projected_area(clipped)==0:
      clips.append(dict(region=label,regionTriangle=j,exactFiniteClipVertices=[[str(v)for v in p]for p in clipped],exactZeroProjectedBoundaryOnly=True,output={}))
      continue
     cells,certificate=upper_cells(clipped,base,max_cells=budget-len(base))
     upper_cell_proofs.append(dict(originalParentFace=i,region=label,regionTriangle=j,certificate=json_safe(certificate)))
     for cell in cells:
      gid=cell['faceIndex'];fragment=cell['polygon']
      result=append(fragment,t,label,base[gid]);clips.append(dict(region=label,regionTriangle=j,candidatePlaneFace=gid,exactFiniteClipVertices=[[str(v)for v in p]for p in fragment],exactUpperCellPlane=[str(v)for v in cell['plane']],output=result))
  records.append(dict(originalParentFace=i,exactZeroProjectedArea=cross(*original)==0,exactDegenerate3D=not nondegenerate(original),completeFiniteClipDispositions=clips))
 # Conform ALL rational finite region interfaces before any packing. Every
 # boundary segment gains all existing exact clip vertices lying on it;
 # centre fans retain every segment rather than dropping collinear fan edges.
 projected_nodes=set((p[0],p[2])for poly,face,region,host,outcome in pending if cross(*[rational(p)for p in face])!=0 for p in poly)
 prepared=[];roles={}
 for poly,parent_face,region,host,outcome in pending:
  is_height=cross(*[rational(p)for p in parent_face])!=0
  if is_height:
   expanded=[]
   for a,b in zip(poly,poly[1:]+poly[:1]):
    ax,az=a[0],a[2];bx,bz=b[0],b[2]
    if (ax,az)==(bx,bz):continue
    axis=0 if ax!=bx else 1
    nodes=sorted((q for q in projected_nodes if on_segment((ax,az),(bx,bz),q)),key=lambda q:(q[axis]-(ax,az)[axis])/((bx,bz)[axis]-(ax,az)[axis]))
    assert nodes[0]==(ax,az)and nodes[-1]==(bx,bz)
    for x,z in nodes[:-1]:expanded.append((x,parent_plane_height((x,F(0),z),parent_face),z))
   assert len(expanded)>=3
   centre=tuple(sum(p[k]for p in expanded)/len(expanded)for k in range(3));vertices=[centre,*expanded]
   fans=[(0,i+1,(i+1)%len(expanded)+1)for i in range(len(expanded))if nondegenerate([centre,expanded[i],expanded[(i+1)%len(expanded)]])]
  else:
   vertices=poly;fans=[(0,i,i+1)for i in range(1,len(poly)-1)if nondegenerate([poly[0],poly[i],poly[i+1]])]
  for p in vertices:
   key=tuple(float(v)for v in np.asarray([float(p[0]),float(p[2])],dtype=np.float32))
   if is_height:
    tags=roles.setdefault(key,set())
    if region=='core'or boundary(p,core_rings):tags.add('one')
    if region=='zero-collar'or boundary(p,[list(blend_outer.exterior.coords),*[list(r.coords)for r in blend_outer.interiors]]):tags.add('zero')
  prepared.append((vertices,fans,parent_face,region,is_height,host,outcome))
 for tags in roles.values():assert tags!={'one','zero'},'Packed core and zero-collar role anchors collapse; no epsilon credit'
 # Actual finite upper heights at packed XZ, not unrounded plane evaluations.
 # This is explicitly changed terrain; no exact original-plane claim.
 def height_inventory(triangles):
  polygons=[];ids=[]
  for i,t in enumerate(triangles):
   if cross(*[rational(p)for p in t])!=0:polygons.append(shapely.Polygon(t[:,[0,2]]));ids.append(i)
  return shapely.STRtree(polygons),ids
 base_tree,base_ids=height_inventory(base);old_tree,old_ids=height_inventory(old)
 def finite_upper(key,triangles,index_tree,ids):
  q=(F(key[0]),F(0),F(key[1]));vals=[]
  for k in sorted(map(int,index_tree.query(shapely.Point(*key)))):
   t=triangles[ids[k]];p=[rational(v)for v in t];sign=cross(*p)
   edge_signs=[cross(p[i],p[(i+1)%3],q)for i in range(3)]
   if all(v>=0 for v in edge_signs)if sign>0 else all(v<=0 for v in edge_signs):vals.append(parent_plane_height(q,t))
  assert vals,'Actual packed finite terrain domain missing; no plane extrapolation'
  return max(vals)
 height_cache={}
 for vertices,fans,parent_face,region,is_height,host,outcome in prepared:
  packed=[];vertex_records=[]
  for p in vertices:
   key=tuple(float(v)for v in np.asarray([float(p[0]),float(p[2])],dtype=np.float32))
   if is_height:
    tags=roles[key]
    alpha=1.0 if 'one'in tags else 0.0 if 'zero'in tags else max(0.0,min(1.0,1.0-shapely.Point(*key).distance(core)/.008))
    parent_coeff=exact_plane([rational(v)for v in parent_face])
    host_coeff=exact_plane([rational(v)for v in host])if host is not None else None
    # Distinct genuine finite branches NEVER share a vertex-height cache.
    # Exact source finite cell ownership was proved before packing. Any
    # rounded vertex outside its authored finite facet remains an explicit
    # changed-terrain extension fact, never source/domain/root credit.
    branch_key=(key,parent_coeff,host_coeff)
    if branch_key not in height_cache:
     q=(F(key[0]),F(0),F(key[1]));py=branch_height(q,parent_coeff)
     by=branch_height(q,host_coeff)if host_coeff is not None else finite_upper(key,base,base_tree,base_ids)
     y=float(py)*alpha+float(by)*(1-alpha);v=np.asarray([key[0],y,key[1]],dtype=np.float32).astype(float)
     height_cache[branch_key]=(v,alpha,py,by)
    v,alpha,py,by=height_cache[branch_key];err=F(float(v[1]))-parent_plane_height(rational(v),parent_face)if region=='core'else None
    if err is not None:height_errors.append(float(abs(err)))
   else:
    # Original nonheight fragments retained and separately inventoried; no
    # height field/root credit from them or collapsed/zero-area facets.
    v=np.asarray([float(x)for x in p],dtype=np.float32).astype(float);alpha=None;py=by=err=None
   assert np.isfinite(v).all();packed.append(v)
   actual_base_upper=finite_upper(key,base,base_tree,base_ids)if is_height else None
   actual_parent_upper=finite_upper(key,old,old_tree,old_ids)if is_height else None
   parent_r=[rational(vv)for vv in parent_face];parent_r=parent_r if cross(*parent_r)>0 else list(reversed(parent_r))
   host_r=[rational(vv)for vv in host]if is_height and host is not None else None
   if host_r is not None and cross(*host_r)<0:host_r.reverse()
   packed_q=(F(key[0]),F(0),F(key[1]))
   vertex_records.append(dict(actualClosedCandidateUpperYAtPackedXZ=str(actual_base_upper)if actual_base_upper is not None else None,actualClosedParentUpperYAtPackedXZ=str(actual_parent_upper)if actual_parent_upper is not None else None,selectedCandidateFiniteFacetContainsPackedXZ=branch_contains(packed_q,host_r)if host_r is not None else None,selectedParentFiniteFacetContainsPackedXZ=branch_contains(packed_q,parent_r)if is_height else None,exactParentClipVertex=[str(x)for x in p],blendAlpha=alpha,packedFloat32Vertex=v.tolist(),corePackedParentHeightDeviationM=str(err)if err is not None else None,branchLocalParentPlaneY=str(py)if py is not None else None,branchLocalCandidateUpperCellPlaneY=str(by)if by is not None else None))
  ids=[]
  for fan in fans:
   tri=np.asarray([packed[i]for i in fan],dtype=float);first=len(mesh['position'])//3;mesh['position'].extend(tri.reshape(-1).tolist());mesh['index'].extend([first,first+1,first+2]);assert len(mesh['index'])//3<=budget
   fid=len(mesh['index'])//3-1;ids.append(fid);added.append(tri)
   if not nondegenerate([rational(p)for p in tri]):packed_degenerate.append(fid)
  outcome.update(completePrepackVertices=vertex_records,completeVertexFanIndices=[list(f)for f in fans],newCandidateFaceIds=ids,allRationalBoundaryVerticesConformedBeforePacking=is_height)
 assert added and mesh['position'][:len(old_position)]==old_position and mesh['index'][:len(old_index)]==old_index
 actual=np.asarray(added,dtype='<f8');projection=finite_projection(actual)
 assert all(not projection.intersects(p)for p in sources.values()),'Packed appended terrain intersects a source arithmetic stream'
 proof=dict(sharedPackedHeightVertexCount=len(height_cache),allRationalClipBoundaryPointsConformedBeforePacking=True,allSharedPackedVerticesUseOneActualFiniteUpperHeight=False,sharedHeightsAreBranchLocal=True,completeUpperCellCertificates=upper_cell_proofs,completeOriginalCandidateFaces=len(base),completeActualParentFaces=len(old),completeAddedTerrainFaces=len(actual),finalTerrainFacets=len(mesh['index'])//3,originalCandidatePositionAndIndexPrefixesUnchanged=True,completeOriginalParentFacetDispositions=records,exactCoreRegionPartition=core_part,exactApronRegionPartition=apron_part,exactZeroAlphaCollarRegionPartition=collar_part,declaredZeroAlphaCollarWidthM=.002,declaredBlendWidthM=margin-.002,actualProtectedCoreGeoJSON=shapely.to_geojson(core),declaredOuterEnvelopeGeoJSON=shapely.to_geojson(outer),sourceStreamDistancesM={k:outer.distance(p)for k,p in sources.items()},completeAddedFloat32TriangleSHA256=digest(actual.tobytes()),maxCorePackedParentHeightDeviationM=max(height_errors,default=0),exactParentPlanePreservationClaimed=False,allParentNonheightClipFaceIds=sorted(set(nonheight)),packedDegenerateAddedFaceIds=packed_degenerate,unchangedTerrainBudget=budget,declaredTransitionWidthM=margin,terrainRepresentationChanges=True,governmentBuildingGeometryChanges=0,physicalAccepted=False,installationApproved=False,qualification='Separately labelled scripted terrain proposal. Exact finite upper-envelope cells are constructed before packing, with branch-local plane heights preserving genuine finite boundary jumps (no global highest-vertex chord). Rounded points outside finite selected cells are changed-terrain extensions only, requiring complete independent actual finite/seam validation. Original candidate streams remain literal; clipped parent core is explicitly Float32-retessellated, apron is constrained by actual candidate finite planes and has declared alpha1/alpha0 boundaries and a constrained2mm zero-alpha collar with conforming rational boundary segmentation and shared actual packed finite-height vertices INSIDE the same1cm envelope (no seam tolerance change). Exact packed actor coverage, all finite seams/heights/upper-branch continuity, source original/literal/F32 clearance, complete BASIC/native/foreign/runtime gates remain mandatory. No original-plane equivalence or numeric waiver.')
 return out,proof
