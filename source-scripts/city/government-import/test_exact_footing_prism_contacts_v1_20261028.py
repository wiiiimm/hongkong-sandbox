import unittest
import numpy as np
from exact_footing_prism_contacts_v1_20261028 import surface_contacts


class PrismContacts(unittest.TestCase):
    cap = np.array([[[0., 1., 0.], [2., 1., 0.], [0., 1., 2.]]])

    def contacts(self, tri, caps=None):
        return surface_contacts(np.array([tri]), self.cap if caps is None else caps, 0., 1.)['contacts']

    def test_wholly_contained_face(self):
        self.assertTrue(self.contacts([[.2, .5, .2], [.3, .5, .2], [.2, .5, .3]]))

    def test_crossing_with_every_vertex_outside(self):
        self.assertTrue(self.contacts([[-1., .5, .5], [3., .5, .5], [.5, .5, 3.]]))

    def test_above_and_below(self):
        for y in [-.001, 1.001]:
            self.assertFalse(self.contacts([[.2, y, .2], [.3, y, .2], [.2, y, .3]]))

    def test_outside_cap_inside_aabb(self):
        self.assertFalse(self.contacts([[1.6, .5, 1.6], [1.7, .5, 1.6], [1.6, .5, 1.7]]))

    def test_closed_boundary_and_degenerate_points(self):
        for p in [[0., 0., 0.], [1., 1., 1.], [2., .5, 0.]]:
            self.assertTrue(self.contacts([p, p, p]))

    def test_winding_independent(self):
        tri = [[.2, .5, .2], [.3, .5, .2], [.2, .5, .3]]
        self.assertEqual(bool(self.contacts(tri)), bool(self.contacts(tri, self.cap[:, ::-1])))

    def test_oblique_vertical_crossing(self):
        self.assertTrue(self.contacts([[.2, -1., .2], [.3, 2., .2], [.2, 2., .3]]))


if __name__ == '__main__':
    unittest.main()
