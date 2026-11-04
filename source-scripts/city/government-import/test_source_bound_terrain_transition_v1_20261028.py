"""Geometric counterexamples for the private source-bound terrain apron."""
import unittest
import numpy as np
import shapely
from source_bound_terrain_transition_v1_20261028 import build, plane, heights, weights


class TransitionTests(unittest.TestCase):
    def setUp(self):
        self.root = np.asarray([[[0, 5, 0], [0, 5, 4], [4, 5, 0]],
                                [[4, 5, 0], [0, 5, 4], [4, 9, 4]]], float)
        self.old = self.root.copy(); self.old[:, :, 1] = 10
        self.core, self.outer, self.domain = shapely.box(1, 1, 3, 3), shapely.box(.5, .5, 3.5, 3.5), shapely.box(0, 0, 4, 4)

    def height(self, mesh, x, z):
        found = []
        for face in mesh:
            if np.cross(face[1]-face[0], face[2]-face[0])[1] == 0:
                continue
            if shapely.Polygon(face[:, [0, 2]]).covers(shapely.Point(x, z)):
                found.append(float(heights(plane(face), [[x, z]])[0]))
        self.assertTrue(found)
        return max(found)

    def test_core_and_exterior_follow_different_exact_surfaces(self):
        mesh, _, _ = build(self.old, self.root, self.core, self.outer, self.domain)
        for x, z in [(1.5, 1.5), (2.5, 2.5)]:
            self.assertAlmostEqual(self.height(mesh, x, z), 10)
        for x, z in [(.1, .2), (3.9, 3.7), (3.9, .1)]:
            self.assertAlmostEqual(self.height(mesh, x, z), self.height(self.root, x, z))

    def test_parent_diagonal_is_never_bridged(self):
        mesh, records, _ = build(self.old, self.root, self.core, self.outer, self.domain)
        for face, record in zip(mesh, records):
            if record['kind'] == 'exterior-parent':
                parent = self.root[record['parentFace']]
                self.assertTrue(shapely.Polygon(parent[:, [0, 2]]).covers(shapely.Polygon(face[:, [0, 2]])))
                np.testing.assert_allclose(face[:, 1], heights(plane(parent), face[:, [0, 2]]), atol=1e-12)

    def test_complete_projected_domain_coverage(self):
        mesh, _, audit = build(self.old, self.root, self.core, self.outer, self.domain)
        union = shapely.union_all(shapely.polygons(mesh[:, :, [0, 2]]))
        self.assertLess(union.symmetric_difference(self.domain).area, 1e-10)
        self.assertLess(audit['maximumCoreAreaConservationErrorM2'], 1e-10)

    def test_vertical_core_has_conserved_three_dimensional_area(self):
        vertical = np.array([[2, 8, 0], [2, 8, 4], [2, 12, 4]], float)
        mesh, records, _ = build(np.concatenate([self.old, vertical[None]]), self.root, self.core, self.outer, self.domain)
        pieces = [f for f, r in zip(mesh, records) if r['kind'] == 'clipped-core-vertical']
        self.assertTrue(pieces)
        self.assertAlmostEqual(sum(np.linalg.norm(np.cross(f[1]-f[0], f[2]-f[0]))/2 for f in pieces), 4)
        for face in pieces:
            np.testing.assert_equal(face[:, 0], 2)

    def test_vertical_face_on_parent_diagonal(self):
        face = np.array([[0, 8, 4], [4, 8, 0], [4, 12, 0]], float)
        mesh, records, _ = build(np.concatenate([self.old, face[None]]), self.root, self.core, self.outer, self.domain)
        self.assertTrue(any(r['kind'] == 'transition-vertical' for r in records))
        self.assertTrue(np.isfinite(mesh).all())

    def test_actual_polygonal_buffer_boundary_has_zero_native_weight(self):
        outer = self.core.buffer(.5, quad_segs=2)
        points = np.asarray(outer.exterior.coords)
        np.testing.assert_allclose(weights(points, self.core, outer), 0, atol=1e-12)
        np.testing.assert_allclose(weights(np.array([[1, 1], [2, 2]]), self.core, outer), 1)

    def test_source_core_cannot_be_truncated_to_domain(self):
        with self.assertRaises(AssertionError):
            build(self.old, self.root, self.core, shapely.box(-1, -1, 5, 5), self.domain)


if __name__ == '__main__':
    unittest.main()
