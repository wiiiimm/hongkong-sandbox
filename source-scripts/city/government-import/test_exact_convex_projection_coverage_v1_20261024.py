import unittest
from exact_convex_projection_coverage_v1_20261024 import rational,intersection,uncovered,area2


class Coverage(unittest.TestCase):
    def setUp(self):
        self.square=rational([[0,0],[2,0],[2,2],[0,2]])
        self.cover=[rational([[0,0],[2,0],[2,2]]),rational([[0,0],[2,2],[0,2]])]
    def test_full_two_triangle_cover(self):self.assertFalse(uncovered(self.square,self.cover))
    def test_missing_half_retained(self):self.assertEqual(sum(abs(area2(p))for p in uncovered(self.square,self.cover[:1])),4)
    def test_reversed_winding_same(self):self.assertFalse(uncovered(self.square,[t[::-1]for t in self.cover]))
    def test_detached_triangle_no_credit(self):self.assertEqual(sum(abs(area2(p))for p in uncovered(self.square,[rational([[5,5],[6,5],[5,6]])])),8)
    def test_boundary_only_not_area(self):self.assertEqual(area2(intersection(self.square,rational([[2,0],[3,0],[2,2]]))),0)
    def test_tiny_real_gap_not_rounded_away(self):
        tri=rational([[0,0],[2,0],[2,2-2**-40]]);self.assertTrue(uncovered(self.square,[tri,self.cover[1]]))

if __name__=='__main__':unittest.main()
