"""UNEXECUTED focused exact closed-region distance fixtures."""
import unittest
from fractions import Fraction as F
from southside_saved_negative_region_exact_core_distance_draft_v1_20261013 import closed_negative_region,convex_linf_distance,prepare_complete_core,distance_to_complete_core,authentic_positive_faces
class DistanceFixtures(unittest.TestCase):
 def test_point_point_next_double(self):self.assertEqual(convex_linf_distance([(0,0)],[(F(1)+F(1,2**52),0)])['exactDistanceM'],F(1)+F(1,2**52))
 def test_point_diagonal_segment_exact(self):self.assertEqual(convex_linf_distance([(0,5)],[(0,0),(1,1)])['exactDistanceM'],4)
 def test_interior_overlap_has_exact_zero_witness(self):
  p=convex_linf_distance([(0,0),(2,0),(0,2)],[(F(1,4),F(1,4))]);self.assertEqual(p['exactDistanceM'],0);self.assertEqual(p['exactNegativeProjectionWitness'],p['exactCoreProjectionWitness'])
 def test_closed_edge_touch(self):self.assertEqual(convex_linf_distance([(0,0),(1,0),(0,1)],[(1,0),(2,0)])['exactDistanceM'],0)
 def test_overlapping_bounds_are_not_zero_distance(self):self.assertEqual(convex_linf_distance([(0,0),(2,0),(0,2)],[(2,2),(3,2),(2,3)])['exactDistanceM'],1)
 def test_negative_halfplane_intersection_threshold_retained(self):
  r=closed_negative_region([(0,0,0),(2,0,0),(0,0,2)],[-1,0,0]);self.assertTrue(r['hasStrictNegativePoint']);self.assertEqual(set(r['completeClosedNegativeSourcePoints']),{(F(0),F(0),F(0)),(F(1),F(0),F(0)),(F(0),F(0),F(1))});self.assertIn(F(-1,2),r['exactGapM'])
 def test_vertical_projection_segment_preserved(self):
  r=closed_negative_region([(0,0,0),(0,2,0),(0,0,2)],[-1,1,-1]);self.assertTrue(r['hasStrictNegativePoint']);self.assertEqual(convex_linf_distance([(p[0],p[2])for p in r['completeClosedNegativeSourcePoints']],[(1,1)])['exactDistanceM'],1)
 def test_boundary_only_closure_not_genuine_negative(self):self.assertFalse(closed_negative_region([(0,0,0)],[F(-1,2)])['hasStrictNegativePoint'])
 def test_positive_region_not_included(self):self.assertEqual(closed_negative_region([(0,0,0),(1,0,0)],[0,1])['completeClosedNegativeSourcePoints'],[])
 def test_reversed_polygon_and_duplicate_vertices(self):self.assertEqual(convex_linf_distance([(0,2),(2,0),(0,0),(0,0)],[(3,0)])['exactDistanceM'],1)
 def test_strict_exclusions_and_equal_distance_ties(self):
  records=[dict(uid=str(i),domainID=str(i),completeXZPoints=[p])for i,p in enumerate([(-1,0),(1,0),(100,0)])];core=prepare_complete_core(records);r=distance_to_complete_core([(0,0)],core);self.assertEqual(r['exactMinimumDistanceM'],1);self.assertEqual(len(r['completeNearestCoreTies']),2);self.assertEqual(len(r['completeStrictDistanceExclusions']),1)
 def test_identical_mask_keeps_original_lineage(self):
  r=[dict(uid=str(i),domainID=str(i),completeXZPoints=[(0,0),(1,1)])for i in range(13)];core=prepare_complete_core(r);self.assertEqual(len(core),1);self.assertEqual(core[0]['completeOriginalCoreDomainLineage'],r)
 def test_authentic_complete_records_define_positive_and_unresolved_negative_scope(self):
  current=dict(completeOriginalFaceCount=2,completeWholeWorldSHA256='world',completeOriginalFaceComparisons=[dict(sourceFace=i,completeOriginalFacetSHA256=str(i))for i in range(2)])
  records=[dict(sourceFace=i,completeOriginalFacetSHA256=str(i),unfilteredAuthenticatedOriginalGroundComparison=dict(coarse=dict(existingOrdinaryClearanceBoundProved=i==0),paired=None if i==0 else dict(existingOrdinaryClearanceBoundProved=False),completeFiniteOrdinaryBoundProved=i==0))for i in range(2)]
  authentic=dict(completeWorldSHA256='world',completeOriginalFaceComparisons=records,allAuthenticatedGroundFailuresRetained=[1]);self.assertEqual(authentic_positive_faces(authentic,current),{0})
 def test_omitted_unresolved_authentic_failure_cannot_appear_positive(self):
  current=dict(completeOriginalFaceCount=1,completeWholeWorldSHA256='world',completeOriginalFaceComparisons=[dict(sourceFace=0,completeOriginalFacetSHA256='facet')]);authentic=dict(completeWorldSHA256='world',completeOriginalFaceComparisons=[dict(sourceFace=0,completeOriginalFacetSHA256='facet',unfilteredAuthenticatedOriginalGroundComparison=dict(coarse=dict(existingOrdinaryClearanceBoundProved=False),paired=dict(existingOrdinaryClearanceBoundProved=False),completeFiniteOrdinaryBoundProved=False))],allAuthenticatedGroundFailuresRetained=[])
  with self.assertRaises(AssertionError):authentic_positive_faces(authentic,current)
if __name__=='__main__':unittest.main()
