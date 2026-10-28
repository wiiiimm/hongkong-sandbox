import unittest
import numpy as np
from finite_terrain_two_way_partition_v1_20261028 import partition


class PartitionTests(unittest.TestCase):
    def test_surface_vertical_and_degenerate_conservation(self):
        faces = np.array([
            [[-1, 0, 0], [1, 2, 0], [1, 2, 2]],
            [[0, 0, 0], [0, 3, 0], [0, 3, 2]],
            [[-1, 1, 0], [-1, 1, 0], [-1, 1, 0]],
        ], float)
        parts, proof = partition(faces, 0.)
        self.assertFalse(proof['missingParentFaces'])
        self.assertFalse(proof['missingOriginalVertices'])
        self.assertNotIn(1, parts['west']['parentFaceIndices'])
        self.assertEqual(parts['east']['parentFaceIndices'].count(1), 1)
        self.assertLess(proof['maximumSourcePlaneHeightDriftM'], 1e-12)
        for name, sign in [('west', -1), ('east', 1)]:
            self.assertTrue((parts[name]['triangles'][:, :, 0]*sign >= 0).all())

    def test_nonfinite_and_empty_side_rejected(self):
        for face in [np.full((1, 3, 3), np.nan),
                     np.array([[[1, 0, 0], [2, 1, 0], [1, 0, 1]]])]:
            with self.assertRaises(AssertionError):
                partition(face, 0.)


if __name__ == '__main__':
    unittest.main()
