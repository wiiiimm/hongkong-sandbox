"""Real clip failure plus counterexamples for both unchanged repair limits."""
import json
from fractions import Fraction as F
from pathlib import Path
import unittest
from unittest.mock import patch
import numpy as np
import shapely
from exact_affine_halfplane_clip_v1_20261024 import convex_positive as old_clip
from exact_affine_halfplane_clip_v2_20261102 import (
    convex_positive, lower_region, bounded_line, REPAIRS,
    AREA_LIMIT, DISTANCE_SQUARED_LIMIT)


class Clip(unittest.TestCase):
    def setUp(self):
        REPAIRS.clear()

    def fixture(self):
        data = json.loads((Path(__file__).parent / 'tests/fixtures/academic-affine-clip-roundoff-20261102.json').read_text())
        return shapely.from_wkb(bytes.fromhex(data['regionWKB'])), data['difference']

    def test_real_saved_failure_has_a_fully_bounded_representable_line(self):
        region, coefficients = self.fixture()
        self.assertTrue(region.is_valid)
        with self.assertRaises(AssertionError):
            old_clip(region, coefficients)
        result = convex_positive(region, coefficients)
        self.assertEqual(result.geom_type, 'LineString')
        self.assertTrue(result.is_valid)
        self.assertEqual(result.area, 0)
        self.assertEqual(len(REPAIRS), 1)
        proof = REPAIRS[0]
        self.assertEqual(proof['operandWKB'], region.wkb_hex)
        self.assertEqual(proof['outputWKB'], result.wkb_hex)
        self.assertEqual(AREA_LIMIT, F(1e-12))
        self.assertEqual(DISTANCE_SQUARED_LIMIT, F(1e-12)**2)
        self.assertLessEqual(F(proof['exactSymmetricDifferenceAreaM2']), AREA_LIMIT)
        for key in ['exactForwardHausdorffSquaredM2', 'exactBackwardHausdorffSquaredM2']:
            self.assertLessEqual(F(proof[key]), DISTANCE_SQUARED_LIMIT)
        self.assertTrue(proof['continuousHausdorffDirectionsProvedByConvexity'])

    def test_normal_clips_keep_the_ordinary_result_exactly(self):
        region = shapely.box(10, 20, 14, 24)
        for coefficients in [(1,0,-12), (0,1,-22), (1,1,-34), (-1,0,11)]:
            self.assertEqual(convex_positive(region, coefficients).wkb,
                             old_clip(region, coefficients).wkb)
        self.assertEqual(REPAIRS, [])

    def test_larger_positive_area_cannot_be_collapsed(self):
        with self.assertRaises(AssertionError):
            bounded_line([(F(0),F(0)), (F(3),F(0)), (F(3),F(1,10**12))])

    def test_small_area_does_not_excuse_unrepresentable_distance(self):
        origin = F(10**16)
        with self.assertRaises(AssertionError):
            bounded_line([(origin,F(0)), (origin+F(1,10**6),F(0)),
                          (origin+F(1,10**6),F(1,10**18))])

    def test_nonconvex_target_cannot_use_convex_hausdorff_proof(self):
        with self.assertRaises(AssertionError):
            bounded_line([(F(0),F(0)), (F(1,10**6),F(0)),
                          (F(1,10**6),F(1,10**7)),
                          (F(1,2*10**6),F(1,2*10**7)), (F(0),F(1,10**7))])

    def test_complete_region_interface_preserves_the_real_fix(self):
        region, coefficients = self.fixture()
        result = lower_region(region, coefficients)
        self.assertEqual(result.geom_type, 'LineString')
        self.assertEqual(len(REPAIRS), 1)

    def test_normal_floor_return_is_identical_and_dispatch_restored(self):
        import bounded_original_upward_floor_return_v3_20261102 as original
        import bounded_original_upward_floor_domains_v3_20261102 as domains
        from bounded_original_upward_floor_domains_v4_20261102 import inset
        from test_bounded_original_ramp_return_v1_20261025 import square
        terrain = square(10., lambda x,z: 6.)
        source = square(.1, lambda x,z: 4.5+1.5*x)
        previous = original.lower_region
        expected, _ = domains.inset(terrain,source)
        actual, proof = inset(terrain,source)
        np.testing.assert_array_equal(expected,actual)
        self.assertEqual(proof['boundedAffineClipRepairs'], [])
        self.assertIs(original.lower_region,previous)

    def test_floor_dispatch_restores_on_failure(self):
        import bounded_original_upward_floor_return_v3_20261102 as original
        import bounded_original_upward_floor_domains_v3_20261102 as domains
        from bounded_original_upward_floor_domains_v4_20261102 import inset
        previous = original.lower_region
        with patch.object(domains,'inset',side_effect=RuntimeError('test cleanup')):
            with self.assertRaises(RuntimeError):
                inset(None,None)
        self.assertIs(original.lower_region,previous)


if __name__ == '__main__':
    unittest.main()
