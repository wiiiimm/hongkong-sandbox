import unittest
from shapely.geometry import box
from protected_original_inset_return_v1_20261024 import constrain


class ProtectedReturn(unittest.TestCase):
    def setUp(self):self.core=box(0,0,2,2);self.outer=box(-3,-3,5,5)
    def test_current_footprint_is_excluded_but_core_preserved(self):
        p=box(3,-1,4,3);r=constrain(self.core,self.outer,[p]);self.assertTrue(r.covers(self.core));self.assertEqual(r.intersection(p).area,0);self.assertEqual(r.area,self.outer.area-p.area)
    def test_multiple_protected_footprints(self):
        ps=[box(3,-1,4,3),box(-2,0,-1,1)];r=constrain(self.core,self.outer,ps);self.assertTrue(all(r.intersection(p).area==0 for p in ps))
    def test_unrelated_outside_footprint_preserves_domain(self):self.assertTrue(constrain(self.core,self.outer,[box(9,9,10,10)]).equals(self.outer))
    def test_core_intersection_is_rejected(self):
        with self.assertRaises(AssertionError):constrain(self.core,self.outer,[box(1,1,3,3)])
    def test_core_boundary_contact_is_rejected(self):
        with self.assertRaises(AssertionError):constrain(self.core,self.outer,[box(2,0,3,1)])
    def test_empty_or_invalid_protected_domains_are_rejected(self):
        for footprints in [[],[box(0,0,0,0)]]:
            with self.subTest(footprints=footprints),self.assertRaises(AssertionError):constrain(self.core,self.outer,footprints)
    def test_core_on_parent_return_boundary_is_rejected(self):
        with self.assertRaises(AssertionError):constrain(self.core,box(0,0,5,5),[box(3,3,4,4)])

if __name__=='__main__':unittest.main()
