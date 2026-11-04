import unittest
import numpy as np
from recover_degenerate_low_group_receipt_v1_20261027 import canonical_facet


class DegenerateNormals(unittest.TestCase):
    def test_zero_area_retained_with_undefined_normal(self):
        tri = np.array([[0.,0.,0.], [1.,0.,0.], [2.,0.,0.]])
        result = canonical_facet(dict(sourceFace=7, areaM2=0., signedNormalYRatio=float('nan')), 7, tri)
        self.assertEqual(result, dict(sourceFace=7, areaM2=0., signedNormalYRatio=None, degenerate=True))

    def test_nonzero_area_nan_is_not_repaired(self):
        tri = np.array([[0.,0.,0.], [0.,0.,1.], [1.,0.,0.]])
        with self.assertRaises(AssertionError):
            canonical_facet(dict(sourceFace=7, areaM2=.5, signedNormalYRatio=float('nan')), 7, tri)

    def test_finite_normal_and_face_identity_preserved(self):
        tri = np.array([[0.,0.,0.], [0.,0.,1.], [1.,0.,0.]])
        record = dict(sourceFace=7, areaM2=.5, signedNormalYRatio=1.)
        self.assertFalse(canonical_facet(record, 7, tri)['degenerate'])
        for changed in (dict(record, sourceFace=8), dict(record, areaM2=.6), dict(record, signedNormalYRatio=-1.)):
            with self.assertRaises(AssertionError):
                canonical_facet(changed, 7, tri)


if __name__ == '__main__':
    unittest.main()
