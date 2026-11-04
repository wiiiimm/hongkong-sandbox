import unittest
from silvercord_buried_wall_grade_context_v1_20261103 import wall_grade_paths


class OriginalWallGradePaths(unittest.TestCase):
    def test_nonzero_shared_original_wall_edge(self):
        tri = [[[0, 0, 0], [1, 0, 0], [0, 1, 0]],
               [[1, 0, 0], [1, 1, 0], [0, 1, 0]]]
        result = wall_grade_paths(tri, [1], [0])
        self.assertEqual(result['unresolvedWallFaces'], [])
        self.assertEqual(result['paths'][0]['originalWallFacePath'], [1, 0])
        self.assertEqual(len(result['paths'][0]['sharedNonzeroOriginalEdges']), 1)

    def test_point_only_contact_does_not_create_wall_path(self):
        tri = [[[0, 0, 0], [1, 0, 0], [0, 1, 0]],
               [[0, 1, 0], [-1, 1, 0], [0, 2, 0]]]
        self.assertEqual(wall_grade_paths(tri, [1], [0])['unresolvedWallFaces'], [1])

    def test_roof_cannot_bridge_separate_walls(self):
        tri = [[[0, 0, 0], [1, 0, 0], [0, 1, 0]],
               [[0, 0, 0], [1, 0, 0], [1, 0, 1]],
               [[1, 0, 0], [1, 0, 1], [1, 1, 1]]]
        self.assertEqual(wall_grade_paths(tri, [2], [0])['unresolvedWallFaces'], [2])
        self.assertEqual(wall_grade_paths(tri, [2], [1])['unresolvedWallFaces'], [2])

    def test_no_grade_contact_or_invalid_face(self):
        tri = [[[0, 0, 0], [1, 0, 0], [0, 1, 0]]]
        self.assertEqual(wall_grade_paths(tri, [0], [])['unresolvedWallFaces'], [0])
        with self.assertRaises(AssertionError):
            wall_grade_paths(tri, [0], [4])


if __name__ == '__main__':
    unittest.main()
