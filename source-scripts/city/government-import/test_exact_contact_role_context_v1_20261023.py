import unittest
from exact_original_shell_intersections_20261009 import rational_face, intersection_points
from exact_original_primitive_contacts_v1 import contact_measure
from exact_contact_role_context_v1_20261023 import contact_role


class ContactRoleTests(unittest.TestCase):
    def role(self, a, b):
        a, b = rational_face(a), rational_face(b)
        points = intersection_points(a, b)
        return contact_role(a, b, points, contact_measure(points)['dimension'], [2, 2])

    def test_proper_transverse_crossing(self):
        self.assertEqual(self.role([(0, 0, 0), (4, 0, 0), (0, 4, 0)], [(1, 1, -1), (1, 1, 1), (2, 1, 0)]), 'transverse-surface-crossing')

    def test_shared_boundary_not_crossing(self):
        self.assertEqual(self.role([(0, 0, 0), (4, 0, 0), (0, 4, 0)], [(0, 0, 0), (4, 0, 0), (2, 0, 2)]), 'source-edge-surface-contact')

    def test_coplanar_area_stays_separate(self):
        a = [(0, 0, 0), (4, 0, 0), (0, 4, 0)]
        self.assertEqual(self.role(a, a), 'shared-plane-area-contact')


if __name__ == '__main__':
    unittest.main()
