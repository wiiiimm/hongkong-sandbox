"""UNEXECUTED focused exact boundary fixtures; no actual terrain construction."""
import unittest
from fractions import Fraction as F
import southside_domain_first_exact_core_union_construction_draft_v2_20261013 as m
class Boundary(unittest.TestCase):
 def branches(self,hulls,width=F(1,10)):
  out=[]
  for raw in hulls:
   h=m._hull([tuple(map(F,q))for q in raw]);outer=m._hull([(x+dx,z+dz)for x,z in h for dx in [-width,width]for dz in [-width,width]])
   terms=[(F(0),F(0),F(1))]+[(a/(width*(abs(a)+abs(b))),b/(width*(abs(a)+abs(b))),F(1)+c/(width*(abs(a)+abs(b))))for a,b,c in m._support_planes(h)]
   out.append(dict(coreHull=h,closedOuterHull=outer,closedOuterBounds=[min(p[0]for p in outer),min(p[1]for p in outer),max(p[0]for p in outer),max(p[1]for p in outer)],alphaTerms=terms))
  return out
 def rect(self,x0,z0,x1,z1):return [(x0,z0),(x1,z0),(x1,z1),(x0,z1)]
 def partition(self,poly,hulls):
  b=self.branches(hulls);u=m.exact_core_union_boundary(b);return m.domain_first_partition([tuple(map(F,p))for p in poly],b,1,u),u
 def test_internal_diagonal_mask_edge_excluded_before_terrain(self):
  b=self.branches([[(0,0),(2,0),(2,2)],[(0,0),(2,2),(0,2)]]);u=m.exact_core_union_boundary(b);self.assertEqual(len(u['completeTrueAreaUnionBoundary']),4);self.assertTrue(u['excludedInternalMaskEdgesNotTerrainFacets'])
 def test_no_internal_diagonal_split_wholly_core_triangle(self):
  rows,u=self.partition([(F(1,2),3,F(1,2)),(F(3,2),3,F(1,2)),(F(1,2),3,F(3,2))],[[(0,0),(2,0),(2,2)],[(0,0),(2,2),(0,2)]]);self.assertEqual(len(rows),1);self.assertEqual(rows[0][1],(0,0,1))
 def test_disjoint_components_retained(self):
  u=m.exact_core_union_boundary(self.branches([self.rect(0,0,1,1),self.rect(3,0,4,1)]));self.assertEqual(len(u['completeTrueAreaUnionBoundary']),8)
 def test_reversed_input_order_preserves_boundary_set(self):
  hs=[self.rect(0,0,2,2),self.rect(1,1,3,3)];one=m.exact_core_union_boundary(self.branches(hs));two=m.exact_core_union_boundary(self.branches(hs[::-1]));keys=lambda u:{tuple(sorted(r['completeClosedSegment']))for r in u['completeTrueAreaUnionBoundary']};self.assertEqual(keys(one),keys(two))
 def test_collinear_overlap_endpoints_retained(self):
  self.assertEqual(m.intersection_knots((F(0),F(0)),(F(3),F(0)),(F(1),F(0)),(F(4),F(0))),[(F(1),F(0)),(F(3),F(0))])
 def test_touching_point_not_removed_or_bridged(self):
  u=m.exact_core_union_boundary(self.branches([self.rect(0,0,1,1),self.rect(1,1,2,2)]));self.assertEqual(len(u['completeTrueAreaUnionBoundary']),8)
 def test_hole_remains_outside_core(self):
  hs=[self.rect(0,0,4,1),self.rect(0,3,4,4),self.rect(0,1,1,3),self.rect(3,1,4,3)];u=m.exact_core_union_boundary(self.branches(hs));self.assertFalse(any(m.contains_closed((F(2),F(2)),h)for h in u['completeCoreHulls']));self.assertTrue(any(a[0]==b[0]==1 for r in u['completeTrueAreaUnionBoundary']for a,b in [r['completeClosedSegment']]))
 def test_single_point_primitive_inventory_retained(self):
  u=m.exact_core_union_boundary(self.branches([[(1,2)]]));self.assertEqual(u['completeLowerDimensionalPrimitives'][0]['completeClosedPoints'],[(1,2)])
 def test_segment_primitive_inventory_retained(self):
  u=m.exact_core_union_boundary(self.branches([[(0,0),(2,0)]]));self.assertEqual(len(u['completeLowerDimensionalPrimitives']),1)
 def test_far_source_triangle_bytes_remain_unsplit(self):
  poly=[(10,3,10),(12,3,10),(10,3,12)];rows,u=self.partition(poly,[self.rect(0,0,1,1)]);self.assertEqual(len(rows),1);self.assertEqual(rows[0][0],[tuple(map(F,p))for p in poly]);self.assertEqual(rows[0][1],(0,0,0))
 def test_whole_original_layer_heights_stay_independent(self):
  low,_=self.partition([(0,2,0),(3,2,0),(0,2,3)],[self.rect(1,1,2,2)]);high,_=self.partition([(0,4,0),(3,4,0),(0,4,3)],[self.rect(1,1,2,2)]);self.assertTrue(all(p[1]==2 for q,_,_ in low for p in q));self.assertTrue(all(p[1]==4 for q,_,_ in high for p in q))
 def test_true_boundary_segment_nomination_keeps_touch(self):
  self.assertTrue(m.segment_touches_projection((F(1),F(0)),(F(1),F(2)),[(F(0),F(3),F(0)),(F(1),F(3),F(0)),(F(0),F(3),F(1))]))
 def test_boundary_segment_far_excluded_exactly(self):
  self.assertFalse(m.segment_touches_projection((F(5),F(5)),(F(5),F(7)),[(F(0),F(3),F(0)),(F(1),F(3),F(0)),(F(0),F(3),F(1))]))
 def test_symbolic_sides_use_no_finite_epsilon(self):
  h=[(F(0),F(0)),(F(1),F(0)),(F(1),F(1)),(F(0),F(1))];self.assertTrue(m.directional_inside((F(1,2),F(0)),(F(0),F(1)),h));self.assertFalse(m.directional_inside((F(1,2),F(0)),(F(0),F(-1)),h))
 def test_competing_branches_keep_exact_vertex_max_min(self):
  rows,_=self.partition([(-1,2,0),(3,2,0),(-1,2,3)],[self.rect(0,0,1,1),self.rect(F(1,2),F(1,2),2,2)]);self.assertTrue(rows)
 def test_positive_intrinsic_area_partition_preserved(self):
  poly=[(-1,3,-1),(3,3,-1),(-1,3,3)];rows,_=self.partition(poly,[self.rect(0,0,1,1)]);self.assertEqual(sum((m.old.intrinsic_area(q,1)for q,_,_ in rows),F(0)),m.old.intrinsic_area([tuple(map(F,p))for p in poly],1))
 def test_segment_endpoints_in_disconnected_cores_do_not_certify_gap(self):
  hs=[self.rect(F(0),F(0),F(1),F(1)),self.rect(F(2),F(0),F(3),F(1))];a=(F(0),F(1,2));b=(F(3),F(1,2));self.assertTrue(all(any(m.contains_closed(p,h)for h in hs)for p in [a,b]));self.assertFalse(m.closed_segment_union_coverage(a,b,hs)['covered'])
 def test_segment_closed_touching_area_union_complete(self):
  hs=[self.rect(F(0),F(0),F(1),F(1)),self.rect(F(1),F(0),F(2),F(1))];self.assertTrue(m.closed_segment_union_coverage((F(0),F(1,2)),(F(2),F(1,2)),hs)['covered'])
 def test_isolated_points_cannot_bridge_projected_segment(self):
  self.assertFalse(m.closed_segment_union_coverage((F(0),F(0)),(F(2),F(0)),[[(F(0),F(0))],[(F(2),F(0))]])['covered'])
 def test_collinear_segment_union_retains_closed_point_ties(self):
  proof=m.closed_segment_union_coverage((F(0),F(0)),(F(2),F(0)),[[(F(0),F(0)),(F(1),F(0))],[(F(1),F(0)),(F(2),F(0))]]);self.assertTrue(proof['covered']);self.assertEqual(len(proof['completeIntervals']),2)
 def test_collapsed_projection_point_requires_actual_membership(self):
  p=(F(0),F(0));self.assertTrue(m.closed_segment_union_coverage(p,p,[[p]])['covered']);self.assertFalse(m.closed_segment_union_coverage(p,p,[[(F(1),F(0))]])['covered'])
 def test_empty_union_and_empty_primitives_never_certify_segment(self):
  a=(F(0),F(0));b=(F(1),F(0));self.assertFalse(m.closed_segment_union_coverage(a,b,[])['covered']);self.assertFalse(m.closed_segment_union_coverage(a,b,[[]])['covered'])
 def test_vertical_original_facet_complete_segment_coverage(self):
  poly=[(F(0),F(0),F(0)),(F(0),F(2),F(0)),(F(0),F(2),F(2))];branches=self.branches([self.rect(-1,0,1,1),self.rect(-1,1,1,2)]);union=m.exact_core_union_boundary(branches);parts=m.partition_complete_core_union(poly,0,union);self.assertTrue(parts);self.assertTrue(all(inside for _,inside in parts));self.assertEqual(sum((m.old.intrinsic_area(p,0)for p,_ in parts),F(0)),m.old.intrinsic_area(poly,0))
if __name__=='__main__':unittest.main(verbosity=2)
