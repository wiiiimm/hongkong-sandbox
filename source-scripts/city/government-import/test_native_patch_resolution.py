import importlib.util
from pathlib import Path
import unittest

import numpy as np
import shapely

spec = importlib.util.spec_from_file_location('native_patch_resolution', Path(__file__).with_name('native_patch_resolution.py'))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class Sampler:
    def ground(self, x, z):
        return 2.0


class NativePatchResolutionTests(unittest.TestCase):
    def patch(self, gap=.01):
        faces = np.array([
            [[0, 1, 0], [1 - gap, 1, 0], [0, 1, 1]],
            [[1 - gap, 1, 0], [1 - gap, 1, 1], [0, 1, 1]],
            [[1 + gap, 3, 0], [2, 3, 0], [1 + gap, 3, 1]],
            [[2, 3, 0], [2, 3, 1], [1 + gap, 3, 1]],
        ])
        return {'nativeMesh': {'position': faces.reshape(-1).tolist(), 'index': list(range(12)), 'source': {}}}

    def test_fills_bounded_protected_seam_from_source_edges(self):
        patch = self.patch()
        proof = m.fill_narrow_source_seam(patch, [0, 0, 2, 1], shapely.box(.5, 0, 1.5, 1), Sampler(), tolerance=.011)
        self.assertAlmostEqual(proof['protectedAreaM2'], .02)
        self.assertGreater(proof['sourceEdgeTriangles'], 0)
        self.assertAlmostEqual(m.projected_context(patch, [0, 0, 2, 1])[2].area, 0)
        added = np.asarray(patch['nativeMesh']['position']).reshape(-1, 3)[12:]
        self.assertTrue(set(added[:, 1]).issubset({1.0, 3.0}))

    def test_preserves_parent_height_under_unresolved_projection(self):
        patch = self.patch(0)
        proof = m.preserve_parent_under_projection(patch, [0, 0, 2, 1], shapely.box(.75, .25, 1.25, .75), Sampler())
        self.assertAlmostEqual(proof['areaM2'], .25)
        faces = m._faces(patch)
        polygons = shapely.polygons(faces[:, :, [0, 2]])
        centres = faces.mean(axis=1)
        protected = shapely.box(.75, .25, 1.25, .75)
        inside = np.array([protected.contains(shapely.Point(x, z)) for x, _, z in centres])
        self.assertTrue(inside.any())
        self.assertTrue((centres[inside, 1] == 2).all())

    def test_rejects_gap_wider_than_tolerance(self):
        with self.assertRaisesRegex(AssertionError, 'protected-gap-exceeds'):
            m.fill_narrow_source_seam(self.patch(.1), [0, 0, 2, 1], shapely.box(.5, 0, 1.5, 1), Sampler(), tolerance=.02)


if __name__ == '__main__':
    unittest.main()
