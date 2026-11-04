import unittest
import shapely
from exact_local_planar_partition_v1_20261030 import verify

class LocalPartition(unittest.TestCase):
    def test_valid_partition(self):
        a=shapely.Polygon([(10600,-5600),(10601,-5600),(10601,-5599)])
        b=shapely.Polygon([(10600,-5600),(10601,-5599),(10600,-5599)])
        result=verify([a,b],shapely.box(10600,-5600,10601,-5599))
        self.assertTrue(result['inputCoordinateRoundTripExact'])
        self.assertEqual(result['areaExcessM2'],0)
    def test_overlap_rejected(self):
        a=shapely.box(10600,-5600,10601,-5599)
        with self.assertRaisesRegex(AssertionError,'overlaps'):verify([a,a],a)
    def test_gap_rejected(self):
        a=shapely.box(10600,-5600,10601,-5599)
        with self.assertRaisesRegex(AssertionError,'cover'):verify([a],shapely.box(10600,-5600,10602,-5599))
    def test_tolerance_cannot_be_widened(self):
        a=shapely.box(0,0,1,1)
        with self.assertRaises(AssertionError):verify([a],a,1)
if __name__=='__main__':unittest.main()
