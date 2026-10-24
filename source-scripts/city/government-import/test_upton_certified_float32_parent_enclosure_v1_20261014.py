import unittest
from fractions import Fraction as F
from upton_certified_float32_parent_enclosure_v1_20261014 import bracket,round_nearest,enclose,edge_nodes,exact_f32,bits_value
class Float32Certificates(unittest.TestCase):
 def test_exact_adjacent_fraction_brackets(self):
  lo,hi,p=bracket(F(1,3));self.assertLess(lo,F(1,3));self.assertGreater(hi,F(1,3));self.assertEqual(p['adjacentOrderedKeys'][1]-p['adjacentOrderedKeys'][0],1)
 def test_exact_signed_and_subnormal_brackets(self):
  for q in [F(-1,3),F(1,2**200),-F(1,2**200),F(0),F(1,2**149)]:
   lo,hi,_=bracket(q);self.assertLessEqual(lo,q);self.assertGreaterEqual(hi,q);self.assertTrue(exact_f32(lo)and exact_f32(hi))
 def test_positive_ties_even(self):
  v,p=round_nearest(F(1)+F(1,2**24));self.assertEqual(v,1.);self.assertTrue(p['halfwayTie']);self.assertEqual(p['chosenBitsHex'],'3f800000')
  v,p=round_nearest(F(1)+F(3,2**24));self.assertEqual(F(v),F(1)+F(1,2**22));self.assertTrue(p['halfwayTie'])
 def test_negative_ties_even(self):
  v,p=round_nearest(-F(1)-F(1,2**24));self.assertEqual(v,-1.);self.assertEqual(p['chosenBitsHex'],'bf800000')
 def test_outside_finite_range_rejected(self):
  with self.assertRaises(AssertionError):bracket(F(2)**129)
class Enclosure(unittest.TestCase):
 def setUp(self):self.parent=[[-2345.,7.,1.],[-2344.,8.,1.],[-2345.,6.,2.]]
 def test_nondyadic_interior_full_closed_packed_certificate(self):
  mask=[[F(-2345)+F(1,3),F(6,5)],[F(-2345)+F(1,2),F(6,5)],[F(-2345)+F(1,3),F(7,5)]];r=enclose(mask,self.parent)
  self.assertTrue(r['actualHeightIndexedWholeClosedMaskCoverage']['wholeClosedResidualCovered']);self.assertTrue(r['allHullVerticesWithinOriginalParent'])
  self.assertTrue(all(p['allPackedXZByteIdentityCertified']and p['noOtherHeightLayerYUsed']for p in r['completeOwnPlanePackedNodeCertificates']))
  self.assertGreater(len(r['actualHeightIndexedWholeClosedMaskCoverage']['completeWholeGapBoundaryProofs']),0)
 def test_thin_round_to_nearest_collapse_is_enclosed_by_exact_cells(self):
  mask=[(F(-2344.5),F(5,4)),(F(-2344.5)+F(1,100000),F(5,4)),(F(-2344.5)+F(1,100000),F(13,10))]
  rounded=[round_nearest(p[0])[0]for p in mask];self.assertEqual(len(set(rounded)),1)
  r=enclose(mask,self.parent);self.assertTrue(r['actualHeightIndexedWholeClosedMaskCoverage']['wholeClosedResidualCovered']);self.assertTrue(all(p['productionHeightIndexIncludesFacet']for p in r['actualPackedFacetRecords']))
 def test_edge_cell_uses_exact_collinear_subdivision(self):
  u=F(1,3*4096);p=(F(-2344.5)+u,F(1.5)-u);q=(F(-2344.5)-u,F(1.5)+u);inside=(F(-2344.5),F(1.5)-F(1,100000))
  r=enclose([p,inside,q],self.parent);self.assertTrue(r['completeOriginalParentEdgeCertificates']);self.assertTrue(r['actualHeightIndexedWholeClosedMaskCoverage']['wholeClosedResidualCovered'])
  self.assertTrue(all(c['completeOwnEdgeRepresentabilityCertificate']['allOtherCoordinateRepresentabilityTestedExactly']for c in r['completeOriginalParentEdgeCertificates']))
 def test_only_authentic_whole_edge_when_no_internal_lattice_node(self):
  a=(F(-2345),F(1));b=(F(-2344.75),F(bits_value(0x3fa00001)))
  nodes,p=edge_nodes(a,b,10000,lambda:None);self.assertEqual([t for t,_ in nodes],[F(0),F(1)]);self.assertEqual(p['completeEnumeratedKeyCount'],1025)
 def test_outside_original_parent_never_extrapolated(self):
  with self.assertRaises(AssertionError):enclose([[-2343.,1.],[-2343.,1.1],[-2343.1,1.]],self.parent)
 def test_nonconvex_mask_never_bbox_substituted(self):
  with self.assertRaises(AssertionError):enclose([[-2344.9,1.1],[-2344.5,1.1],[-2344.8,1.2],[-2344.5,1.3],[-2344.9,1.3]],self.parent)
 def test_declared_enumeration_limit_is_unresolved_not_snap(self):
  with self.assertRaises(ValueError):edge_nodes((F(-2345),F(1)),(F(-2344),F(2)),100,lambda:None)
 def test_height_index_tiny_geometry_gets_no_coverage_credit(self):
  p=[[0.,0.,0.],[2**-100,0.,0.],[0.,0.,2**-100]]
  with self.assertRaises(AssertionError):enclose([[F(0),F(0)],[F(1,2**101),F(0)],[F(0),F(1,2**101)]],p)
if __name__=='__main__':unittest.main()
