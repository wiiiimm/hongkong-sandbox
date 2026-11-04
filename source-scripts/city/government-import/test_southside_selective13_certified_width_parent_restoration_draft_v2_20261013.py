"""UNEXECUTED focused boundary/adverse fixtures; no model acceptance."""
import unittest,copy,struct,json
from fractions import Fraction as F
import southside_selective13_certified_width_parent_restoration_draft_v2_20261013 as h
class TestCertifiedRestoration(unittest.TestCase):
 def branch(self,core=None,width=F(1,10)):
  core=core or [(F(0),F(0)),(F(1),F(0)),(F(1),F(1)),(F(0),F(1))]
  outer=h._hull([(x+dx,z+dz)for x,z in core for dx in [-width,width]for dz in [-width,width]])
  return dict(coreHull=core,closedOuterHull=outer,closedOuterBounds=[min(p[0]for p in outer),min(p[1]for p in outer),max(p[0]for p in outer),max(p[1]for p in outer)],alphaTerms=h.alpha_terms(core,width))
 def alpha(self,x,z,b=None):return h.affine_value(min((b or self.branch())['alphaTerms'],key=lambda t:h.affine_value(t,(F(x),F(0),F(z)))),(F(x),F(0),F(z)))
 def plane(self,y=0):return [(F(0),F(y),F(0)),(F(2),F(y),F(0)),(F(0),F(y),F(2))]
 def test_core_alpha_one(self):self.assertEqual(self.alpha(F(1,2),F(1,2)),1)
 def test_exact_outer_alpha_zero(self):self.assertEqual(self.alpha(-F(1,10),F(1,2)),0)
 def test_exact_half_width_alpha(self):self.assertEqual(self.alpha(-F(1,20),F(1,2)),F(1,2))
 def test_nonpositive_width_rejected(self):
  with self.assertRaises(AssertionError):h.alpha_terms([(F(0),F(0))],0)
 def test_point_core_outer_closed(self):
  b=self.branch([(F(0),F(0))]);self.assertEqual(len(b['closedOuterHull']),4);self.assertEqual(self.alpha(0,0,b),1)
 def test_segment_core_outer_closed(self):
  b=self.branch([(F(0),F(0)),(F(1),F(0))]);self.assertEqual(self.alpha(F(1,2),F(0),b),1)
 def test_exact_parent_core_height(self):self.assertEqual(h.proposed_point((F(1,4),F(8),F(1,4)),'actual-parent-core-once',(F(0),F(0),F(1)),self.plane(2))[1],2)
 def test_transition_height_is_explicit_new(self):self.assertEqual(h.proposed_point((F(1,4),F(8),F(1,4)),'changed-certified-width-parent-transition',(F(0),F(0),F(1,2)),self.plane(2))[1],5)
 def test_alpha_outside_rejected(self):
  with self.assertRaises(AssertionError):h.proposed_point((F(0),F(8),F(0)),'actual-parent-core-once',(F(0),F(0),F(2)),self.plane())
 def test_unchanged_exterior_literal_coordinates(self):
  p=(F(1,3),F(7),F(1,5));self.assertEqual(h.proposed_point(p,'unchanged-v4-exterior',(F(0),F(0),F(0)),None),p)
 def test_closed_area_covered(self):self.assertTrue(h.rational_closed_coverage([(0,0),(1,0),(0,1)],[self.plane()])['covered'])
 def test_area_hole_not_vertices_only(self):self.assertFalse(h.rational_closed_coverage([(0,0),(2,0),(2,2),(0,2)],[self.plane()])['covered'])
 def test_closed_segment_touch_retained(self):self.assertTrue(h.rational_closed_coverage([(0,0),(2,0)],[self.plane()])['covered'])
 def test_closed_segment_gap_rejected(self):self.assertFalse(h.rational_closed_coverage([(0,0),(3,0)],[self.plane()])['covered'])
 def test_singular_point_touch(self):self.assertTrue(h.rational_closed_coverage([(0,0)],[self.plane()])['covered'])
 def test_singular_point_far(self):self.assertFalse(h.rational_closed_coverage([(3,3)],[self.plane()])['covered'])
 def test_no_global_exterior_retessellation(self):
  a={'kind':'unchanged-v4-exterior','prePolygon':self.plane()};b={'kind':'changed-certified-width-parent-transition','prePolygon':[(F(1),F(0),F(0)),(F(2),F(0),F(0)),(F(1),F(0),F(1))]};r=h.conform_boundaries([a,b]);self.assertEqual(r[0]['prePolygon'],a['prePolygon'])
 def test_changed_boundary_gets_exact_knots(self):
  a={'kind':'actual-parent-core-once','prePolygon':self.plane()};b={'kind':'unchanged-v4-exterior','prePolygon':[(F(1),F(0),F(0)),(F(2),F(0),F(0)),(F(1),F(0),F(1))]};self.assertIn((F(1),F(0),F(0)),h.conform_boundaries([a,b])[0]['prePolygon'])
 def test_all_layer_maximum_not_first(self):
  q=h.whole_edge_max_envelope((0,0,0),(1,0,0),[(0,self.plane(1)),(1,self.plane(3))]);self.assertTrue(q['allClosedEdgeCovered']);self.assertEqual(q['allOriginalClosedEndpointAndPlaneCrossoverKnots'][0]['completeHighestFacetTies'],[1])
 def test_complete_layer_ties_preserved(self):
  q=h.whole_edge_max_envelope((0,0,0),(1,0,0),[(0,self.plane(1)),(1,self.plane(1))]);self.assertEqual(q['allOriginalClosedEndpointAndPlaneCrossoverKnots'][0]['completeHighestFacetTies'],[0,1])
 def test_maximum_whole_edge_missing_interval(self):self.assertFalse(h.whole_edge_max_envelope((0,0,0),(3,0,0),[(0,self.plane())])['allClosedEdgeCovered'])
 def test_collapsed_facet_retained_filtered_context(self):
  t=[(0,0,0),(0,1,0),(0,2,0)];q=h.whole_edge_max_envelope((0,0,0),(1,0,0),[(7,t)]);self.assertEqual(q['actualProductionHeightFieldFilteredFacetIDs'],[7]);self.assertFalse(q['allClosedEdgeCovered']);self.assertTrue(q['meshFacetsNotRemoved'])
 def test_actual_float32_bytes_and_error(self):
  p=(F(1,3),F(2),F(1,7));v,e,b=h.packed_vertex(p);self.assertEqual(struct.unpack('<f',bytes.fromhex(b[0]))[0],v[0]);self.assertEqual(e[0],abs(F(v[0])-p[0]))
 def test_exterior_plane_change_rejected(self):
  p=self.plane()
  with self.assertRaises(AssertionError):h.source_plane_correspondence(p,[(x,y+1,z)for x,y,z in p],p,'unchanged-v4-exterior')
 def test_exact_rational_record_json_boundary(self):
  q=h.literal_json_ready(dict(points=[(F(1,7),F(-2,3),F(0))],alpha=F(1,11),strict=False));self.assertEqual(json.loads(json.dumps(q))['points'][0],['1/7','-2/3','0']);self.assertEqual(q['alpha'],'1/11');self.assertIs(q['strict'],False)
 def test_packed_float_bytes_preserved_by_json_boundary(self):
  p=h.packed_vertex((F(1,3),F(2),F(1,7)))[0];q=json.loads(json.dumps(h.literal_json_ready(dict(packed=p))));self.assertEqual([struct.pack('<f',v)for v in q['packed']],[struct.pack('<f',v)for v in p])
if __name__=='__main__':unittest.main()
