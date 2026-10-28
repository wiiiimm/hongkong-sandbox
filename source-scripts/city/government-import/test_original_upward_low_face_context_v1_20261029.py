"""Guard the existing terrain-return nomination threshold and original binding."""
import unittest
import numpy as np
from original_upward_low_face_context_v1_20261029 import upward_ids


class UpwardNomination(unittest.TestCase):
    def setUp(self):
        self.up = np.array([[0., 0., 0.], [0., 0., 1.], [1., 0., 0.]])

    def select(self, triangles, gap):
        t = np.asarray(triangles)
        return upward_ids(t, [dict(sourceFace=i, vertices=v.tolist(), minimumFiniteGapM=gap) for i, v in enumerate(t)])

    def test_exact_half_metre_is_excluded(self):
        self.assertEqual(self.select([self.up], '-1/2'), [])
        self.assertEqual(self.select([self.up], '-5000000000000001/10000000000000000'), [0])

    def test_underside_and_collapsed_faces_are_excluded(self):
        self.assertEqual(self.select([self.up[::-1], np.zeros((3, 3))], '-2'), [])

    def test_clear_upward_surface_is_excluded(self):
        self.assertEqual(self.select([self.up], '1/10'), [])

    def test_changed_original_vertices_fail_closed(self):
        r = dict(sourceFace=0, vertices=self.up.tolist(), minimumFiniteGapM='-1')
        r['vertices'][0][0] = 0.001
        with self.assertRaises(AssertionError):
            upward_ids(np.array([self.up]), [r])


if __name__ == '__main__':
    unittest.main()
