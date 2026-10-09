import unittest,copy
from original_wall_rim_accounting_20261009 import original_samples,verify
class Tests(unittest.TestCase):
 def fixture(self):
  p=[0,0,0,2,0,0,0,3,0, 5,0,0,7,0,0,5,3,0];idx=[0,1,2,3,4,5]
  samples=original_samples(p,idx,0)
  for s in samples:s.update(ground=s['point'][1]+(1 if s['originalIncidentFaces']==[0] else 0),gap=-1 if s['originalIncidentFaces']==[0] else 0)
  low=[s for s in samples if s['point'][1]<=.35];m={'checks':len(samples),'lowRimChecks':len(low),'minSurfaceGap':-1,'minLowGap':-1,'maxLowGap':0}
  return p,idx,samples,m
 def check(self,p,idx,s,m):return verify(p,idx,0,s,wall_faces=[0],verified_wall_role=True,expected_metric=m)
 def test_positive_real_wall_and_anchor(self):p,i,s,m=self.fixture();self.assertTrue(self.check(p,i,s,m)['verified'])
 def test_ordinary_burial_reject(self):
  p,i,s,m=self.fixture();s[-1]['ground']=s[-1]['point'][1]+1;s[-1]['gap']=-1
  with self.assertRaises(AssertionError):self.check(p,i,s,m)
 def test_no_ordinary_anchor_reject(self):
  p,i,s,m=self.fixture()
  for r in s:
   if r['originalIncidentFaces']==[1]:r.update(ground=r['point'][1]-.2,gap=.2)
  m['maxLowGap']=.2
  with self.assertRaises(AssertionError):self.check(p,i,s,m)
 def test_omitted_sample_reject(self):
  p,i,s,m=self.fixture()
  with self.assertRaises(AssertionError):self.check(p,i,s[:-1],m)
 def test_wrong_original_face_reject(self):
  p,i,s,m=self.fixture();s[3]['originalIncidentFaces']=[0]
  with self.assertRaises(AssertionError):self.check(p,i,s,m)
 def test_wall_above_ground_floating_rim_reject(self):
  p,i,s,m=self.fixture();s[0].update(ground=-2,gap=2)
  with self.assertRaises(AssertionError):self.check(p,i,s,m)
 def test_missing_ground_reject(self):
  p,i,s,m=self.fixture();s[0]['ground']=float('nan')
  with self.assertRaises(AssertionError):self.check(p,i,s,m)
if __name__=='__main__':unittest.main()
