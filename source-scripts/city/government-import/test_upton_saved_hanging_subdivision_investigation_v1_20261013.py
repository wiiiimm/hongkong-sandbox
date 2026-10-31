"""UNEXECUTED adversarial local attribution fixtures; no geometry generation."""
import unittest
from fractions import Fraction as F
import numpy as np
from upton_saved_hanging_subdivision_investigation_draft_v1_20261013 import subdivision_relation,oriented_sides
def packed(p):return tuple(F(float(x))for x in np.asarray(p,dtype=np.float32))
class HangingAttribution(unittest.TestCase):
 def setUp(self):
  self.a=(F(0),F(0),F(0));self.b=(F(1),F(0),F(1,3));self.p=(F(1,3),F(0),F(1,9))
 def test_real_float32_hanging_point_not_on_long_edge(self):
  q=subdivision_relation(self.p,self.a,self.b,packed(self.p),packed(self.a),packed(self.b),False)
  self.assertEqual(q['exactFinite3DParameter'],F(1,3));self.assertFalse(q['packedNodeOnLongPackedProjectedEdge']);self.assertTrue(q['eligibleComputed3DHangingSubdivisionNomination'])
 def test_whole_literal_facet_never_nominated_for_edit(self):
  q=subdivision_relation(self.p,self.a,self.b,packed(self.p),packed(self.a),packed(self.b),True)
  self.assertFalse(q['eligibleComputed3DHangingSubdivisionNomination'])
 def test_computed_long_edge_with_protected_node_incident_is_constrained(self):
  q=subdivision_relation(self.p,self.a,self.b,packed(self.p),packed(self.a),packed(self.b),False,protected_node_incident=True)
  self.assertEqual(q['exactFinite3DParameter'],F(1,3));self.assertFalse(q['projectedOnlyDifferentHeightLayer']);self.assertTrue(q['protectedWholeCurrentNodeIncident']);self.assertTrue(q['protectedIncidentFamilyConstrainedUnresolved']);self.assertFalse(q['eligibleComputed3DHangingSubdivisionNomination'])
 def test_projected_coincidence_at_other_height_not_subdivision(self):
  p=(self.p[0],F(1),self.p[2]);q=subdivision_relation(p,self.a,self.b,packed(p),packed(self.a),packed(self.b),False)
  self.assertTrue(q['projectedOnlyDifferentHeightLayer']);self.assertIsNone(q['exactFinite3DParameter']);self.assertFalse(q['protectedWholeCurrentNodeIncident']);self.assertFalse(q['eligibleComputed3DHangingSubdivisionNomination'])
 def test_shared_endpoints_are_not_hanging_nodes(self):
  for p in [self.a,self.b]:self.assertIsNone(subdivision_relation(p,self.a,self.b,packed(p),packed(self.a),packed(self.b),False))
 def test_detached_collinear_extension_is_not_finite_subdivision(self):
  p=(F(2),F(0),F(2,3));self.assertIsNone(subdivision_relation(p,self.a,self.b,packed(p),packed(self.a),packed(self.b),False))
 def test_already_conforming_dyadic_subdivision_not_repair(self):
  a=(F(0),F(0),F(0));b=(F(1),F(0),F(1));p=(F(1,2),F(0),F(1,2));q=subdivision_relation(p,a,b,packed(p),packed(a),packed(b),False)
  self.assertTrue(q['packedNodeOnLongPackedProjectedEdge']);self.assertFalse(q['eligibleComputed3DHangingSubdivisionNomination'])
 def test_ideal_boundary_point_rejected_after_float32_packing(self):
  t=[self.a,self.b,(F(0),F(0),F(1))];point=(F(1,2),F(1,6));_,s=oriented_sides(point,t);_,ps=oriented_sides(point,list(map(packed,t)))
  self.assertTrue(all(v>=0 for v in s));self.assertLess(ps[0],0)
  _,reverse=oriented_sides(point,[t[0],t[2],t[1]]);self.assertTrue(all(v>=0 for v in reverse))
 def test_collapsed_projection_does_not_gain_surface_credit(self):
  area,_=oriented_sides((F(0),F(0)),[(F(0),F(0),F(0)),(F(0),F(1),F(0)),(F(0),F(2),F(0))]);self.assertEqual(area,0)
if __name__=='__main__':unittest.main()
