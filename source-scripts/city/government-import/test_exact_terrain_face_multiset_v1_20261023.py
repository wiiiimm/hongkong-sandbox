import unittest
import numpy as np
from exact_terrain_face_multiset_v1_20261023 import same_faces


class ExactTerrainFaceMultisetTests(unittest.TestCase):
    def setUp(self):
        self.faces=np.array([[[0.,2.,0.],[1.,2.,0.],[0.,2.,1.]],[[1.,2.,0.],[1.,2.,1.],[0.,2.,1.]]])

    def test_order_only_is_accepted(self):
        self.assertTrue(same_faces(self.faces,self.faces[::-1]))

    def test_one_ulp_change_and_winding_are_rejected(self):
        changed=self.faces.copy();changed[0,0,1]=np.nextafter(changed[0,0,1],np.inf)
        self.assertFalse(same_faces(self.faces,changed))
        self.assertFalse(same_faces(self.faces,self.faces[:,::-1]))

    def test_missing_duplicate_is_rejected(self):
        self.assertFalse(same_faces(self.faces,np.repeat(self.faces[:1],2,axis=0)))

    def test_nonfinite_and_bad_shape_rejected(self):
        for value in [np.full((2,3,3),np.nan),np.zeros((2,3,2))]:
            with self.assertRaises(AssertionError):same_faces(self.faces,value)


if __name__=='__main__':unittest.main()
