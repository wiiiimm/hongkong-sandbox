import unittest
from exact_ground_line_cover_v1_20261030 import prove

def strip(left,right,height):
    return [[[left,height,-1],[right,height,-1],[right,height,1]],[[left,height,-1],[right,height,1],[left,height,1]]]

class CoverTests(unittest.TestCase):
    def test_complete_strict_cover(self):
        self.assertTrue(prove([0,0],[1,0],1,strip(0,1,2))['strictlyBelowGroundEverywhere'])
    def test_tiny_internal_gap_is_not_filled(self):
        with self.assertRaises(AssertionError):prove([0,0],[1,0],1,strip(0,.5,2)+strip(.500000000001,1,2))
    def test_middle_dip_is_not_hidden_by_endpoints(self):
        with self.assertRaises(AssertionError):prove([0,0],[1,0],1,strip(0,.4,2)+strip(.4,.6,.9)+strip(.6,1,2))
    def test_touching_is_not_strict_clearance(self):
        with self.assertRaises(AssertionError):prove([0,0],[1,0],1,strip(0,1,1))
    def test_unrelated_high_ground_does_not_cover_missing_part(self):
        with self.assertRaises(AssertionError):prove([0,0],[1,0],1,strip(0,.5,2)+strip(2,3,100))
    def test_upper_field_handles_overlapping_lower_layer(self):
        self.assertGreater(prove([0,0],[1,0],1,strip(0,1,.5)+strip(0,1,2))['minimumMarginM'],0)

if __name__=='__main__':unittest.main()
