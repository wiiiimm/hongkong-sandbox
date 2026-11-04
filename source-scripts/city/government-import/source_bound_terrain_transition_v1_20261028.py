"""Private source-core/parent-apron terrain construction; no building edits.

Core facets retain their old planes. Transition fragments are split at original
parent grid edges/diagonals. Every exterior fragment uses its exact parent plane.
Vertical source triangles are clipped in their finite projected line parameter.
"""
import numpy as np
import shapely
from native_patch_resolution import _triangles


def plane(face):
    a, b, c = face
    n = np.cross(b-a, c-a)
    assert n[1] != 0
    return np.array([-n[0]/n[1], -n[2]/n[1], a[1]+(n[0]*a[0]+n[2]*a[2])/n[1]])


def heights(coeff, xz):
    return np.asarray(xz) @ coeff[:2] + coeff[2]


def parent_faces(parent, cells):
    g, w = parent['meta']['georef'], parent['w']
    assert g['aE'] > 0 and g['aN'] == -g['aE']
    def vertex(c, r):
        k = r*w+c
        rendered = parent.get('renderedElev', [])
        y = rendered[k] if rendered else None
        if y is None:
            y = max(1.2, parent['elev'][k]) if parent['elev'][k] > 0 else -4
        return [g['bE']+c*g['aE']-834500, y, 816500-g['bN']-r*g['aN']]
    result = []
    for r in range(cells[1], cells[3]):
        for c in range(cells[0], cells[2]):
            a, b, d, e = [vertex(x, z) for x, z in [(c, r), (c+1, r), (c, r+1), (c+1, r+1)]]
            # Same finite grid triangles as the renderer; upward winding.
            result.extend([[a, d, b], [b, d, e]])
    return np.asarray(result, dtype=float)


def clip_interval(face, axis, low, high):
    points = list(np.asarray(face, dtype=float))
    for limit, direction in [(low, 1), (high, -1)]:
        output = []
        if not points:
            return []
        for a, b in zip(points, points[1:] + points[:1]):
            ia, ib = direction*(a[axis]-limit) >= 0, direction*(b[axis]-limit) >= 0
            if ia:
                output.append(a.copy())
            if ia != ib:
                point = a + (b-a)*((limit-a[axis])/(b[axis]-a[axis]))
                point[axis] = limit
                output.append(point)
        points = output
    return points


def weights(xz, core, outer):
    points = shapely.points(np.asarray(xz))
    inside = shapely.covers(core, points)
    beyond = ~shapely.covers(outer, points)
    dc, do = shapely.distance(points, core), shapely.distance(points, outer.boundary)
    total = dc+do
    assert np.all(total > 0)
    # This ratio is exactly1 on the core and0 on the actual polygonal outer
    # boundary; round-buffer chord error must not create a root-height step.
    alpha = np.clip(do/total, 0, 1)
    alpha[inside] = 1
    alpha[beyond] = 0
    return alpha


