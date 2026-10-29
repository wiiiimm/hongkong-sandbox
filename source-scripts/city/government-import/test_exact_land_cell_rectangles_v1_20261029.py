import unittest
import shapely
from exact_land_cell_rectangles_v1_20261029 import partition

class LandTests(unittest.TestCase):
    def setUp(self):
        self.bounds=[0,0,4,3];self.cells=[10,20,14,23]
        self.land=shapely.union_all([shapely.box(2,0,4,1),shapely.box(1,1,4,2),shapely.box(0,2,4,3)])
    def test_staircase_keeps_water(self):
        rects,polys=partition(self.land,self.bounds,self.cells,self.land.buffer(-.01))
        self.assertEqual(len(rects),3)
        self.assertTrue(shapely.union_all(polys).equals(self.land))
        self.assertEqual(shapely.union_all(polys).intersection(shapely.box(0,0,1,1)).area,0)
    def test_single_full_rectangle(self):
        rects,_=partition(shapely.box(0,0,4,3),self.bounds,self.cells,shapely.box(1,1,2,2))
        self.assertEqual(rects,[[10,20,14,23]])
    def test_partial_cell_rejected(self):
        with self.assertRaisesRegex(AssertionError,'Partial'):
            partition(self.land.union(shapely.box(0,0,.5,.5)),self.bounds,self.cells,shapely.Point(3,2))
    def test_required_water_rejected(self):
        with self.assertRaisesRegex(AssertionError,'Required'):
            partition(self.land,self.bounds,self.cells,shapely.box(.1,.1,.9,.9))
    def test_extra_parent_land_rejected(self):
        with self.assertRaises(AssertionError):partition(self.land.union(shapely.box(5,5,6,6)),self.bounds,self.cells,self.land)
    def test_hole_is_not_filled(self):
        land=shapely.box(0,0,4,3).difference(shapely.box(1,1,2,2))
        _,polys=partition(land,self.bounds,self.cells,shapely.Point(.5,.5))
        self.assertTrue(shapely.union_all(polys).equals(land))

if __name__=='__main__':unittest.main()
