import unittest
from exact_ground_polygon_cover_v1_20261030 import prove

def strip(left,right,height):
    return [[[left,height,-1],[right,height,-1],[right,height,1]],[[left,height,-1],[right,height,1],[left,height,1]]]

class CoverTests(unittest.TestCase):
    triangle=[[0,0],[1,0],[0,1]]
    def test_complete_cover(self):self.assertTrue(prove(self.triangle,1,strip(0,1,2))['completeProjectedTriangleCovered'])
    def test_tiny_gap_rejected(self):
        with self.assertRaises(AssertionError):prove(self.triangle,1,strip(0,.5,2)+strip(.500000000001,1,2))
    def test_middle_low_ground_rejected(self):
        with self.assertRaises(AssertionError):prove(self.triangle,1,strip(0,.4,2)+strip(.4,.6,.9)+strip(.6,1,2))
    def test_touching_rejected(self):
        with self.assertRaises(AssertionError):prove(self.triangle,1,strip(0,1,1))
    def test_lower_layer_does_not_hide_upper(self):self.assertTrue(prove(self.triangle,1,strip(0,1,.5)+strip(0,1,2))['completeProjectedTriangleCovered'])
    def test_degenerate_source_rejected(self):
        with self.assertRaises(AssertionError):prove([[0,0],[1,0],[2,0]],1,strip(0,2,2))

if __name__=='__main__':unittest.main()
