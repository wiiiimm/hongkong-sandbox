"""Unexecuted adverse fixtures for complete arithmetic enclosure, not point fit."""
import unittest,math
from fractions import Fraction as F
import numpy as np
from upton_complete_mask_float32_enclosure_v1_20261013 import domain_errors,axis_error,envelope,packed_primitive_coverage,native_whole_selection,orient
D=[-2477.5,-37.5,-2267.5,102.5]
def face(a,b,c):return [[a[0],0,a[1]],[b[0],0,b[1]],[c[0],0,c[1]]]
T=face((0,0),(1,0),(0,1))
class Tests(unittest.TestCase):
 def test_actual_domain_bound_not_fitted(self):
  e=domain_errors(D);self.assertEqual(e['x']['completeCastError'],F(1,2**13)+F(1,2**42));self.assertEqual(e['z']['completeCastError'],F(1,2**18)+F(1,2**47))
 def test_negative_midpoint_rounding_enclosed(self):
  e=axis_error(4096)['completeCastError'];q=-F(8193,2);cast=F(float(np.float32(float(q))));self.assertLessEqual(abs(cast-q),e)
 def test_binary64_bin_transition_included(self):
  q=F(2)-F(1,2**55);e=axis_error(q);self.assertGreaterEqual(e['float32HalfSpacing'],F(1,2**23))
 def test_subnormal_domain_enclosed(self):self.assertGreaterEqual(axis_error(F(1,2**160))['completeCastError'],F(1,2**150))
 def test_signed_zero_does_not_shift_coverage(self):
  e=domain_errors([-1,-1,1,1]);self.assertEqual(envelope([[-0.,+0.]]*3,e,[-1,-1,1,1]),envelope([[+0.,-0.]]*3,e,[-1,-1,1,1]))
 def test_overflow_range_rejected(self):
  with self.assertRaises(AssertionError):axis_error(2**128)
 def test_nonfinite_rejected(self):
  with self.assertRaises(AssertionError):axis_error(float('nan'))
 def test_outside_domain_not_clamped(self):
  with self.assertRaises(AssertionError):envelope([[2,0]]*3,domain_errors([-1,-1,1,1]),[-1,-1,1,1])
 def test_complete_triangle_all_directions(self):
  e=domain_errors(D);raw=[[-2340.,33.],[-2339.,33.],[-2340.,34.]];q=envelope(raw,e,D)
  for p in raw:self.assertTrue(all(orient(a,b,tuple(map(F,p)))>=0 for a,b in zip(q['exactEnvelopePolygon'],q['exactEnvelopePolygon'][1:]+q['exactEnvelopePolygon'][:1])))
 def test_projected_line_kept_as_complete_envelope(self):
  q=envelope([[0,0],[1,0],[0,0]],domain_errors([-2,-2,2,2]),[-2,-2,2,2]);self.assertTrue(q['collapsedOriginalPrimitiveUncredited']);self.assertGreater(len(q['exactEnvelopeTriangles']),0)
 def test_projected_point_kept_uncredited(self):self.assertTrue(envelope([[0,0]]*3,domain_errors([-1,-1,1,1]),[-1,-1,1,1])['collapsedOriginalPrimitiveUncredited'])
 def test_actual_packed_envelope_covers_complete_triangle(self):
  raw=[[-2340.,33.],[-2339.,33.],[-2340.,34.]];q=envelope(raw,domain_errors(D),D);g=np.asarray([face(*t)for t in q['exactEnvelopeTriangles']],dtype=np.float32).astype(float);self.assertTrue(packed_primitive_coverage(raw,g)['completeProtectedPrimitiveCovered'])
 def test_partial_edge_does_not_prove_whole(self):self.assertFalse(packed_primitive_coverage([[0,0],[1,0],[0,1]],np.asarray([face((0,0),(.25,0),(0,.25))]))['completeProtectedPrimitiveCovered'])
 def test_full_boundary_with_interior_hole_still_fails(self):
  quads=[[(0,0),(1,0),(.75,.25),(0,.25)],[(1,0),(0,1),(0,.75),(.75,0)],[(0,0),(.25,0),(.25,.75),(0,1)]];g=np.asarray([face(q[0],q[i],q[i+1])for q in quads for i in [1,2]]);r=packed_primitive_coverage([[0,0],[1,0],[0,1]],g);self.assertTrue(all(p['exactProjectionCovered']for p in r['allThreeCompleteBoundaryEdges']));self.assertFalse(r['completeProtectedPrimitiveCovered'])
 def test_renderer_excluded_thin_triangle_no_height_credit(self):
  q=packed_primitive_coverage([[0,0],[1,0],[0,2**-40]],np.asarray([face((0,0),(1,0),(0,2**-40))]));self.assertFalse(q['completeProtectedPrimitiveCovered']);self.assertEqual(q['productionDeterminantExcludedRetainedFaceIDs'],[0])
 def test_non_float32_retained_positions_rejected(self):
  with self.assertRaises(AssertionError):packed_primitive_coverage([[0,0],[1,0],[0,1]],np.asarray([face((0,0),(1,0),(0,1/3))]))
 def test_whole_base_not_native(self):
  s=dict(selected=[dict(currentFace=0),dict(currentFace=1)]);a=[dict(globalCurrentFace=i,uniqueSourceIdentity=True,assignedMultisetOccurrence=dict(sourcePath=p))for i,p in enumerate(['3d-viewer/city/data/terrain.json','parent'])];n,b=native_whole_selection(s,a,'parent');self.assertEqual([q['currentFace']for q in n],[1]);self.assertEqual([q['currentFace']for q in b],[0])
 def test_ambiguous_source_cannot_grant_native_preservation(self):
  with self.assertRaises(AssertionError):native_whole_selection(dict(selected=[dict(currentFace=0)]),[dict(globalCurrentFace=0,uniqueSourceIdentity=False)],'parent')
if __name__=='__main__':unittest.main()
