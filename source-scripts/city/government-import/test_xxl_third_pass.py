import importlib.util
from pathlib import Path
import unittest
import numpy as np

spec = importlib.util.spec_from_file_location('xxl_third', Path(__file__).with_name('xxl-third-pass.py'))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class SurfaceContextTests(unittest.TestCase):
    def test_buried_downward_foundation_is_distinct_from_buried_roof(self):
        terrain = np.array([[[0, 0, 0], [2, 0, 0], [0, 0, 2]], [[2, 0, 0], [2, 0, 2], [0, 0, 2]]], float)
        upward = np.array([[[0, -1, 0], [0, -1, 1], [1, -1, 0]]], float)
        downward = upward[:, ::-1]
        self.assertEqual(m.surface_context(downward, terrain)['fullyBuriedUpwardTriangles'], 0)
        self.assertEqual(m.surface_context(upward, terrain)['fullyBuriedUpwardTriangles'], 1)

    def test_conservative_route_requires_identity_and_small_foundation(self):
        row = {'projectionCandidates': [{'metrics': {'overlapOfSmaller': .99, 'footprintCovered': .99, 'projectionInsideFootprint': .99, 'centroidDistance': .5}}]}
        context = {'completeTerrainTriangles': 1000, 'triangles': 1000, 'fullyBuriedUpwardTriangles': 0, 'fullyBuriedAreaRatio': .0005}
        self.assertEqual(m.route(row, context)['actionableState'], 'scripted-acceptance-candidate')
        context['fullyBuriedUpwardTriangles'] = 1
        self.assertEqual(m.route(row, context)['actionableState'], 'held-unknown')


if __name__ == '__main__':
    unittest.main()
