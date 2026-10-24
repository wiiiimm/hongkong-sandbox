import unittest
import numpy as np
from original_face_ground_crossing_20261009 import face_ground_context


def flat(height=0):
    return np.array([[[-10,height,-10],[10,height,-10],[10,height,10]],
                     [[-10,height,-10],[10,height,10],[-10,height,10]]],float)


class FaceGroundTests(unittest.TestCase):
    def test_vertical_crossing(self):
        face=[[-1,-1,0],[1,-1,0],[0,3,0]]
        r=face_ground_context(face,flat())
        self.assertTrue(r['verticalFace']);self.assertTrue(r['groundProjectionCovered'])
        self.assertEqual(r['minimum']['minimumGapM'],-1)
        self.assertEqual(r['maximumObservedGapM'],3)

    def test_vertical_lower_envelope_vertex_breakpoint(self):
        face=[[-2,2,0],[0,-3,0],[2,2,0]]
        self.assertEqual(face_ground_context(face,flat())['minimum']['minimumGapM'],-3)

    def test_vertical_ground_ridge_interior(self):
        face=[[-2,0,0],[2,0,0],[0,4,0]]
        ground=np.array([[[-3,0,-2],[0,2,-2],[0,2,2]],
                         [[-3,0,-2],[0,2,2],[-3,0,2]],
                         [[0,2,-2],[3,0,-2],[3,0,2]],
                         [[0,2,-2],[3,0,2],[0,2,2]]],float)
        r=face_ground_context(face,ground)
        self.assertEqual(r['minimum']['minimumGapM'],-2)

    def test_slanted_triangle(self):
        face=[[-1,-1,-1],[1,1,-1],[0,2,1]]
        r=face_ground_context(face,flat())
        self.assertFalse(r['verticalFace']);self.assertEqual(r['minimum']['minimumGapM'],-1)

    def test_highest_overlapping_ground(self):
        face=[[-1,-1,0],[1,-1,0],[0,3,0]]
        r=face_ground_context(face,np.concatenate([flat(-2),flat(2)]))
        self.assertEqual(r['minimum']['minimumGapM'],-3)
        self.assertEqual(r['maximumObservedGapM'],1)
        self.assertFalse(r['continuousMaximumCertified'])

    def test_incomplete_projection_is_not_credit(self):
        ground=np.array([[[0,0,-2],[3,0,-2],[0,0,2]]],float)
        r=face_ground_context([[-1,-1,0],[1,-1,0],[0,3,0]],ground)
        self.assertFalse(r['groundProjectionCovered']);self.assertFalse(r['installationApproved'])

    def test_malformed_and_degenerate(self):
        for face in [[[0,0,0]]*3,[[0,0,0],[1,float('nan'),0],[0,0,1]]]:
            with self.assertRaises(AssertionError):face_ground_context(face,flat())


if __name__=='__main__':unittest.main()
