import unittest
import numpy as np
from inherited_parent_coverage_v1 import qualify


def rectangle(x1):
    return np.array([[[0.,2.,0.],[x1,2.,0.],[0.,2.,1.]],[[x1,2.,0.],[x1,2.,1.],[0.,2.,1.]]])


class CoverageTests(unittest.TestCase):
    def test_exact_coverage(self):
        result = qualify(rectangle(1.), [0.,0.,1.,1.])
        self.assertEqual(result['renderedFloat32DifferenceM2'], 0)

    def test_existing_sub_two_mm_policy_keeps_geometry(self):
        faces = rectangle(.999)
        original = faces.copy()
        result = qualify(faces, [0.,0.,1.,1.])
        self.assertIsNotNone(result['existingNumericalCoverageProof'])
        np.testing.assert_array_equal(faces, original)

    def test_material_hole_and_excess_rejected(self):
        for x1 in [.9, 1.1]:
            with self.assertRaises(AssertionError): qualify(rectangle(x1), [0.,0.,1.,1.])
