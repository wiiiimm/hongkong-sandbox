"""Adversarial checks for exact preservation of existing coastal terrain."""
import unittest
import numpy as np
import shapely
from retained_native_template_v3_20261023 import verify_existing_low_faces, exact_rendered_face_multiset


class RetainedLowFaces(unittest.TestCase):
    def setUp(self):
        self.face = np.array([[[100., .7, 200.], [101., .8, 200.], [100., .9, 201.]]])
        self.record = [dict(kind='unchanged', parentFace=0)]

    def test_exact_low_face_outside_edits_is_preserved(self):
        proof = verify_existing_low_faces(self.face, self.face.copy(), self.record, shapely.box(300, 300, 301, 301))
        self.assertEqual(proof['newlyAuthoredLowFaces'], 0)

    def test_real_xz_contact_is_forbidden(self):
        with self.assertRaises(AssertionError):
            verify_existing_low_faces(self.face, self.face, self.record, shapely.box(100, 200, 101, 201))

    def test_changed_low_face_is_forbidden(self):
        altered = self.face.copy()
        altered[0, 0, 1] += .001
        with self.assertRaises(AssertionError):
            verify_existing_low_faces(self.face, altered, self.record, shapely.box(300, 300, 301, 301))

    def test_split_low_face_is_forbidden(self):
        with self.assertRaises(AssertionError):
            verify_existing_low_faces(self.face, self.face, [dict(kind='parent-fragment', parentFace=0)], shapely.box(300, 300, 301, 301))

    def test_removed_low_face_is_forbidden(self):
        with self.assertRaises(AssertionError):
            verify_existing_low_faces(self.face, np.empty((0, 3, 3)), [], shapely.box(300, 300, 301, 301))

    def test_production_float32_winding_preserves_complete_face(self):
        captured = self.face.astype('float32').astype('float64')[:, ::-1]
        self.assertTrue(exact_rendered_face_multiset(self.face, captured))

    def test_one_float32_step_surface_change_rejected(self):
        captured = self.face.astype('float32')
        captured[0, 0, 0] = np.nextafter(captured[0, 0, 0], np.float32(np.inf))
        self.assertFalse(exact_rendered_face_multiset(self.face, captured.astype('float64')))

    def test_duplicate_multiplicity_preserved(self):
        second = self.face + np.array([0, 0, 5])
        original = np.concatenate([self.face, second])
        captured = np.concatenate([self.face, self.face]).astype('float32').astype('float64')
        self.assertFalse(exact_rendered_face_multiset(original, captured))


if __name__ == '__main__':
    unittest.main()
