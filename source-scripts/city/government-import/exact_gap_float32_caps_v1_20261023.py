"""Finite Float32 terrain gap caps; never modifies a source building mesh."""
from fractions import Fraction
import numpy as np
import shapely
from exact_original_projection_coverage_v2_20261010 import point,cross,signed_area


def bracket(value):
    value=Fraction(value);rounded=np.float32(float(value));assert np.isfinite(rounded)
    current=Fraction.from_float(float(rounded))
    if current==value:return [float(rounded)]
    direction=np.float32(-np.inf if current>value else np.inf)
    other=np.nextafter(rounded,direction)
    result=sorted([float(rounded),float(other)])
    assert Fraction.from_float(result[0])<=value<=Fraction.from_float(result[1])
    return result


def enclosing_hull(rational_xz):
    exact=[tuple(Fraction(v)for v in p)for p in rational_xz];points=[]
    for x,z in exact:points.extend((a,b)for a in bracket(x)for b in bracket(z))
    hull=shapely.MultiPoint(points).convex_hull
    assert hull.geom_type=='Polygon'and hull.area>0
    vertices=[point(p)for p in list(hull.exterior.coords)[:-1]]
    if signed_area(vertices)<0:vertices.reverse()
    assert all(all(cross(a,b,p)>=0 for a,b in zip(vertices,vertices[1:]+vertices[:1]))for p in exact)
    return hull


def height(face,xz):
    a,b,c=face;normal=np.cross(b-a,c-a);assert abs(normal[1])>1e-10
    return a[1]-(normal[0]*(xz[:,0]-a[0])+normal[2]*(xz[:,1]-a[2]))/normal[1]


def lower_cap(hull,ground,polygons,tree):
    ids=[int(i)for i in tree.query(hull,predicate='intersects')]
    levels=[];witnesses=[]
    for i in ids:
        q=shapely.get_coordinates(hull.intersection(polygons[i]))
        if len(q):
            values=height(ground[i],q);levels.extend(values.tolist());witnesses.append(dict(groundFace=i,minY=float(values.min())))
    assert levels,'Gap cap requires authenticated adjacent finite surface'
    floor=float(np.nextafter(np.float32(min(levels)),np.float32(-np.inf)))
    assert 1.2<=floor<min(levels),'New terrain cap violates clamp or raises adjacent ground'
    xz=np.asarray(list(hull.exterior.coords)[:-1]);assert np.array_equal(xz,xz.astype('float32').astype(float))
    vertices=np.column_stack([xz[:,0],np.full(len(xz),floor),xz[:,1]])
    faces=np.asarray([vertices[[0,i,i+1]]for i in range(1,len(vertices)-1)])
    assert np.array_equal(faces,faces.astype('float32').astype(float))
    return faces,dict(floorY=floor,adjacentMinimumY=min(levels),adjacentWitnesses=witnesses,addedFaces=len(faces),hullWKT=hull.wkt)
