"""Complete actual baseline UID fixture and narrow exact two-delta negatives."""
import unittest
from run import ROOT,read
from actual_native_post_block17_census_20261011 import exact_post_block17_census
class PostBlock17CensusTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.old=[r['uid'] for r in read(ROOT/'docs/astra-city/government-import/government-xl-complete-current-native-actual-position-matrix-bounds-v2-20261011/inventory.json.gz')['rows']]
 def actual(self):return self.old+['landsd/255438:0','landsd/256116:0']
 def test_actual_complete_baseline_plus_named_two_deltas(self):self.assertTrue(exact_post_block17_census(self.old,self.actual()))
 def test_missing_block17(self):
  with self.assertRaises(AssertionError):exact_post_block17_census(self.old,self.actual()[:-1])
 def test_missing_block6(self):
  with self.assertRaises(AssertionError):exact_post_block17_census(self.old,self.old+['landsd/256116:0'])
 def test_duplicate_delta_same_count(self):
  with self.assertRaises(AssertionError):exact_post_block17_census(self.old,self.old+['landsd/255438:0']*2)
 def test_unrelated_extra_delta(self):
  with self.assertRaises(AssertionError):exact_post_block17_census(self.old,self.old+['landsd/255438:0','landsd/1:0'])
 def test_baseline_actor_disappears_same_count(self):
  with self.assertRaises(AssertionError):exact_post_block17_census(self.old,self.actual()[1:]+['landsd/1:0'])
 def test_extra_current_actor(self):
  with self.assertRaises(AssertionError):exact_post_block17_census(self.old,self.actual()+['landsd/1:0'])
 def test_duplicate_original_baseline(self):
  with self.assertRaises(AssertionError):exact_post_block17_census(self.old[:-1]+[self.old[0]],self.actual())
if __name__=='__main__':unittest.main()
