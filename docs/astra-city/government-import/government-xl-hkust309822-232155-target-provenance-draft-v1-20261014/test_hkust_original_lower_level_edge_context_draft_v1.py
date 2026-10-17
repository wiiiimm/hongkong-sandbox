"""Focused novel interval-account fixtures; reused finite kernel tests remain separate."""
import unittest
from fractions import Fraction as Q
from hkust_original_lower_level_edge_context_draft_v1 import closed_interval_account
class AccountTests(unittest.TestCase):
 def test_touching_complete(self):self.assertTrue(closed_interval_account([(Q(0),Q(1,2)),(Q(1,2),Q(1))],[])['entireEdgeExactPositiveDimensionalContact'])
 def test_exact_tiny_gap(self):self.assertFalse(closed_interval_account([(Q(0),Q(1,2)),(Q(1,2)+Q(1,2**60),Q(1))],[])['entireEdgeExactPositiveDimensionalContact'])
 def test_points_no_bridge(self):self.assertFalse(closed_interval_account([],[Q(0),Q(1)])['entireEdgeExactPositiveDimensionalContact'])
 def test_duplicate_interval(self):self.assertEqual(closed_interval_account([(Q(0),Q(1)),(Q(0),Q(1))],[])['positiveClosedIntervals'],[['0','1']])
 def test_empty_scope_negative(self):self.assertFalse(closed_interval_account([],[])['entireEdgeExactPositiveDimensionalContact'])
 def test_invalid_outside(self):
  with self.assertRaises(AssertionError):closed_interval_account([(Q(-1),Q(1))],[])
 def test_zero_interval_rejected(self):
  with self.assertRaises(AssertionError):closed_interval_account([(Q(1,2),Q(1,2))],[])
 def test_no_support_credit_even_complete(self):self.assertFalse(closed_interval_account([(Q(0),Q(1))],[])['structuralSupportAccepted'])
if __name__=='__main__':unittest.main()
