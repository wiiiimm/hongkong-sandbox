"""Unexecuted adversarial fixtures for retained lineage/MAX and 3D joins."""
import unittest
from fractions import Fraction as F
import numpy as np
from upton_inherited_overlap_boundary_v1_20261012 import overlap_pair,complete_max_difference,projection,segment_to_facets,source_attribution,intersection,area
def face(y=0):return np.array([[0,y,0],[2,y,0],[0,y,2]],float)
class Tests(unittest.TestCase):
 def test_unchanged_complete_area(self):
  a=face();q=overlap_pair(a,a,a,a);self.assertTrue(q['projectionInherited']and q['heightInherited']);self.assertEqual(q['exactCandidatePairAreaM2'],'2')
 def test_packed_region_outside_original(self):
  a=face();b=a.copy();b[1,0]+=1/1024;self.assertFalse(overlap_pair(b,b,a,a)['projectionInherited'])
 def test_real_offset_not_copied_approval(self):
  a=face();q=overlap_pair(face(1/1024),a,a,a);self.assertFalse(q['heightInherited']);self.assertEqual(q['exactPerLineageHeightDifferenceRangesM'][0],['1/1024']*2)
 def test_point_not_positive_area(self):
  a=face();b=a+np.array([2,0,0]);self.assertEqual(overlap_pair(a,b,a,b)['exactCandidateProjectionDimension'],'point')
 def test_line_not_positive_area(self):
  a=face();b=np.array([[0,0,0],[2,0,0],[0,0,-2]],float);self.assertEqual(overlap_pair(a,b,a,b)['exactCandidateProjectionDimension'],'line')
 def test_full_affine_range_not_single_witness(self):
  a=face();b=a.copy();b[1,1]=1;self.assertEqual(overlap_pair(b,a,a,a)['exactPerLineageHeightDifferenceRangesM'][0],['0','1'])
 def test_max_crossing_full_region(self):
  a=face();a[1,1]=2;b=face(1);poly=projection(face());q=complete_max_difference(poly,[a,b],[b,a]);self.assertTrue(q['exactIdealAffineMaxUnchanged']);self.assertGreater(len(q['allExactWinnerRegions']),1)
 def test_third_higher_plane_not_hidden_by_pair(self):
  q=complete_max_difference(projection(face()),[face(),face(3)],[face()]);self.assertEqual(q['exactMaximumAbsoluteIdealAffineMaxDifferenceM'],'3');self.assertFalse(q['exactIdealAffineMaxUnchanged'])
 def test_missing_current_footprint(self):
  q=complete_max_difference(projection(face()),[face()],[face()+[4,0,0]]);self.assertFalse(q['completeIdealAffineMaxRegionCovered'])
 def test_rational_clip_no_second_rounding(self):
  p=[(F(0),F(0)),(F(1,3),F(0)),(F(0),F(1,3))];self.assertEqual(area(intersection(p,p)),F(1,18))
 def test_duplicate_source_identities_preserved(self):
  f=face();s=[dict(sourcePath='a',lineage=[],allSelectedMeshFaceIDs=[7,8],completeSelectedDrawnTriplets=[f.reshape(9).tolist()]*2)];q=source_attribution([f,f],s);self.assertFalse(q[0]['uniqueSourceIdentity']);self.assertEqual([r['assignedMultisetOccurrence']['sourceMeshFace']for r in q],[7,8])
 def test_multiset_missing_rejected(self):
  with self.assertRaises(AssertionError):source_attribution([face()],[])
 def test_source_extra_rejected(self):
  s=[dict(sourcePath='a',lineage=[],allSelectedMeshFaceIDs=[7],completeSelectedDrawnTriplets=[face().reshape(9).tolist()])]
  with self.assertRaises(AssertionError):source_attribution([],s)
 def test_vertical_ruled_face_full_segment(self):
  f=np.array([[0,0,0],[2,0,0],[0,3,0]],float);q=segment_to_facets([[0,0,0],[0,3,0]],[f],F(0));self.assertTrue(q['completeFinite3DCorrespondence'])
 def test_partial_endpoint_contact_rejected(self):
  q=segment_to_facets([[0,0,0],[3,0,0]],[face()],F(0));self.assertFalse(q['completeFinite3DCorrespondence'])
 def test_disconnected_middle_gap_rejected(self):
  a=face();a[:,0]*=.4;b=a+[1.2,0,0];q=segment_to_facets([[0,0,0],[2,0,0]],[a,b],F(0));self.assertFalse(q['completeFinite3DCorrespondence'])
 def test_whole_union_two_facets(self):
  a=face();b=np.array([[2,0,0],[4,0,0],[2,0,2]],float);self.assertTrue(segment_to_facets([[0,0,0],[4,0,0]],[a,b],F(0))['completeFinite3DCorrespondence'])
 def test_fixed_01_3d_not_height_only(self):
  self.assertTrue(segment_to_facets([[0,.005,0],[1,.005,0]],[face()],F(.01))['completeFinite3DCorrespondence']);self.assertFalse(segment_to_facets([[0,.02,0],[1,.02,0]],[face()],F(.01))['completeFinite3DCorrespondence'])
 def test_zero_facet_uncredited(self):
  q=segment_to_facets([[0,0,0],[1,0,0]],np.zeros((1,3,3)),F(.1));self.assertFalse(q['completeFinite3DCorrespondence']);self.assertEqual(q['allExactDegenerateFacetsUncredited'],[0])
 def test_collapsed_segment_rejected(self):
  with self.assertRaises(AssertionError):segment_to_facets([[0,0,0],[0,0,0]],[face()],F(.01))
 def test_nonfinite_rejected(self):
  with self.assertRaises(AssertionError):segment_to_facets([[0,0,0],[np.inf,0,0]],[face()],F(.01))
if __name__=='__main__':unittest.main()
