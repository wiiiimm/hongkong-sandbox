"""Account for unchanged zero-area source faces as exact lines/points.

No triangle or source vertex is omitted or repaired. This is a continuous
clearance diagnostic for a non-rendering original primitive, not a source role.
"""
import numpy as np
import shapely
from exact_original_shell_intersections_20261009 import rational_face,cross,sub
from exact_terrain_contact_20261009 import _height
from original_face_ground_crossing_20261009 import _vertical_heights

def degenerate_ground_context(face,ground,polygons,tree):
    face=np.asarray(face,dtype=float);ground=np.asarray(ground,dtype=float)
    exact=rational_face(face)
    assert not any(cross(sub(exact[1],exact[0]),sub(exact[2],exact[0])))
    projection=shapely.MultiPoint(face[:,[0,2]]).convex_hull
    assert projection.geom_type in ('LineString','Point')
    hits=tree.query(projection,predicate='intersects');witnesses=[]
    for j in hits:
        overlap=projection.intersection(polygons[j])
        if overlap.is_empty:continue
        coords=list(shapely.get_coordinates(overlap))
        coords += [v[[0,2]] for v in face if overlap.covers(shapely.Point(v[[0,2]]))]
        for x,z in coords:
            lo,hi=_vertical_heights(face,x,z);gy=_height(ground[j],x,z)
            highest=max([gy,*(_height(ground[k],x,z) for k in tree.query(shapely.Point(x,z),predicate='intersects'))])
            witnesses.append({'minimumGapM':lo-gy,'position':[float(x),lo,float(z)],
                'terrainHeight':gy,'terrainFace':int(j),'upperObservedGapM':hi-highest})
    union=shapely.union_all(polygons[hits]);missing=projection.difference(union)
    return {'sourceDegenerate':True,'originalPrimitive':projection.geom_type,
        'groundProjectionCovered':bool(union.covers(projection)),
        'uncoveredProjectionLengthM':float(missing.length),
        'uncoveredProjectionAreaM2':float(missing.area),
        'minimum':min(witnesses,key=lambda r:r['minimumGapM']) if witnesses else None,
        'maximumObservedGapM':max((r['upperObservedGapM'] for r in witnesses),default=None),
        'continuousMaximumCertified':False,'floatingIntersectionArithmetic':True,
        'groundFacetPairs':len(hits),'normalYRatio':None,'diagnosticOnly':True,
        'geometryChanges':0,'installationApproved':False}
