"""Exact fallback retains real burial while rejecting impossible plane extensions."""
import unittest
from unittest.mock import patch
import numpy as np
import original_face_ground_finite_witness_context_v1_20261025 as context


class FiniteWitnessTests(unittest.TestCase):
    ground = np.array([[[-1., 0., -1.], [2., 0., -1.], [-1., 0., 2.]]])

    def fallback(self, face):
        old = dict(minimum=dict(position=[0., -5000., 0.], minimumGapM=-5000.))
        with patch.object(context, 'previous', return_value=old):
            result = context.face_ground_context(np.array(face), self.ground)
        self.assertEqual(result['rawPriorImpossibleWitnessVerbatim'], old)
        self.assertFalse(result['installationApproved'])
        return result

    def test_nearly_vertical_wall_uses_finite_height(self):
        result = self.fallback([[0., 10., 0.], [1., 20., 0.], [0., 10., 1e-15]])
        self.assertEqual(result['minimum']['minimumGapM'], 10.)
        self.assertTrue(result['groundProjectionCovered'])

    def test_actual_burial_remains_negative(self):
        result = self.fallback([[0., -2., 0.], [1., -1., 0.], [0., -2., 1e-15]])
        self.assertEqual(result['minimum']['minimumGapM'], -2.)
        self.assertFalse(result['exactFiniteWitnessProof']['existingOrdinaryClearanceBoundProved'])

    def test_valid_prior_diagnostic_is_preserved(self):
        old = dict(minimum=dict(position=[0., 10., 0.], minimumGapM=10.))
        with patch.object(context, 'previous', return_value=old), patch.object(context, 'verify') as verify:
            result = context.face_ground_context(np.array([[0., 10., 0.], [1., 20., 0.], [0., 10., 1.]]), self.ground)
        self.assertIs(result, old)
        verify.assert_not_called()

    def test_nonfinite_point_cannot_be_a_source_witness(self):
        self.assertFalse(context.finite_source_bounds_contain([[0., 0., 0.], [1., 1., 0.], [0., 0., 1.]], [0., float('nan'), 0.]))


if __name__ == '__main__':
    unittest.main()
