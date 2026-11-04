"""UNEXECUTED selective13 closed-union/source-plane adverse fixtures."""
import unittest
from fractions import Fraction as F
from southside_selective13_guard_union_parent_correspondence_draft_v1_20261013 import complete_union_atoms,parent_plane_correspondence,complete_closed_parent_coverage,partition_original_surface_by_union

def domains(points=((0,0),(2,0),(0,2))):
 return {'fixture/'+str(i):[dict(domainID='full',domainKind='complete-guard-triangle',completeXZPoints=[list(p)for p in points])]for i in range(13)}
BASE=[[[0,0,0],[2,0,0],[0,0,2]]]
class Selective13Tests(unittest.TestCase):
 def test_exact_duplicate_union_atom_retains_all13_lineages(self):
  a=complete_union_atoms(domains());self.assertEqual(len(a['atoms']),1);self.assertEqual(len(a['atoms'][0]['completeOriginalDomainLineage']),13);self.assertEqual(len(a['completeRawDomainRecords']),13)
 def test_one_conflicting_form_rejected(self):
  d=domains();d['landsd/311760:0']=d.pop('fixture/0')
  with self.assertRaises(AssertionError):complete_union_atoms(d)
 def test_point_and_segment_domains_retained_and_covered(self):
  d=domains();d['fixture/0']+=[dict(domainID='point',domainKind='unused-point',completeXZPoints=[[0,0]]),dict(domainID='segment',domainKind='vertical-projection',completeXZPoints=[[0,0],[0,2]])];a=complete_union_atoms(d);self.assertEqual(len(a['completeDegenerateDomainRecords']),2);self.assertTrue(complete_closed_parent_coverage(a,BASE)['allClosedPrimitivesCovered'])
 def test_actual_parent_coverage_missing_segment_end_fails(self):
  d=domains();d['fixture/0'].append(dict(domainID='segment',domainKind='vertical-projection',completeXZPoints=[[0,0],[0,3]]));p=complete_closed_parent_coverage(complete_union_atoms(d),BASE);self.assertFalse(p['allClosedPrimitivesCovered'])
 def test_exact_parent_vertex_correspondence_allows_winding_only(self):self.assertEqual(parent_plane_correspondence(BASE,[list(reversed(BASE[0]))])['uniqueActualBaselineFacetBySavedGroundFacet'],[0])
 def test_changed_parent_height_not_plane_fitted(self):
  changed=[[[0,0,0],[2,F(1,2**20),0],[0,0,2]]]
  with self.assertRaises(AssertionError):parent_plane_correspondence(BASE,changed)
 def test_duplicate_parent_facet_ambiguity_rejected(self):
  with self.assertRaises(AssertionError):parent_plane_correspondence(BASE,BASE+BASE)
 def test_vertical_original_surface_partition_retains_real3d_area(self):
  r=partition_original_surface_by_union([[0,0,0],[0,2,0],[0,2,2]],complete_union_atoms(domains()));self.assertTrue(r['whole3DPartitionComplete']);self.assertEqual(r['exactOutsideUnionIntrinsicArea'],'0');self.assertEqual(r['exactWholeIntrinsicArea'],r['exactInsideUnionIntrinsicArea'])
 def test_closed_point_touch_has_no_invented_real_area(self):
  r=partition_original_surface_by_union([[2,0,0],[3,0,0],[2,0,1]],complete_union_atoms(domains()));self.assertEqual(r['exactInsideUnionIntrinsicArea'],'0');self.assertEqual(r['exactWholeIntrinsicArea'],r['exactOutsideUnionIntrinsicArea'])
 def test_real_collapsed_original_descriptor_retained(self):
  r=partition_original_surface_by_union([[0,0,0],[0,0,0],[1,0,0]],complete_union_atoms(domains()));self.assertTrue(r['descriptorOnlyNoSurfaceCredit']);self.assertIn('originalCollapsedFacetVerbatim',r)
if __name__=='__main__':unittest.main()
