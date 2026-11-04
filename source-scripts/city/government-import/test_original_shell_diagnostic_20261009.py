import unittest
import numpy as np
from original_shell_diagnostic_20261009 import shell_context


def tetrahedron():
    v = np.array([[0,0,0], [1,0,0], [0,1,0], [0,0,1]], dtype=float)
    return v[[[0,2,1], [0,1,3], [0,3,2], [1,2,3]]]


class OriginalShellTests(unittest.TestCase):
    def test_exact_closed_original(self):
        result = shell_context(tetrahedron(), [0])
        self.assertTrue(result['outwardPositiveVolume'])
        self.assertEqual(result['edgeIncidenceHistogram'], {2:6})
        self.assertAlmostEqual(result['signedVolumeM3'], 1/6)
        self.assertFalse(result['placementAccepted'])

    def test_open_shell_is_not_closed(self):
        self.assertFalse(shell_context(tetrahedron()[:-1], [0])['closedConsistentlyOriented'])

    def test_reversed_single_face_is_not_oriented(self):
        t = tetrahedron(); t[0] = t[0, ::-1]
        self.assertFalse(shell_context(t, [0])['closedConsistentlyOriented'])

    def test_reversed_whole_shell_has_negative_volume(self):
        result = shell_context(tetrahedron()[:, ::-1], [0])
        self.assertTrue(result['closedConsistentlyOriented'])
        self.assertFalse(result['outwardPositiveVolume'])

    def test_nearby_component_not_joined(self):
        t = tetrahedron(); other = t + [2,0,0]
        self.assertEqual(shell_context(np.concatenate([t, other]), [0])['triangles'], 4)

    def test_exact_gap_is_not_repaired(self):
        t = tetrahedron(); t[-1,0,0] += 1e-9
        self.assertFalse(shell_context(t, [0])['closedConsistentlyOriented'])

    def test_duplicate_face_not_manifold(self):
        t = tetrahedron()
        self.assertFalse(shell_context(np.concatenate([t, t[:1]]), [0])['closedConsistentlyOriented'])

    def test_disconnected_reversed_shell_cannot_hide_in_positive_sum(self):
        t = tetrahedron()
        other = t[:, ::-1]*.5 + [2,0,0]
        with self.assertRaises(ValueError):
            shell_context(np.concatenate([t, other]), [0, 4])

    def test_fractional_seed_rejected(self):
        with self.assertRaises(AssertionError):
            shell_context(tetrahedron(), [1.5])


if __name__ == '__main__':unittest.main()
