"""Diagnostic extrema at exact original source/terrain facet intersections.

No acceptance, surface selection, mesh edits or tolerance changes. A point
between the historic vertex/centroid/rim samples can establish a previously
unsampled contact, but all ordinary complete acceptance checks still apply.
"""
import math
import numpy as np
import shapely


def _clip_band(face, ceiling):
    output = []
    for a, b in zip(face, np.roll(face, -1, axis=0)):
        ain, bin = a[1] <= ceiling, b[1] <= ceiling
        if ain:
            output.append(a)
        if ain != bin:
            fraction = (ceiling - a[1]) / (b[1] - a[1])
            output.append(a + fraction * (b - a))
    return np.asarray(output)


def _height(face, x, z):
    a, b, c = face
    cross = np.cross(b-a, c-a)
    return float(a[1] - (cross[0]*(x-a[0])+cross[2]*(z-a[2]))/cross[1])


def continuous_contact(source, terrain, *, bottom, band=.35):
    source, terrain = np.asarray(source, dtype=float), np.asarray(terrain, dtype=float)
    assert source.ndim == terrain.ndim == 3 and source.shape[1:] == terrain.shape[1:] == (3, 3)
    assert source.size and terrain.size and np.isfinite(source).all() and np.isfinite(terrain).all()
    assert math.isfinite(bottom) and math.isfinite(band) and band >= 0
    determinant = np.cross(terrain[:, 1]-terrain[:, 0], terrain[:, 2]-terrain[:, 0])[:, 1]
    keep = np.abs(determinant) > 1e-10
    terrain_ids = np.flatnonzero(keep)
    ground = terrain[keep]
    polygons = shapely.polygons(ground[:, :, [0, 2]])
    tree = shapely.STRtree(polygons)
    minima, maxima = None, None
    pairs = faces = 0
    vertical_source_faces = 0
    for face_id, face in enumerate(source):
        clipped = _clip_band(face, bottom+band)
        if len(clipped) < 3:
            continue
        normal = np.cross(face[1]-face[0], face[2]-face[0])
        if abs(normal[1]) <= 1e-10:
            vertical_source_faces += 1
            continue
        projected = shapely.Polygon(clipped[:, [0, 2]])
        if projected.area <= 1e-10:
            continue
        faces += 1
        for i in tree.query(projected, predicate='intersects'):
            overlap = projected.intersection(polygons[i])
            for x, z in shapely.get_coordinates(overlap):
                sy, gy = _height(face, x, z), _height(ground[i], x, z)
                # The actual height field is the highest drawn terrain facet.
                # Record this intersection only if this ground face supplies
                # that height; lower overlapping layers grant no contact credit.
                hits = tree.query(shapely.Point(x, z), predicate='intersects')
                highest = max([gy, *(_height(ground[j], x, z) for j in hits)])
                if gy < highest-1e-8:
                    continue
                row = {'gapM':sy-gy, 'position':[float(x),sy,float(z)],
                       'terrainHeight':gy, 'sourceFace':face_id,
                       'terrainFace':int(terrain_ids[i])}
                if minima is None or row['gapM'] < minima['gapM']:
                    minima = row
                if maxima is None or row['gapM'] > maxima['gapM']:
                    maxima = row
            pairs += 1
    return {'minimum':minima, 'maximumAtIntersectionVertices':maxima,
            'continuousMaximumCertified':False, 'projectedLowBandFaces':faces,
            'projectedIntersectionPairs':pairs, 'verticalSourceFacesExcluded':vertical_source_faces,
            'completeLowRimProof':False, 'diagnosticOnly':True, 'publication':False,
            'geometryChanges':0, 'policy':'Exact nonvertical low-band minimum against highest drawn ground. Maximum is observed only at facet intersection vertices; ground-plane crossing lines are not partitioned. Vertical faces and sampled acceptance retained separately.'}
