import unittest
import shapely
from exact_affine_halfplane_clip_v1_20261024 import lower_region

class ExactAffineClipTests(unittest.TestCase):
    def test_large_translated_polygon_is_partitioned(self):
        p=shapely.box(-19000,-13400,-18800,-13200)
        positive=lower_region(p,[1,1,32200])
        negative=lower_region(p,[-1,-1,-32200])
        self.assertEqual(positive.area,20000)
        self.assertEqual(negative.area,20000)
        self.assertEqual(positive.intersection(negative).area,0)
        self.assertEqual(positive.union(negative).symmetric_difference(p).area,0)
    def test_positive_constant_retains_all(self):
        p=shapely.box(0,0,2,2)
        self.assertTrue(lower_region(p,[0,0,1]).equals(p))
    def test_nonpositive_constant_provides_no_area(self):
        p=shapely.box(0,0,2,2)
        self.assertTrue(lower_region(p,[0,0,0]).is_empty)
        self.assertTrue(lower_region(p,[0,0,-1]).is_empty)
    def test_holes_are_not_silently_filled(self):
        p=shapely.Polygon([(0,0),(3,0),(3,3),(0,3)],holes=[[(1,1),(2,1),(2,2),(1,2)]])
        with self.assertRaises(AssertionError):lower_region(p,[1,0,-1.5])
    def test_disconnected_regions_are_both_retained(self):
        p=shapely.MultiPolygon([shapely.box(0,0,1,1),shapely.box(2,0,3,1)])
        self.assertEqual(lower_region(p,[0,0,1]).area,2)
    def test_input_is_unchanged(self):
        p=shapely.box(-19000,-13400,-18800,-13200);old=p.wkb
        lower_region(p,[1,1,32200])
        self.assertEqual(p.wkb,old)

if __name__=='__main__':unittest.main()