def build(old, parent, core, outer, domain, progress=None):
    old, parent = np.asarray(old, float), np.asarray(parent, float)
    assert old.shape[1:] == parent.shape[1:] == (3, 3)
    assert np.isfinite(old).all() and np.isfinite(parent).all()
    assert core.is_valid and outer.is_valid and outer.covers(core) and domain.covers(outer)
    root_polys = shapely.polygons(parent[:, :, [0, 2]])
    root_planes = np.asarray([plane(f) for f in parent])
    tree = shapely.STRtree(root_polys)
    transition = outer.difference(core)
    output, lineage = [], []
    metrics = dict(unchangedCoreFaces=0, clippedCoreFaces=0, transitionFaces=0,
                   exteriorParentFaces=0, omittedExteriorOldFaces=0,
                   verticalInputFaces=0, verticalCoreFaces=0, verticalTransitionFaces=0,
                   maximumCoreAreaConservationErrorM2=0., maximumPolygonTriangulationAreaLossM2=0.)

    def append(face, kind, source, root=None, normal=None):
        face = np.asarray(face, float)
        if normal is not None and np.dot(np.cross(face[1]-face[0], face[2]-face[0]), normal) < 0:
            face = face[[0, 2, 1]]
        output.append(face)
        lineage.append(dict(kind=kind, originalFace=source, parentFace=root))

    def emit(region, coeff, kind, source, root, normal, blend=False):
        parts = _triangles(region)
        loss = abs(region.area-sum(p.area for p in parts))
        metrics['maximumPolygonTriangulationAreaLossM2'] = max(metrics['maximumPolygonTriangulationAreaLossM2'], loss)
        before = len(output)
        for poly in parts:
            xz = np.asarray(poly.exterior.coords[:3])
            y = heights(coeff, xz)
            if blend:
                alpha = weights(xz, core, outer)
                y = alpha*y + (1-alpha)*heights(root_planes[root], xz)
            append(np.column_stack([xz[:, 0], y, xz[:, 1]]), kind, source, root, normal)
        return before, len(output)

    for index, face in enumerate(old):
        normal = np.cross(face[1]-face[0], face[2]-face[0])
        poly = shapely.Polygon(face[:, [0, 2]])
        if normal[1] != 0:
            if core.covers(poly):
                append(face.copy(), 'unchanged-core', index)
                metrics['unchangedCoreFaces'] += 1
            elif outer.disjoint(poly):
                metrics['omittedExteriorOldFaces'] += 1
            else:
                coeff = plane(face)
                inside = poly.intersection(core)
                start, end = emit(inside, coeff, 'clipped-core', index, None, normal)
                metrics['clippedCoreFaces'] += end-start
                expected = inside.area * np.linalg.norm(normal)/abs(normal[1])
                area = sum(np.linalg.norm(np.cross(f[1]-f[0], f[2]-f[0]))/2 for f in output[start:end])
                metrics['maximumCoreAreaConservationErrorM2'] = max(metrics['maximumCoreAreaConservationErrorM2'], abs(area-expected))
                band = poly.intersection(transition)
                for root in tree.query(band, predicate='intersects'):
                    root = int(root)
                    part = band.intersection(root_polys[root])
                    a, b = emit(part, coeff, 'transition', index, root, normal, blend=True)
                    metrics['transitionFaces'] += b-a
        else:
            metrics['verticalInputFaces'] += 1
            xz = face[:, [0, 2]]
            line = shapely.LineString(xz)
            if core.covers(line):
                append(face.copy(), 'unchanged-core-vertical', index)
                metrics['verticalCoreFaces'] += 1
                continue
            if outer.disjoint(line):
                metrics['omittedExteriorOldFaces'] += 1
                continue
            axis = 0 if np.ptp(face[:, 0]) >= np.ptp(face[:, 2]) else 2
            low, high = float(face[:, axis].min()), float(face[:, axis].max())
            if low == high:
                # All projected points coincide. Preserve the degenerate
                # primitive explicitly, applying only the apron height rule.
                roots = tree.query(shapely.Point(xz[0]), predicate='intersects')
                assert len(roots)
                root = int(roots[0])
                result = face.copy(); alpha = weights(xz, core, outer)
                result[:, 1] = alpha*face[:, 1]+(1-alpha)*heights(root_planes[root], xz)
                append(result, 'transition-degenerate', index, root, normal)
                metrics['verticalTransitionFaces'] += 1
                continue
            endpoints = face[np.argmin(face[:, axis])], face[np.argmax(face[:, axis])]
            segment = shapely.LineString([endpoints[0][[0, 2]], endpoints[1][[0, 2]]])
            root_ids = tree.query(segment, predicate='intersects')
            events = {low, high}
            for boundary in [core.boundary, outer.boundary, *[root_polys[i].boundary for i in root_ids]]:
                coordinates = shapely.get_coordinates(segment.intersection(boundary))
                events.update(float(p[0 if axis == 0 else 1]) for p in coordinates)
            events = sorted(max(low, min(high, p)) for p in events)
            for lo, hi in zip(events, events[1:]):
                if hi <= lo:
                    continue
                fraction = ((lo+hi)/2-low)/(high-low)
                midpoint = endpoints[0]+fraction*(endpoints[1]-endpoints[0])
                point = shapely.Point(midpoint[[0, 2]])
                in_core = core.covers(point)
                if not in_core and not outer.covers(point):
                    continue
                roots = [int(i) for i in root_ids if root_polys[i].covers(point)]
                assert roots, 'Vertical interval has no finite parent triangle'
                root = roots[0]
                points = clip_interval(face, axis, lo, hi)
                for k in range(1, len(points)-1):
                    result = np.asarray([points[0], points[k], points[k+1]])
                    if not in_core:
                        xz = result[:, [0, 2]]; alpha = weights(xz, core, outer)
                        result[:, 1] = alpha*result[:, 1]+(1-alpha)*heights(root_planes[root], xz)
                    append(result, 'clipped-core-vertical' if in_core else 'transition-vertical', index, root, normal)
                    metrics['verticalCoreFaces' if in_core else 'verticalTransitionFaces'] += 1
        if progress and index % 5000 == 0:
            progress(index, len(output))
    exterior = domain.difference(outer)
    for root, (face, poly) in enumerate(zip(parent, root_polys)):
        a, b = emit(poly.intersection(exterior), root_planes[root], 'exterior-parent', None, root,
                    np.cross(face[1]-face[0], face[2]-face[0]))
        metrics['exteriorParentFaces'] += b-a
    assert output and len(output) == len(lineage)
    return np.asarray(output), lineage, metrics
