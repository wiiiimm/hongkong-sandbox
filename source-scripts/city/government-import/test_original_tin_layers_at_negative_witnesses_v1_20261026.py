import unittest
from fractions import Fraction as F
from original_tin_layers_at_negative_witnesses_v1_20261026 import interval_at
class LayerTests(unittest.TestCase):
    def test_sloping_surface(self):self.assertEqual(interval_at([[0,0,0],[2,2,0],[0,0,2]],(F(1,2),F(1,2))),(F(1,2),F(1,2)))
    def test_outside_exact_boundary(self):self.assertIsNone(interval_at([[0,0,0],[2,2,0],[0,0,2]],(F(-1,10**20),F(0))))
    def test_vertical_surface_interval(self):self.assertEqual(interval_at([[0,0,0],[2,0,0],[0,4,0]],(F(1),F(0))),(F(0),F(2)))
    def test_vertical_not_at_point(self):self.assertIsNone(interval_at([[0,0,0],[2,0,0],[0,4,0]],(F(1),F(1,10**20))))
if __name__=='__main__':unittest.main()
