"""DRAFT adverse exact closed-core tests; numerical execution awaits ROOT."""
import unittest
from fractions import Fraction as F
from exact_finite_original_core_max_preservation_v1_20261011 import added_native_core_max,closed_piece_coverage,closed_segment_union

def tri(y=0,xz=((0,0),(2,0),(0,2))):return [(x,y,z)for x,z in xz]
class CoreMAX(unittest.TestCase):
 def test_equal_surface(self):self.assertTrue(added_native_core_max([tri()],[tri()])['wholeOriginalClosedCoreMAXPreserved'])
 def test_lower_surface(self):self.assertTrue(added_native_core_max([tri()],[tri(-1)])['wholeOriginalClosedCoreMAXPreserved'])
 def test_positive_area_raise(self):self.assertFalse(added_native_core_max([tri()],[tri(1)])['wholeOriginalClosedCoreMAXPreserved'])
 def test_point_raise(self):self.assertFalse(added_native_core_max([tri()],[tri(1,((2,0),(3,0),(2,-1)))])['wholeOriginalClosedCoreMAXPreserved'])
 def test_segment_raise(self):self.assertFalse(added_native_core_max([tri()],[tri(1,((0,0),(2,0),(0,-2)))])['wholeOriginalClosedCoreMAXPreserved'])
 def test_piecewise_max_not_single_witness(self):
  p=[(0,0,0),(2,2,0),(0,0,2)];q=[(0,2,0),(2,0,0),(0,2,2)]
  self.assertTrue(added_native_core_max([p,q],[tri(1)])['wholeOriginalClosedCoreMAXPreserved'])
 def test_v_envelope_endpoints_do_not_hide_middle_raise(self):
  p=[(0,0,0),(2,2,0),(0,0,2)];q=[(0,2,0),(2,0,0),(0,2,2)]
  self.assertFalse(added_native_core_max([p,q],[tri(F(3,2),((0,0),(2,0),(0,-1)))])['wholeOriginalClosedCoreMAXPreserved'])
 def test_boundary_points_do_not_cover_segment(self):self.assertFalse(closed_segment_union((F(0),F(0)),(F(2),F(0)),[[(F(0),F(0))],[(F(2),F(0))]])['closedCovered'])
 def test_full_boundary_does_not_cover_area(self):
  p=[(F(0),F(0)),(F(2),F(0)),(F(0),F(2))];r=[[a,b]for a,b in zip(p,p[1:]+p[:1])]
  self.assertFalse(closed_piece_coverage(p,r)['wholeFiniteCovered'])
 def test_vertical_drawn_not_indexed(self):
  r=added_native_core_max([tri()],[[(0,0,0),(0,1,0),(0,0,1)]])
  self.assertTrue(r['allCompleteAddedFaceCoreMAXProofs'][0]['drawnContactsStillUnqualified'])
 def test_absent_core_vacuous_not_coverage_credit(self):
  r=added_native_core_max([tri()],[tri(99,((3,3),(4,3),(3,4)))])
  self.assertEqual(r['allCompleteAddedFaceCoreMAXProofs'][0]['allFiniteOriginalCoreIntersectionProofs'],[]);self.assertTrue(r['notContactOrSeamOrActorApproval'])
 def test_nonfinite_rejected(self):
  with self.assertRaises(AssertionError):added_native_core_max([tri(float('nan'))],[tri()])
if __name__=='__main__':unittest.main()
