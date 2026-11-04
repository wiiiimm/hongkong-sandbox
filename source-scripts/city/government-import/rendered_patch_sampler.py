"""Sample and retain an installed terrain patch's actual facets during replacement."""
import numpy as np
import shapely
import native_patch_resolution as patches


class RenderedPatchSampler:
    def __init__(self, patch, fallback, grid):
        self.grid, self.fallback = grid, fallback
        g = patch['meta']['georef']
        x, z = g['bE'] - 834500, 816500 - g['bN']
        self.extent = shapely.box(x, z, x + (patch['w'] - 1) * g['aE'],
                                 z - (patch['h'] - 1) * g['aN'])
        self.faces = self.polygons = self.tree = None
        if patch.get('nativeMesh'):
            faces = patches._faces(patch)
            # Match the runtime height field: vertical retaining faces have
            # no projected area and cannot provide a height at a point.
            determinant = np.cross(faces[:, 1] - faces[:, 0], faces[:, 2] - faces[:, 0])[:, 1]
            self.faces = faces[np.abs(determinant) > 1e-10]
            self.polygons = shapely.polygons(self.faces[:, :, [0, 2]])
            self.tree = shapely.STRtree(self.polygons)

    @staticmethod
    def height(face, x, z):
        a, b, c = face
        normal = np.cross(b - a, c - a)
        assert abs(normal[1]) > 1e-10, 'vertical-terrain-facet'
        return float(a[1] - (normal[0] * (x - a[0]) + normal[2] * (z - a[2])) / normal[1])

    def ground(self, x, z):
        point = shapely.Point(x, z)
        if not self.extent.covers(point):
            return self.fallback.ground(x, z)
        if self.tree is not None:
            hits = self.tree.query(point, predicate='intersects')
            if len(hits):
                return max(self.height(self.faces[i], x, z) for i in hits)
        return self.grid.ground(x, z)

    def surface_faces(self, protected):
        """Clip existing planes; sampling a coarse grid cannot preserve native detail."""
        output = []
        inside = protected.intersection(self.extent)
        outside = protected.difference(self.extent)
        if self.tree is None:
            output.extend(patches.grid_surface_faces(self.grid, inside))
        elif not inside.is_empty:
            # Preserve the grid only in numerical holes in the original TIN.
            covered = []
            for i in self.tree.query(inside, predicate='intersects'):
                face = self.faces[i]
                clipped = self.polygons[i].intersection(inside)
                covered.append(clipped)
                for part in shapely.get_parts(clipped):
                    if part.geom_type != 'Polygon':
                        continue
                    for triangle in patches._triangles(part):
                        output.append([[x, self.height(face, x, z), z]
                                       for x, z in list(triangle.exterior.coords)[:3]])
            gaps = inside.difference(shapely.union_all(covered))
            output.extend(patches.grid_surface_faces(self.grid, gaps))
        output.extend(patches.grid_surface_faces(self.fallback, outside))
        assert output, 'replacement-projection-empty'
        return output


def clip_native_against_retained_facets(patch, retained_count, maximum_passes=4):
    """Remove mixed source/retained overlap after Float32 seam quantisation.

    Retained before-state facets stay untouched. New-source triangles are only
    clipped on their existing planes; all coverage/contact gates still apply.
    """
    assert 0 < retained_count < len(patch['nativeMesh']['index']) // 3
    proof = []
    for _ in range(maximum_passes):
        faces = patches._faces(patch)
        native, retained = faces[:-retained_count], faces[-retained_count:]
        polygons = shapely.polygons(native[:, :, [0, 2]])
        region = shapely.union_all(shapely.polygons(retained[:, :, [0, 2]]))
        overlap = shapely.union_all(polygons).intersection(region).area
        if overlap <= .25:
            break
        output = []
        for face, polygon in zip(native, polygons):
            remainder = polygon.difference(region)
            if remainder.equals(polygon):
                output.append(face)
                continue
            for part in shapely.get_parts(remainder):
                if part.geom_type != 'Polygon':
                    continue
                for triangle in patches._triangles(part):
                    output.append([[x, RenderedPatchSampler.height(face, x, z), z]
                                   for x, z in list(triangle.exterior.coords)[:3]])
        flat = np.concatenate((np.asarray(output).reshape(-1, 3), retained.reshape(-1, 3)))
        patch['nativeMesh']['position'] = flat.reshape(-1).tolist()
        patch['nativeMesh']['index'] = list(range(len(flat)))
        proof.append({'mixedOverlapBeforeM2': float(overlap), 'nativeTrianglesAfter': len(output)})
    faces = patches._faces(patch)
    regions = [shapely.union_all(shapely.polygons(f[:, :, [0, 2]]))
               for f in (faces[:-retained_count], faces[-retained_count:])]
    return {'passes': proof, 'mixedOverlapAfterM2': float(regions[0].intersection(regions[1]).area),
            'retainedTriangles': retained_count,
            'policy': 'Clip only new-source facets against exact Float32 retained-facet projection; retained planes unchanged, no overlap or clearance gate waived.'}


def remove_coplanar_duplicates(patch, maximum_passes=2):
    """Remove only overlapping terrain fragments on the same original plane.

    Different-height surfaces are never selected or lowered. Later fragments
    are clipped against earlier coplanar fragments in stable index order.
    Quantised coverage, source contact and neighbour checks remain mandatory.
    """
    proof = []
    for _ in range(maximum_passes):
        faces = patches._faces(patch)
        polygons = shapely.polygons(faces[:, :, [0, 2]])
        tree = shapely.STRtree(polygons)
        first, second = tree.query(polygons, predicate='intersects')
        masks = {}
        for i, j in zip(first, second):
            if i >= j:
                continue
            overlap = polygons[i].intersection(polygons[j])
            if overlap.area <= 1e-8:
                continue
            coords = shapely.get_coordinates(overlap)
            if not len(coords):
                continue
            # Agreement across every overlap vertex establishes equal planes,
            # rather than relying on a single representative point.
            if any(abs(RenderedPatchSampler.height(faces[i], x, z) -
                       RenderedPatchSampler.height(faces[j], x, z)) > 1e-8
                   for x, z in coords):
                continue
            masks.setdefault(int(j), []).append(polygons[i])
        if not masks:
            break
        output = []
        removed = 0.0
        for j, (face, polygon) in enumerate(zip(faces, polygons)):
            if j not in masks:
                output.append(face)
                continue
            remainder = polygon.difference(shapely.union_all(masks[j]))
            removed += polygon.area - remainder.area
            for part in shapely.get_parts(remainder):
                if part.geom_type != 'Polygon':
                    continue
                for triangle in patches._triangles(part):
                    output.append([[x, RenderedPatchSampler.height(face, x, z), z]
                                   for x, z in list(triangle.exterior.coords)[:3]])
        flat = np.asarray(output).reshape(-1, 3)
        patch['nativeMesh']['position'] = flat.reshape(-1).tolist()
        patch['nativeMesh']['index'] = list(range(len(flat)))
        proof.append({'coplanarFragmentsClipped': len(masks),
                      'removedProjectedAreaM2': float(removed)})
    return {'passes': proof, 'policy': 'Remove only duplicate coplanar terrain; no source model geometry changes or acceptance gate waivers.'}
