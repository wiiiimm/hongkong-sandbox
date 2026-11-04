import unittest
from exact_original_shell_intersections_20261009 import rational_face, intersection_points
from exact_original_primitive_contacts_v1 import primitive_intersections, exact_component_contacts_with_primitives


class PrimitiveContactTests(unittest.TestCase):
    def check(self, a, b, expected):
        a, b = rational_face(a), rational_face(b)
        expected = {tuple(p) for p in expected}
        self.assertEqual(primitive_intersections(a, b), expected)
        self.assertEqual(primitive_intersections(b, a), expected)

    def test_points_and_off_plane(self):
        tri = [(0, 0, 0), (4, 0, 0), (0, 4, 0)]
        self.check([(1, 1, 0)] * 3, tri, [(1, 1, 0)])
        self.check([(1, 1, 1)] * 3, tri, [])
        self.check([(4, 4, 0)] * 3, tri, [])

    def test_segment_triangle_pierce_and_coplanar_clip(self):
        tri = [(0, 0, 0), (4, 0, 0), (0, 4, 0)]
        self.check([(1, 1, -1), (1, 1, 1), (1, 1, 0)], tri, [(1, 1, 0)])
        self.check([(-1, 1, 0), (5, 1, 0), (2, 1, 0)], tri, [(0, 1, 0), (3, 1, 0)])
        self.check([(5, 5, -1), (5, 5, 1), (5, 5, 0)], tri, [])

    def test_segments_skew_overlap_and_touch(self):
        a = [(0, 0, 0), (4, 0, 0), (2, 0, 0)]
        self.check(a, [(1, -1, 1), (1, 1, 1), (1, 0, 1)], [])
        self.check(a, [(1, 0, 0), (6, 0, 0), (3, 0, 0)], [(1, 0, 0), (4, 0, 0)])
        self.check(a, [(4, 0, 0), (4, 2, 0), (4, 1, 0)], [(4, 0, 0)])

    def test_ordinary_triangles_preserve_previous_exact_result(self):
        a = rational_face([(0, 0, 0), (4, 0, 0), (0, 4, 0)])
        b = rational_face([(1, 1, -1), (1, 1, 1), (2, 1, 0)])
        self.assertEqual(primitive_intersections(a, b), intersection_points(a, b))

    def test_whole_original_face_accounting_and_no_surface_credit_for_zero(self):
        a = [[(1, 1, 0)] * 3, [(0, 0, 0), (4, 0, 0), (0, 4, 0)]]
        b = [[(0, 0, 0), (4, 0, 0), (0, 4, 0)]]
        r = exact_component_contacts_with_primitives(a, [0, 1], b, [0])
        self.assertTrue(r['allPairsExamined'])
        self.assertEqual(r['originalFacePrimitiveDimensionsA'], {0: 0, 1: 2})
        self.assertEqual([c['surfacePair'] for c in r['contacts']], [False, True])
        self.assertFalse(r['physicalSupportAccepted'])


if __name__ == '__main__':
    unittest.main()
