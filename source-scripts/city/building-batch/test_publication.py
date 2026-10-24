import unittest
from publication import disposition
class Screening(unittest.TestCase):
 def setUp(self):
  self.m={'worldBounds':[[0,2,0],[5,12,5]]};self.r={'outcome':'runtime-accepted-placement-unreviewed','concerns':[]};self.b={'source_base':2,'source_top':12,'height':10}
 def test_ground_and_source_guards(self):
  self.assertEqual(disposition(self.m,self.r,self.b),[])
  self.b['source_base']=20;self.assertIn('survey-height-disagreement',disposition(self.m,self.r,self.b))
  self.b['source_base']=None;self.assertIn('missing-survey-height-pair',disposition(self.m,self.r,self.b))
 def test_runtime_or_terrain_exception_never_passes(self):
  self.r['outcome']='validation-exception';self.assertIn('validation-exception',disposition(self.m,self.r,self.b))
  self.r['outcome']='runtime-accepted-placement-unreviewed';self.r['concerns']=['sampled-ground-gap-below-model-bottom'];self.assertEqual(disposition(self.m,self.r,self.b),self.r['concerns'])
if __name__=='__main__':unittest.main()
