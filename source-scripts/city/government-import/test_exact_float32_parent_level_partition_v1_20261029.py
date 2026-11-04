import unittest
from fractions import Fraction
import numpy as np
from exact_float32_parent_level_partition_v1_20261029 import choose,partition
REAL=np.array([[[-11857.5,6,-2207.5],[-11857.5,-4,-2137.5],[-11787.5,5,-2207.5]],[[-11787.5,5,-2207.5],[-11857.5,-4,-2137.5],[-11787.5,3,-2137.5]],[[-11787.5,5,-2207.5],[-11787.5,3,-2137.5],[-11717.5,6,-2207.5]],[[-11717.5,6,-2207.5],[-11787.5,3,-2137.5],[-11717.5,3,-2137.5]]],float)
class PartitionTests(unittest.TestCase):
 def test_real_mixed_coast_partition_is_exact_and_input_unchanged(self):
  before=REAL.copy();out,p=choose(REAL);np.testing.assert_array_equal(REAL,before)
  self.assertEqual(p['exactLevel'],'77/64');self.assertTrue(p['parentSurfaceExactlyUnchanged']);self.assertTrue(p['exactOriginalPlaneAndWinding']);self.assertTrue(p['exactProjectedAreaConservation']);self.assertEqual(p['subdividedParentFaces'],2);self.assertEqual(len(out),8)
 def test_unrepresentable_intersections_reject_instead_of_rounding(self):
  with self.assertRaisesRegex(AssertionError,'nonrepresentable'):partition(REAL,Fraction(6,5))
 def test_unrepresented_input_and_nonfinite_input_reject(self):
  changed=REAL.copy();changed[0,0,0]+=.00001
  with self.assertRaisesRegex(AssertionError,'represented Float32'):choose(changed)
  changed=REAL.copy();changed[0,0,1]=np.nan
  with self.assertRaises(AssertionError):partition(changed,Fraction(77,64))
 def test_level_outside_unchanged_floor_interval_rejects(self):
  for level in [1,3]:
   with self.assertRaises(AssertionError):partition(REAL,Fraction(level))
if __name__=='__main__':unittest.main()
