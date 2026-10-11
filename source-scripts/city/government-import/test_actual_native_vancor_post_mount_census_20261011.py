import unittest
from actual_native_vancor_post_mount_census_20261011 import DELTA,exact_census
class Tests(unittest.TestCase):
 def setUp(self):self.old=['landsd/'+str(1000000+i)+':0'for i in range(6639)];self.current=self.old+DELTA
 def test_complete(self):self.assertTrue(exact_census(self.old,self.current))
 def test_order_independent(self):self.assertTrue(exact_census(self.old,list(reversed(self.current))))
 def test_missing_old(self):
  with self.assertRaises(AssertionError):exact_census(self.old,self.current[1:]+['landsd/99999999:0'])
 def test_wrong_delta(self):
  with self.assertRaises(AssertionError):exact_census(self.old,self.current[:-1]+['landsd/99999999:0'])
 def test_duplicate_old(self):
  with self.assertRaises(AssertionError):exact_census(self.old[:-1]+[self.old[0]],self.current)
 def test_duplicate_current(self):
  with self.assertRaises(AssertionError):exact_census(self.old,self.current[:-1]+[self.current[0]])
 def test_extra(self):
  with self.assertRaises(AssertionError):exact_census(self.old,self.current+['landsd/99999999:0'])
if __name__=='__main__':unittest.main()
