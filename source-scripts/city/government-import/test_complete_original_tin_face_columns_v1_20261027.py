import unittest
import numpy as np
from complete_original_tin_face_columns_v1_20261027 import finite_face_context

class FiniteFaceColumns(unittest.TestCase):
    face = np.array([[0.,0.,0.], [2.,0.,0.], [0.,0.,2.]])
    def test_complete_cover_below_strict_existing_threshold(self):
        ground = self.face.copy(); ground[:,1] = 1
        r = finite_face_context(self.face, ground[None,:,:])
        self.assertTrue(r['belowEveryOverlappingGroundFaceByMoreThanHalfMetre'])
        self.assertEqual(r['exactMaximumAllFinitePairGapM'], '-1')

    def test_missing_projection_does_not_get_whole_below_credit(self):
        ground = self.face.copy(); ground[:,0] += 10; ground[:,1] = 1
        self.assertFalse(finite_face_context(self.face, ground[None,:,:])['belowEveryOverlappingGroundFaceByMoreThanHalfMetre'])

    def test_boundary_half_metre_is_not_more_than_half(self):
        ground = self.face.copy(); ground[:,1] = .5
        self.assertFalse(finite_face_context(self.face, ground[None,:,:])['belowEveryOverlappingGroundFaceByMoreThanHalfMetre'])

    def test_other_layer_prevents_exposure_inference(self):
        upper = self.face.copy(); upper[:,1] = 1
        lower = self.face.copy(); lower[:,1] = -1
        r = finite_face_context(self.face, np.array([upper, lower]))
        self.assertEqual(r['exactMaximumAllFinitePairGapM'], '1')
        self.assertFalse(r['exposedSurfaceProved'])
        self.assertFalse(r['belowEveryOverlappingGroundFaceByMoreThanHalfMetre'])

if __name__ == '__main__':
    unittest.main()
