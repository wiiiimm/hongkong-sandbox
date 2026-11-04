import copy
import unittest
import numpy as np
import shapely
from float32_native_seam_cover_v1_20261025 import cover
from native_patch_resolution import projected_context


def fixture(width):
    x, z = 4700., -6400.
    triangles = []
    for lo, hi in [(x, x+1), (x+1+width, x+2)]:
        points = [[lo, 4., z], [hi, 4., z], [hi, 4., z+1], [lo, 4., z+1]]
        triangles.extend([[points[i] for i in ids] for ids in [(0,1,2),(0,2,3)]])
    for low, high in [(z,z+.125),(z+.875,z+1)]:
        points = [[x+1,4.,low],[x+1+width,4.,low],[x+1+width,4.,high],[x+1,4.,high]]
        triangles.extend([[points[i] for i in ids] for ids in [(0,1,2),(0,2,3)]])
    return {'nativeMesh': {'position': np.array(triangles).reshape(-1).tolist(), 'index': list(range(24))}}, (x,z,x+2,z+1)


class SeamTests(unittest.TestCase):
    def test_closed_float32_gap_is_covered_without_changing_old_terrain(self):
        patch, bounds = fixture(.00048828125)
        before = copy.deepcopy(patch)
        proof = cover(patch, bounds)
        old = before['nativeMesh']
        self.assertEqual(patch['nativeMesh']['position'][:len(old['position'])], old['position'])
        self.assertEqual(patch['nativeMesh']['index'][:len(old['index'])], old['index'])
        _, polygons, missing, _ = projected_context(patch, bounds)
        self.assertLess(missing.area, 1e-10)
        union = shapely.union_all(polygons)
        for z in np.linspace(bounds[1], bounds[3], 7):
            self.assertTrue(union.covers(shapely.Point(bounds[0]+1.000244140625,z)))
        self.assertEqual(proof['unchangedOriginalTerrainTriangles'],8)

    def test_material_gap_is_rejected_before_mutation(self):
        patch, bounds = fixture(.01)
        before = copy.deepcopy(patch)
        with self.assertRaises(AssertionError):
            cover(patch, bounds)
        self.assertEqual(patch,before)


if __name__ == '__main__':
    unittest.main()
