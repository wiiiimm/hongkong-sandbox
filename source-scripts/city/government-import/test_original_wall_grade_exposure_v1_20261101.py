import unittest
import numpy as np
from original_wall_grade_exposure_v1_20261101 import vertex_exposure

class WallExposureTests(unittest.TestCase):
    def test_local_upper_bound_is_positive(self):
        g=np.array([[[0.,0,0],[1,0,0],[0,0,1]]])
        self.assertTrue(vertex_exposure([.25,2,.25],g)['exposed'])

    def test_sloping_bbox_requires_exact_query(self):
        g=np.array([[[0.,0,0],[1,10,0],[0,0,1]]])
        p=vertex_exposure([.1,2,.1],g)
        self.assertTrue(p['exposed'])
        self.assertIn('completeCandidateColumnProofs',p)

    def test_vertical_ground_cannot_be_omitted(self):
        g=np.array([[[0.,0,0],[1,0,0],[0,0,1]],[[.25,0,.25],[.25,3,.25],[.25,0,.5]]])
        self.assertFalse(vertex_exposure([.25,2,.25],g)['exposed'])

    def test_no_ground_has_no_exposure_credit(self):
        g=np.array([[[0.,0,0],[1,0,0],[0,0,1]]])
        self.assertFalse(vertex_exposure([5,2,5],g)['exposed'])

if __name__=='__main__':unittest.main()
