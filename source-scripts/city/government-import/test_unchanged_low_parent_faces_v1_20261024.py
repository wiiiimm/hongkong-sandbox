import unittest
import numpy as np
import shapely
from unchanged_low_parent_faces_v1_20261024 import bind, verify

class UnchangedLowParentFacesTests(unittest.TestCase):
    def setUp(self):
        self.low=np.array([[[0.,-4.,0.],[1.,-4.,0.],[0.,-4.,1.]]])
        self.edit=shapely.box(10,10,20,20)
    def test_unchanged_low_faces_and_new_land_pass(self):
        b=bind(self.low,self.edit)
        land=self.low+np.array([10.,10.,10.])
        self.assertTrue(verify(np.concatenate([self.low,land]),b)['exactFloat32FaceMultiplicityPreserved'])
    def test_low_face_touching_edit_is_rejected(self):
        with self.assertRaisesRegex(AssertionError,'touches'):
            bind(self.low,shapely.box(1,0,2,1))
    def test_changed_low_height_is_rejected(self):
        b=bind(self.low,self.edit);changed=self.low.copy();changed[0,0,1]-=.01
        with self.assertRaisesRegex(AssertionError,'changed'):
            verify(changed,b)
    def test_removed_low_face_is_rejected(self):
        with self.assertRaisesRegex(AssertionError,'removed'):
            verify(self.low+np.array([10.,10.,10.]),bind(self.low,self.edit))
    def test_duplicate_low_face_is_rejected(self):
        with self.assertRaisesRegex(AssertionError,'duplicated'):
            verify(np.concatenate([self.low,self.low]),bind(self.low,self.edit))
    def test_new_low_face_is_rejected(self):
        with self.assertRaisesRegex(AssertionError,'introduced'):
            verify(np.concatenate([self.low,self.low+np.array([3.,0.,0.])]),bind(self.low,self.edit))

if __name__=='__main__':unittest.main()
