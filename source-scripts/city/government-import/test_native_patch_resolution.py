import copy
import hashlib
import importlib.util
import json
from pathlib import Path
from tempfile import TemporaryDirectory
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

    def test_accepts_numerically_complete_parent_coverage_without_new_triangles(self):
        patch = self.patch(0)
        proof = m.fill_parent_only_holes(patch, {}, [0, 0, 2, 1], shapely.box(.25, .25, .75, .75), Sampler())
        self.assertEqual(proof["triangles"], 0)
        self.assertLessEqual(proof["missingAreaM2"], 1e-8)
        self.assertEqual(len(patch["nativeMesh"]["index"]), 12)

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

    def test_snaps_new_patch_edge_vertices_to_parent_height(self):
        patch = self.patch(0)
        m.preserve_parent_under_projection(patch, [0, 0, 2, 1], shapely.box(.5, 0, 1.5, .5), Sampler())
        points = np.asarray(patch['nativeMesh']['position']).reshape(-1, 3)
        edge = points[np.isclose(points[:, 2], 0)]
        self.assertGreater(len(edge), 0)
        self.assertTrue((edge[:, 1] == 2).all())

    def test_preserves_piecewise_linear_parent_across_grid_diagonal(self):
        class GridSampler:
            def __init__(self):
                self.g = {'aE': 1, 'aN': -1, 'bE': 834500, 'bN': 816500}
                self.w = 2
                self.dem = {'w': 2, 'h': 2, 'elev': [0, 0, 0, 10]}
            def ground(self, x, z):
                return 0 if x + z <= 1 else 10 * (x + z - 1)
        patch = self.patch(0)
        sampler = GridSampler()
        m.preserve_parent_under_projection(patch, [0, 0, 2, 1], shapely.box(.25, .25, .75, .75), sampler)
        faces = m._faces(patch)
        protected = shapely.box(.25, .25, .75, .75)
        for face in faces:
            centre = face.mean(axis=0)
            if protected.contains(shapely.Point(centre[0], centre[2])):
                self.assertAlmostEqual(centre[1], sampler.ground(centre[0], centre[2]), places=10)

    def test_finalizes_overlap_proof_after_deterministic_patch_changes(self):
        patch = self.patch(0)
        patch['nativeMesh']['sourceOverlap'] = {'policy': 'highest-native-surface', 'evidenceSHA256': 'stale'}
        patch['nativeMesh']['source']['parentHoleFill'] = {'triangles': 2}
        with TemporaryDirectory() as folder:
            evidence = Path(folder) / 'overlap.json'
            evidence.write_text(json.dumps({'stagedGeometrySha256': 'stale'}) + '\n')
            proof = m.finalize_overlap_evidence(patch, evidence)
            original = copy.deepcopy(patch)
            original['nativeMesh'].pop('sourceOverlap')
            expected = hashlib.sha256((json.dumps(original, separators=(',', ':')) + '\n').encode()).hexdigest()
            self.assertEqual(proof['stagedGeometrySha256'], expected)
            self.assertEqual(json.loads(evidence.read_text())['stagedGeometrySha256'], expected)
            self.assertEqual(proof['evidenceSHA256'], hashlib.sha256(evidence.read_bytes()).hexdigest())

    def test_rejects_gap_wider_than_tolerance(self):
        with self.assertRaisesRegex(AssertionError, 'protected-gap-exceeds'):
            m.fill_narrow_source_seam(self.patch(.1), [0, 0, 2, 1], shapely.box(.5, 0, 1.5, 1), Sampler(), tolerance=.02)


if __name__ == '__main__':
    unittest.main()
