"""Private exact-plane lower-envelope proposal. Does not approve or publish assets."""
import numpy as np
import shapely
from shapely.geometry import Polygon
from native_patch_resolution import _triangles

def plane(face):
    a,b,c=face;n=np.cross(b-a,c-a)
    if abs(n[1])<=1e-10:raise ValueError('Projected vertical face has no surface plane')
    return np.array([-n[0]/n[1],-n[2]/n[1],a[1]+(n[0]*a[0]+n[2]*a[2])/n[1]])

def lower_region(region,difference):
    """Clip a convex intersection at the exact affine plane crossing."""
    points=list(region.exterior.coords[:-1]);out=[]
    def value(p):return difference[0]*p[0]+difference[1]*p[1]+difference[2]
    for a,b in zip(points,points[1:]+points[:1]):
        va,vb=value(a),value(b)
        if va>0:out.append(a)
        if (va>0)!=(vb>0):
            f=va/(va-vb);out.append((a[0]+f*(b[0]-a[0]),a[1]+f*(b[1]-a[1])))
    result=Polygon(out) if len(out)>=3 else Polygon()
    if not result.is_valid:
        repaired=shapely.make_valid(result)
        assert abs(repaired.area-result.area)<=1e-12
        assert shapely.hausdorff_distance(result,repaired)<=1e-12
        result=repaired
    return result

def lift(region,coefficients):
    result=[]
    parts=list(shapely.get_parts(region)); triangles=[]
    while parts:
        part=parts.pop()
        if part.geom_type in ('MultiPolygon','GeometryCollection'):parts.extend(shapely.get_parts(part))
        elif part.geom_type=='Polygon' and part.area>1e-10:triangles.extend(_triangles(part))
    for p in triangles:
        xz=np.asarray(p.exterior.coords[:3]);y=xz@coefficients[:2]+coefficients[2]
        result.append(np.column_stack([xz[:,0],y,xz[:,1]]))
    return result

def inset_faces(terrain,source):
    terrain=np.asarray(terrain,dtype=float);source=np.asarray(source,dtype=float)
    if not np.isfinite(terrain).all() or not np.isfinite(source).all():raise ValueError('Nonfinite source')
    source_polys=shapely.polygons(source[:,:,[0,2]]);areas=shapely.area(source_polys)
    if (areas<=1e-10).any():raise ValueError('Inset source must consist of nonvertical surface faces')
    union=shapely.union_all(source_polys)
    if abs(float(areas.sum()-union.area))>1e-6:raise ValueError('Inset source has overlapping projected surfaces')
    source_planes=[plane(t) for t in source];tree=shapely.STRtree(source_polys);output=[];lineage=[];changed=[];removedArea=insertedArea=0.
    for i,t in enumerate(terrain):
        p=Polygon(t[:,[0,2]])
        if p.area<=1e-10 or not p.intersects(union):output.append(t);lineage.append(dict(kind='unchanged-terrain',face=i));continue
        tp=plane(t);cuts=[];add=[]
        for j in tree.query(p,predicate='intersects'):
            q=p.intersection(source_polys[j])
            if q.area<=1e-10:continue
            parts=list(shapely.get_parts(q)); regions=[]
            while parts:
                part=parts.pop()
                if part.geom_type=='Polygon':regions.append(part)
                elif part.geom_type in ('MultiPolygon','GeometryCollection'):parts.extend(shapely.get_parts(part))
                else:assert part.area==0
            assert abs(sum(part.area for part in regions)-q.area)<=1e-10
            lower=shapely.union_all([lower_region(part,tp-source_planes[j]) for part in regions])
            if lower.area<=1e-10:continue
            cuts.append(lower);new=lift(lower,source_planes[j]);add.extend((f,int(j)) for f in new);insertedArea+=lower.area
        if not cuts:output.append(t);lineage.append(dict(kind='unchanged-terrain',face=i));continue
        cut=shapely.union_all(cuts);removedArea+=cut.area;changed.append(i)
        for f in lift(p.difference(cut),tp):output.append(f);lineage.append(dict(kind='terrain-plane-fragment',face=i))
        for f,j in add:output.append(f);lineage.append(dict(kind='inset-source-plane-fragment',face=j,terrainFace=i))
    if abs(removedArea-insertedArea)>1e-6:raise ValueError('Overlapping replacement regions')
    return np.asarray(output),dict(changedTerrainFaceIndices=changed,removedProjectedAreaM2=removedArea,insertedProjectedAreaM2=insertedArea,lineage=lineage,policy='Lower envelope of existing terrain and exact bounded source surfaces; no inferred or shifted heights. Original building assets untouched.')
