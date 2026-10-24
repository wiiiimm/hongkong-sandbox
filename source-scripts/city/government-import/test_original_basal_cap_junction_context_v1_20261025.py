"""Prevent basal-context classification from accepting other surface roles."""
import math
import unittest

from original_basal_cap_junction_context_v1_20261025 import classify


class BasalContextTests(unittest.TestCase):
    def basal(self, face, minimum=0.0):
        return all(classify(face, minimum).values())

    def test_downward_at_complete_minimum(self):
        self.assertTrue(self.basal([[0., 0., 0.], [1., 0., 0.], [0., 0., 1.]]))

    def test_upward_surface_is_not_basal(self):
        self.assertFalse(self.basal([[0., 0., 0.], [0., 0., 1.], [1., 0., 0.]]))

    def test_horizontal_internal_surface_is_not_basal(self):
        self.assertFalse(self.basal([[0., 1., 0.], [1., 1., 0.], [0., 1., 1.]]))

    def test_one_representable_height_step_is_not_flat(self):
        y = math.nextafter(1.0, math.inf)
        self.assertFalse(self.basal([[0., 1., 0.], [1., 1., 0.], [0., y, 1.]], 1.0))

    def test_degenerate_face_has_no_downward_role(self):
        self.assertFalse(self.basal([[0., 0., 0.], [1., 0., 0.], [2., 0., 0.]]))

    def test_vertical_wall_is_not_basal(self):
        self.assertFalse(self.basal([[0., 0., 0.], [1., 0., 0.], [0., 1., 0.]]))


if __name__ == '__main__':
    unittest.main()
