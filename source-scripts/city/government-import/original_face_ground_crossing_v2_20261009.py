"""Versioned coverage correction; original face minimum algorithm unchanged.

Coverage uses full original terrain polygons. Unioning separately clipped
intersection fragments can introduce floating seams and false uncovered lines.
"""
import numpy as np
import shapely
from original_face_ground_crossing_20261009 import face_ground_context as previous_context


def face_ground_context(face, ground, polygons=None, tree=None):
    face,ground=np.asarray(face,dtype=float),np.asarray(ground,dtype=float)
    if polygons is None:
        polygons=shapely.polygons(ground[:,:,[0,2]])
    if tree is None:
        tree=shapely.STRtree(polygons)
    result=previous_context(face,ground,polygons,tree)
    projection=shapely.MultiPoint(face[:,[0,2]]).convex_hull
    hits=tree.query(projection,predicate='intersects')
    union=shapely.union_all(polygons[hits])
    missing=projection.difference(union)
    result.update(clippedUnionCoverageDiagnostic=result['groundProjectionCovered'],
        groundProjectionCovered=bool(union.covers(projection)),
        uncoveredProjectionLengthM=float(missing.length),uncoveredProjectionAreaM2=float(missing.area),
        coverageMethod='Union of full original intersecting ground facets; no buffer or tolerance credit')
    return result
