import unittest
import numpy as np
from original_face_edge_context_v1_20261027 import inspect_faces


class ExactEdgeContext(unittest.TestCase):
    def setUp(self):
        self.a = [[0, 0, 0], [0, 0, 1], [1, 0, 0]]
        self.b = [[1, 0, 0], [0, 0, 1], [1, 0, 1]]

    def test_exact_shared_edge_and_upward_orientation(self):
        r = inspect_faces([self.a, self.b], [0])
        self.assertEqual([x['sourceFace'] for x in r['rows'][0]['edgeNeighbours']], [1])
        self.assertEqual(r['rows'][0]['signedNormalY'], 1)
        self.assertEqual(r['components'][0]['sourceFaces'], [0, 1])
        self.assertEqual(r['components'][0]['unmatchedRepresentedEdges'], 4)
        self.assertFalse(r['physicalAcceptance'])

    def test_point_contact_does_not_join(self):
        b = [[0, 0, 0], [-1, 0, 0], [0, 0, -1]]
        r = inspect_faces([self.a, b], [0, 1])
        self.assertEqual(len(r['components']), 2)

    def test_near_edge_does_not_join(self):
        b = np.asarray(self.b, float) + [0, 1e-12, 0]
        self.assertEqual(len(inspect_faces([self.a, b], [0, 1])['components']), 2)

    def test_partial_edge_does_not_join(self):
        b = [[0, 0, 1], [.5, 0, .5], [1, 0, 1]]
        self.assertEqual(len(inspect_faces([self.a, b], [0, 1])['components']), 2)

    def test_degenerate_face_cannot_bridge(self):
        r = inspect_faces([self.a, self.b, [[0, 0, 1], [1, 0, 0], [.5, 0, .5]]], [2])
        self.assertIsNone(r['rows'][0]['componentId'])
        self.assertEqual(r['rows'][0]['edgeNeighbours'], [])

    def test_invalid_indices_or_nonfinite_coordinates_fail(self):
        for ids in [[-1], [1], [0, 0], []]:
            with self.assertRaises(AssertionError):
                inspect_faces([self.a], ids)
        with self.assertRaises(AssertionError):
            inspect_faces([[[float('nan'), 0, 0], [1, 0, 0], [0, 0, 1]]], [0])


if __name__ == '__main__':
    unittest.main()
