import unittest
import numpy as np
import shapely
from retained_rendered_union_template_v1_20261023 import verify_retained_faces


class ExactUnion(unittest.TestCase):
    def setUp(self):
        self.a=np.array([[[0.,2.,0.],[1.,2.,0.],[0.,2.,1.]]])
        self.b=self.a+np.array([1.,1.,1.])
        self.all=np.concatenate([self.a,self.b]).astype('float32').astype('float64')
        self.domain=shapely.box(0,0,3,3)
    def verify(self,captured):return verify_retained_faces(captured,[self.a,self.b],self.domain)
    def test_complete_union_preserved(self):self.assertTrue(self.verify(self.all)['retainedNativeFaceMultisetPreserved'])
    def test_winding_and_order_do_not_change_surface(self):self.verify(self.all[::-1,::-1])
    def test_unchanged_parent_fill_is_allowed(self):self.verify(np.concatenate([self.all,self.a+np.array([0.,0.,2.])]))
    def test_removed_face_rejected(self):
        with self.assertRaises(AssertionError):self.verify(self.all[:1])
    def test_one_float32_step_rejected(self):
        changed=self.all.copy();changed[0,0,1]=np.nextafter(np.float32(2),np.float32(np.inf))
        with self.assertRaises(AssertionError):self.verify(changed)
    def test_duplicate_substitution_rejected(self):
        with self.assertRaises(AssertionError):self.verify(np.concatenate([self.a,self.a]))
    def test_missing_duplicate_rejected(self):
        with self.assertRaises(AssertionError):verify_retained_faces(self.all,[self.a,self.a,self.b],self.domain)
    def test_nonproduction_capture_rejected(self):
        changed=self.all.copy();changed[0,0,0]=.000000000000000001
        with self.assertRaises(AssertionError):self.verify(changed)
    def test_outside_complete_domain_rejected(self):
        with self.assertRaises(AssertionError):verify_retained_faces(self.all,[self.a,self.b],shapely.box(0,0,1,1))


if __name__=='__main__':unittest.main()
