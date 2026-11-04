"""Unexecuted distinct whole-facet/boundary/provenance adverse fixtures."""
import unittest
from fractions import Fraction as F
from upton_whole_current_facet_protection_v1_20261012 import closed_mask_meets,nominate,exact_overlap_attribution
from upton_two_original_six_mask_partition_v1_20261012 import mask
M=mask([[0,0],[1,0],[0,1]])
def t(x=0,y=0):return [[x,y,0],[x+1,y,0],[x,y,1]]
class Tests(unittest.TestCase):
 def test_whole_extended_facet_not_clipped(self):
  face=[[-1,2,0],[2,2,0],[0,2,2]];r=nominate([face],[M],[-3,-3,3,3]);self.assertEqual(r['selected'][0]['currentFace'],0);self.assertEqual(len(r['expandedMasks']),2);self.assertEqual(face,[[-1,2,0],[2,2,0],[0,2,2]])
 def test_exact_point_boundary_is_selected(self):self.assertTrue(closed_mask_meets([[1,3,0],[2,3,0],[1,3,-1]],M))
 def test_exact_line_boundary_is_selected(self):self.assertTrue(closed_mask_meets([[0,3,0],[1,3,0],[0,3,-1]],M))
 def test_strict_outside_not_nominated(self):self.assertFalse(closed_mask_meets(t(2),M))
 def test_vertical_incident_retained_without_projection_credit(self):
  r=nominate([[[0,0,0],[0,2,0],[1,2,0]]],[M],[-2,-2,2,2]);self.assertTrue(r['selected'][0]['projectedCollapsedUncredited']);self.assertEqual(len(r['expandedMasks']),1)
 def test_zero_incident_retained(self):self.assertEqual(len(nominate([[[0,0,0]]*3],[M],[-2,-2,2,2])['selected']),1)
 def test_whole_outside_domain_is_hold(self):self.assertEqual(nominate([[[-3,1,0],[1,1,0],[0,1,1]]],[M],[-2,-2,2,2])['wholeFacetOutsideCapturedDomainHolds'],[0])
 def test_no_recursive_touching_flood(self):
  r=nominate([t(),t(1)],[mask([[F(1,4),F(1,4)],[F(1,2),F(1,4)],[F(1,4),F(1,2)]])],[-2,-2,3,3]);self.assertEqual([s['currentFace']for s in r['selected']],[0])
 def test_duplicate_layers_preserved(self):self.assertEqual(len(nominate([t(),t(y=5)],[M],[-2,-2,2,2])['selected']),2)
 def test_exact_affine_height_range_not_sample(self):
  r=exact_overlap_attribution(t(),[[0,2,0],[1,4,0],[0,6,1]]);self.assertEqual(r['exactSignedLeftMinusRightRangeM'],['-6','-2'])
 def test_line_not_positive_area(self):self.assertEqual(exact_overlap_attribution(t(),[[0,2,0],[1,2,0],[0,2,-1]])['exactProjectedDimension'],'line')
 def test_collapsed_has_no_affine_credit(self):self.assertTrue(exact_overlap_attribution([[0,0,0]]*3,t())['collapsedProjectedFacetUncredited'])
if __name__=='__main__':unittest.main()
