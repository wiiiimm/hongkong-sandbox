"""UNEXECUTED actual-family and adverse fixtures; no geometry output."""
import unittest
from fractions import Fraction as F
from run import ROOT,read
from upton_source_family_exact_subdivision_v1_20261013 import subdivide_source_triangle
class Subdivision(unittest.TestCase):
 def setUp(self):self.t=((F(0),F(0),F(0)),(F(3),F(0),F(0)),(F(0),F(0),F(3)));self.p=(F(2),F(0),F(1))
 def test_actual_saved_source35676_family(self):
  o=read(ROOT/'docs/astra-city/government-import/government-xl-upton-saved-cut-node-ancestor-correspondence-v1-20261013/complete-saved-cut-node-ancestor-correspondence.json.gz');t=next(r['untouchedOriginalXYZ']for r in o['completeClosedProjectedSourceAncestorNominees']if r['originalSourceFace']==35676)
  q=subdivide_source_triangle(t,o['cutNodeIdealXYZ'],1);self.assertEqual(q['exactFiniteParameter'],F('20309037317127047431788857785/221743238679014703148342181888'));self.assertTrue(q['completeIdealTrianglePreserved'])
 def test_reverse_winding_preserves_oriented_whole_triangle(self):
  q=subdivide_source_triangle(tuple(reversed(self.t)),self.p,0);self.assertLess(q['exactOriginalProjectedArea2'],0);self.assertEqual(sum(q['exactPieceProjectedAreas2']),q['exactOriginalProjectedArea2'])
 def test_endpoint_is_not_a_strict_subdivision(self):
  with self.assertRaises(AssertionError):subdivide_source_triangle(self.t,self.t[1],1)
 def test_collinear_extension_is_not_finite(self):
  with self.assertRaises(AssertionError):subdivide_source_triangle(self.t,(F(4),F(0),F(-1)),1)
 def test_projected_only_other_height_rejected(self):
  with self.assertRaises(AssertionError):subdivide_source_triangle(self.t,(F(2),F(1),F(1)),1)
 def test_face_interior_is_not_an_edge_split(self):
  with self.assertRaises(AssertionError):subdivide_source_triangle(self.t,(F(1),F(0),F(1)),1)
 def test_protected_literal_target_rejected(self):
  with self.assertRaises(AssertionError):subdivide_source_triangle(self.t,self.p,1,protected_target=True)
 def test_protected_node_incident_rejected(self):
  with self.assertRaises(AssertionError):subdivide_source_triangle(self.t,self.p,1,protected_node_incident=True)
 def test_zero_area_source_descriptor_retained_without_credit(self):
  with self.assertRaises(AssertionError):subdivide_source_triangle((self.t[0],self.t[0],self.t[0]),self.t[0],0)
if __name__=='__main__':unittest.main()
