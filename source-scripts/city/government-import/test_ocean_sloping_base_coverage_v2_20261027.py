import unittest
from fractions import Fraction as F
from ocean_sloping_base_coverage_v2_20261027 import source_polygon,fraction_area

def proof(points):return {'allExactBasicFeasibleColumnVertices':[{'exactSourceBarycentricWeights':[str(1-x-y),str(x),str(y)],'exactGapM':str(z)}for x,y,z in points]}
class CoverageTest(unittest.TestCase):
 def test_clear(self):self.assertEqual(fraction_area(source_polygon(proof([(F(0),F(0),F(1)),(F(1),F(0),F(1)),(F(0),F(1),F(1))]),F(0))),0)
 def test_full(self):self.assertEqual(fraction_area(source_polygon(proof([(F(0),F(0),F(-1)),(F(1),F(0),F(-1)),(F(0),F(1),F(-1))]),F(0))),F(1,2))
 def test_affine_cut(self):self.assertEqual(fraction_area(source_polygon(proof([(F(0),F(0),F(-1)),(F(1),F(0),F(1)),(F(0),F(1),F(1))]),F(0))),F(1,8))
 def test_vertical_ground_multiple_gaps(self):
  points=[(F(x),F(y),F(z))for x,y in [(0,0),(1,0),(0,1)]for z in [-1,1]]
  self.assertEqual(fraction_area(source_polygon(proof(points),F(0))),F(1,2))
 def test_strict_boundary_no_area(self):self.assertEqual(fraction_area(source_polygon(proof([(F(0),F(0),F(0)),(F(1),F(0),F(0)),(F(0),F(1),F(0))]),F(0))),0)
 def test_threshold(self):self.assertEqual(fraction_area(source_polygon(proof([(F(0),F(0),F(-1)),(F(1),F(0),F(0)),(F(0),F(1),F(0))]),F(-1,2))),F(1,8))
if __name__=='__main__':unittest.main()
