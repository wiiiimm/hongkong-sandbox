import unittest
from build_city import number,xy,geometry
class ImportTests(unittest.TestCase):
 def test_units(self):
  self.assertEqual(number('100'),100)
  self.assertEqual(number('100 ft'),30.48)
  self.assertAlmostEqual(number('7\'4"'),2.2352)
  self.assertIsNone(number('three'))
  self.assertIsNone(number('10;20'))
 def test_coordinate_control(self):
  x,z=xy(114.1595,22.2852)
  self.assertAlmostEqual(x,-22.5,delta=.2);self.assertAlmostEqual(z,243,delta=.2)
 def test_multipolygon_hole(self):
  def ring(points,role):return {'role':role,'geometry':[{'lon':x,'lat':y} for x,y in points]}
  p=geometry({'members':[ring([(114.15,22.28),(114.151,22.28),(114.151,22.281),(114.15,22.281),(114.15,22.28)],'outer'),ring([(114.1502,22.2802),(114.1508,22.2802),(114.1508,22.2808),(114.1502,22.2808),(114.1502,22.2802)],'inner')]})
  self.assertEqual(len(p.interiors),1)
if __name__=='__main__':unittest.main()
