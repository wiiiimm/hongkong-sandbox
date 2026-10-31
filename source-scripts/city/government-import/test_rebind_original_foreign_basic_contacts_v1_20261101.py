import unittest
import numpy as np
from rebind_original_foreign_basic_contacts_v1_20261101 import identical_array

class CompleteArrayBindingTests(unittest.TestCase):
    def test_exact_full_array_matches(self):
        x=[[1.,2.,3.],[4.,5.,6.]]
        self.assertEqual(identical_array(x,x,'<f8'),identical_array(x,x,'<f8'))

    def test_signed_zero_is_not_silently_normalised(self):
        with self.assertRaises(AssertionError):identical_array([0.],[-0.],'<f8')

    def test_one_ulp_source_change_is_rejected(self):
        with self.assertRaises(AssertionError):identical_array([1.],[np.nextafter(1.,2.)],'<f8')

    def test_triangle_winding_change_is_rejected(self):
        with self.assertRaises(AssertionError):identical_array([0,1,2],[0,2,1],'<i8')

if __name__=='__main__':unittest.main()
