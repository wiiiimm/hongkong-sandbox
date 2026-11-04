import unittest
from fractions import Fraction
import numpy as np
from exact_float32_parent_level_partition_v2_20261031 import choose,partition
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
 def test_all_inland_faces_return_byte_identical_noop(self):
  original=REAL.copy();original[:,:,1]+=8
  before=original.copy();out,proof=choose(original)
  self.assertEqual(out.tobytes(),before.tobytes());self.assertEqual(original.tobytes(),before.tobytes())
  self.assertFalse(proof['parentTriangulationChanged']);self.assertEqual(proof['subdividedParentFaces'],0)
  self.assertEqual(proof['sourceFaceByOutputFace'],list(range(len(original))))
  self.assertEqual(proof['inputSHA256'],proof['outputSHA256'])
 def test_already_separated_low_and_high_faces_preserve_both_sides(self):
  low=REAL[0].copy();low[:,1]=0
  high=REAL[1].copy();high[:,1]=4
  original=np.array([low,high]);out,proof=choose(original)
  self.assertEqual(out.tobytes(),original.tobytes());self.assertEqual(proof['sourceFaceByOutputFace'],[0,1])
  self.assertFalse(proof['parentTriangulationChanged'])
 def test_vertical_parent_remains_rejected(self):
  vertical=np.array([[[0,0,0],[0,4,0],[0,4,1]]],float)
  with self.assertRaises(AssertionError):partition(vertical,Fraction(77,64))
if __name__=='__main__':unittest.main()
