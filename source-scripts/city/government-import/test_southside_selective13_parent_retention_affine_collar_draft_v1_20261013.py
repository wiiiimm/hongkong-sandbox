"""UNEXECUTED local collar fixtures; no source or terrain construction."""
import unittest
from fractions import Fraction as F
from southside_selective13_parent_retention_affine_collar_draft_v1_20261013 import prepare_branches,alpha_at,complete_changed_projection_domains,partition_retention_alpha,old

def union(*polygons):
 return dict(completeRawDomainRecords=[dict(uid=f'fixture/{i}',domainID='original-'+str(i),domainKind='fixture-only',completeXZPoints=[[str(F(v))for v in p]for p in poly])for i,poly in enumerate(polygons)])
class CollarFixtures(unittest.TestCase):
 def test_core_closed_triangle_vertices_and_interior(self):
  b=prepare_branches(union([(0,0),(1,0),(0,1)]))
  for p in [(0,0),(1,0),(0,1),(F(1,4),F(1,4))]:self.assertEqual(alpha_at(*p,b),1)
 def test_exact_five_metre_and_next_double_boundary(self):
  b=prepare_branches(union([(0,0),(1,0),(0,1)]));self.assertEqual(alpha_at(6,0,b),0);self.assertEqual(alpha_at(F(11,2),0,b),F(1,10));self.assertEqual(alpha_at(F(6)+F(1,2**50),0,b),0)
 def test_acute_corner_cannot_expand_beyond_axis_five_metres(self):
  b=prepare_branches(union([(0,0),(100,0),(100,F(1,1000))]));self.assertEqual(alpha_at(-10,0,b),0);self.assertEqual(alpha_at(106,0,b),0)
 def test_original_segment_and_point_obligations_not_area_filtered(self):
  b=prepare_branches(union([(0,0),(1,1),(F(1,2),F(1,2))],[(20,20)]));self.assertEqual(alpha_at(F(1,2),F(1,2),b),1);self.assertEqual(alpha_at(0,5,b),F(1,5));self.assertEqual(alpha_at(23,24,b),F(1,5))
 def test_identical_mask_preserves_all_thirteen_lineages(self):
  q=union(*([[(0,0),(1,0),(0,1)]]*13));b=prepare_branches(q);self.assertEqual(len(b),1);self.assertEqual(b[0]['completeOriginalDomainLineage'],q['completeRawDomainRecords'])
 def test_complete_changed_closed_hull_includes_every_outer_boundary(self):
  b=prepare_branches(union([(0,0),(1,0),(0,1)]));d=complete_changed_projection_domains(b);polys=[[(F(x),F(0),F(z))for x,z in r['completeXZPoints']]for r in d]
  self.assertEqual(sum(old.intrinsic_area(p,1)for p in polys),F(241,2));self.assertTrue(all('UNQUALIFIED'in r['domainKind']for r in d));self.assertIn((F(-5),F(-5)),b[0]['closedOuterHull'])
 def test_exact_affine_partition_retains_whole_original_surface_area(self):
  b=prepare_branches(union([(0,0),(1,0),(0,1)]));p=[(F(-6),F(3),F(-6)),(F(7),F(3),F(-6)),(F(-6),F(3),F(7))];parts=partition_retention_alpha(p,b,1)
  self.assertEqual(sum(old.intrinsic_area(q,1)for q,_,_ in parts),old.intrinsic_area(p,1));self.assertTrue(all(v[1]==3 for q,_,_ in parts for v in q))
 def test_vertical_boundary_ties_never_duplicate_real_area(self):
  b=prepare_branches(union([(0,0),(1,0),(0,1)],[(0,0),(0,1),(1,0)]));p=[(F(0),F(0),F(-6)),(F(0),F(10),F(-6)),(F(0),F(0),F(7))];parts=partition_retention_alpha(p,b,0)
  self.assertEqual(sum(old.intrinsic_area(q,0)for q,_,_ in parts),old.intrinsic_area(p,0))
if __name__=='__main__':unittest.main()
