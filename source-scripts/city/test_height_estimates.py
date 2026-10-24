"""Protect the low-rise estimates' source precedence and narrow local scope."""
import unittest
from shapely.geometry import box
from build_city import xy
from height_estimates import make_height_estimator

class HeightEstimateTests(unittest.TestCase):
 def setUp(self):
  self.x,self.z=xy(113.86,22.254)
  self.small=box(self.x-5,self.z-5,self.x+5,self.z+5)
  self.estimate,self.meta=make_height_estimator({'way/1':{'tags':{'highway':'pedestrian','name:en':'Tai O Market Street'},'geometry':[{'lon':113.859,'lat':22.254},{'lon':113.861,'lat':22.254}]}})
 def test_mapped_height_and_levels_always_win(self):
  self.assertEqual(self.estimate({'height':'18','building:levels':'3'},self.small,'house',0),(18,None))
  self.assertEqual(self.estimate({'building:levels':'4'},self.small,'house',0),(12.8,None))
 def test_explicit_house_types_get_low_rise_estimates(self):
  self.assertEqual(self.estimate({},self.small,'house',0),(8,'house-type'))
  self.assertEqual(self.estimate({},self.small,'bungalow',0),(4,'bungalow-type'))
  self.assertEqual(self.estimate({},self.small,'office',0),(24,None))
 def test_local_rule_only_matches_small_nearby_untyped_forms(self):
  self.assertEqual(self.estimate({},self.small,'yes',0),(8,'tai-o-small-village'))
  self.assertEqual(self.estimate({},box(self.x-9,self.z-9,self.x+9,self.z+9),'yes',0),(24,None))
  self.assertEqual(self.estimate({},box(self.x-5,self.z+195,self.x+5,self.z+205),'yes',0),(24,None))
 def test_non_residential_and_raised_parts_are_preserved(self):
  for tags in [{'shop':'convenience'},{'amenity':'school'},{'tourism':'hotel'},{'office':'yes'},{'power':'substation'},{'building:part':'yes'}]:
   self.assertEqual(self.estimate(tags,self.small,'yes',0),(24,None),tags)
  self.assertEqual(self.estimate({},self.small,'house',10),(24,None))
if __name__=='__main__':unittest.main()
