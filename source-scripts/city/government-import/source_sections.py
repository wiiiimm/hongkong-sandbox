"""Exact horizontal source sections, for footprint diagnostics only.

The declared height is an input, never selected by optimising footprint fit.
Vertices are not snapped and source triangles are never modified. Open, dangling
or coplanar sections remain explicit; a closed section does not grant acceptance.
"""
import numpy as np
import shapely
from shapely.geometry import LineString, GeometryCollection
from shapely.ops import polygonize_full


def horizontal_section(triangles, height):
    triangles = np.asarray(triangles, dtype=float)
    if triangles.shape != (len(triangles), 3, 3) or not np.isfinite(triangles).all():
        raise ValueError('Finite N×3×3 original world triangles required')
    if not np.isfinite(height):
        raise ValueError('Finite section height required')
    spans = triangles[(triangles[:, :, 1].min(axis=1) <= height)
                      & (triangles[:, :, 1].max(axis=1) >= height)]
    segments = set()
    coplanar = 0
    point_only = 0
    for face in spans:
        if np.all(face[:, 1] == height):
            coplanar += 1
            continue
        points = set()
        for a, b in zip(face, np.roll(face, -1, axis=0)):
            # Canonical order gives bit-identical intersections on shared edges.
            a, b = sorted((a, b), key=lambda v: tuple(v))
            if a[1] == height:
                points.add((float(a[0]), float(a[2])))
            if b[1] == height:
                points.add((float(b[0]), float(b[2])))
            if min(a[1], b[1]) < height < max(a[1], b[1]):
                p = a + ((height - a[1]) / (b[1] - a[1])) * (b - a)
                points.add((float(p[0]), float(p[2])))
        if len(points) == 2:
            segments.add(tuple(sorted(points)))
        elif len(points) == 1:
            point_only += 1
        elif len(points) > 2:
            raise ValueError('A non-coplanar triangle produced more than two intersections')
    lines = [LineString(s) for s in sorted(segments)]
    # Polygonisation preserves separate ring faces (including courtyard faces).
    # Report these explicitly; their union is only a diagnostic occupied envelope.
    # Source faces can cross one another. Node their exact section intersections
    # before polygonisation; do not snap almost-equal endpoints into closed rings.
    noded = shapely.union_all(lines) if lines else GeometryCollection()
    line_parts = list(noded.geoms) if hasattr(noded, 'geoms') else [noded]
    polygons, cuts, dangles, invalid = polygonize_full(line_parts)
    invalid_faces = sum(not p.is_valid for p in polygons.geoms)
    geometry_error = None
    try:
        envelope = shapely.union_all([p for p in polygons.geoms if p.is_valid])
    except shapely.errors.GEOSException as error:
        # Preserve the failure rather than infer a repaired occupied footprint.
        geometry_error = str(error)
        envelope = GeometryCollection()
    return envelope, {
        'heightHKPD': float(height), 'intersectingTriangles': len(spans),
        'uniqueSegments': len(segments), 'coplanarTriangles': coplanar,
        'pointOnlyTriangles': point_only, 'closedPolygonFaces': len(polygons.geoms),
        'cutEdges': len(cuts.geoms), 'danglingEdges': len(dangles.geoms),
        'invalidRings': len(invalid.geoms), 'invalidPolygonFaces': invalid_faces,
        'geometryError': geometry_error, 'nodedSegments': len(line_parts),
        'closedEnvelopeAreaM2': float(envelope.area),
        'completeClosedLinework': bool(lines) and not (coplanar or invalid_faces or geometry_error or len(cuts.geoms)
                                                      or len(dangles.geoms) or len(invalid.geoms)),
        'qualification': 'Diagnostic envelope only; courtyard faces are not inferred occupied floors. No source identity, component membership or installation approval.'}
