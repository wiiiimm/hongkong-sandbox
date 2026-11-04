"""UNEXECUTED focused actual/adverse pure constructor boundary fixtures."""
import unittest,hashlib
from fractions import Fraction as F
import numpy as np
import polyu_sports_authentic_local_core_parent_draft_v1_20261013 as m
class FocusedBoundary(unittest.TestCase):
 def build(self,source,core=(0,0,10,10),parents=None,ids=None):
  source=np.asarray(source,dtype='<f8');parents=parents or [[[-10,3,-10],[20,3,-10],[-10,3,20]],[[20,3,-10],[20,3,20],[-10,3,20]]];ids=list(range(len(source)))if ids is None else ids
  return m.construct(source,ids,list(map(F,core)),parents,expected_sha256=hashlib.sha256(source.tobytes()).hexdigest(),declared_source_faces=100)
 def test_complete_whole_source_core_no_internal_split(self):
  out,a=self.build([[[1,2,1],[8,2,1],[1,2,8]]]);self.assertEqual(sum(r['classification']=='original-source-core'for r in a['completeOutputFacetLineage']),1)
 def test_two_genuine_layers_retained(self):
  _,a=self.build([[[1,2,1],[8,2,1],[1,2,8]],[[1,4,1],[8,4,1],[1,4,8]]]);self.assertEqual({r['globalOriginalTerrainFacet']for r in a['completeOutputFacetLineage']if r['classification']=='original-source-core'},{0,1})
 def test_vertical_original_layer_not_normal_filtered(self):
  _,a=self.build([[[1,0,1],[1,4,1],[1,0,8]]]);self.assertTrue(a['completeOriginalFacetAccounts'][0]['originalVerticalFacet']);self.assertTrue(any(r['classification']=='original-source-core'for r in a['completeOutputFacetLineage']))
 def test_exact_zero_source_record_retained(self):
  _,a=self.build([[[2,1,2]]*3]);self.assertTrue(a['completeOriginalFacetAccounts'][0]['noHeightOrBridgeCredit']);self.assertTrue(any(r['classification']=='original-source-degenerate'for r in a['completeOutputFacetLineage']))
 def test_source_outside_active_accounted(self):
  _,a=self.build([[[18,1,18],[19,1,18],[18,1,19]]]);self.assertEqual(a['completeOriginalFacetAccounts'][0]['exactIncludedIntrinsicArea'],'0');self.assertTrue(a['completeOriginalFacetAccounts'][0]['completeSourcePlanePartition'])
 def test_closed_core_boundary_vertical_kept_once(self):
  _,a=self.build([[[0,0,1],[0,4,1],[0,0,8]]]);self.assertEqual(sum(r['classification']=='original-source-core'for r in a['completeOutputFacetLineage']),1)
 def test_changed_collar_label_never_original_source_claim(self):
  _,a=self.build([[[-2,2,1],[2,2,1],[-2,2,8]]]);self.assertTrue(any(r['classification']=='changed-five-metre-collar'for r in a['completeOutputFacetLineage']));self.assertTrue(a['transitionIsNewVertexInterpolatedSurfaceNotOriginalTIN'])
 def test_outer_boundary_zero_alpha_matches_parent_before_packing(self):
  _,a=self.build([[[-5,2,1],[-1,2,1],[-5,2,8]]]);pairs=[(before,after)for r in a['completeOutputFacetLineage']if r['classification']=='changed-five-metre-collar'for before,after in zip(r['exactOriginalPoints'],r['exactProposedPoints'])if F(before[0])==-5];self.assertTrue(pairs);self.assertTrue(all(F(after[1])==3 for before,after in pairs))
 def test_exact_source_plane_core_correspondence(self):
  _,a=self.build([[[-1,1,1],[5,7,1],[-1,1,8]]]);self.assertTrue(all(F(p[1])==F(p[0])+2 for r in a['completeOutputFacetLineage']if r['classification']=='original-source-core'for p in r['exactProposedPoints']))
 def test_complete_parent_exterior_partition(self):
  _,a=self.build([[[1,2,1],[8,2,1],[1,2,8]]]);self.assertTrue(all(F(r['exactRemovedByActiveArea'])+F(r['exactRetainedExteriorArea'])==F(r['exactWholeArea'])for r in a['completeCapturedParentAccounts']))
 def test_collapsed_packed_fragment_retained(self):
  _,a=self.build([[[1,2,1],[1+2**-26,2,1],[1,2,1+2**-26]]]);self.assertTrue(a['realFloat32CollapsedOutputFacets'])
 def test_no_budget_or_acceptance_transfer(self):
  _,a=self.build([[[1,2,1],[8,2,1],[1,2,8]]]);self.assertEqual(a['triangleBudget'],25000);self.assertFalse(a['currentAcceptance']);self.assertFalse(a['physicalAccepted']);self.assertTrue(a['noAutomaticOverlapApproval'])
 def test_nonfinite_source_rejected(self):
  with self.assertRaises(AssertionError):self.build([[[1,float('nan'),1],[8,2,1],[1,2,8]]])
 def test_duplicate_original_ids_rejected(self):
  with self.assertRaises(AssertionError):self.build([[[1,2,1],[8,2,1],[1,2,8]]]*2,ids=[1,1])
 def test_collar_outside_parent_rejected(self):
  with self.assertRaises(AssertionError):self.build([[[1,2,1],[8,2,1],[1,2,8]]],parents=[[[0,3,0],[10,3,0],[0,3,10]]])
 def test_missing_actual_parent_collar_coverage_rejected(self):
  with self.assertRaises(AssertionError):self.build([[[-2,2,1],[2,2,1],[-2,2,8]]],parents=[[[-10,3,-10],[20,3,-10],[20,3,20]]])
 def test_all_four_unused_bounds_in_core(self):
  q=[[[0,0,0],[1,1,1]],[[0,0,0],[2,1,1]],[[0,0,-3],[1,1,1]],[[-4,0,0],[1,1,5]]];self.assertEqual(m.bounds_core(q),list(map(F,[-4,-3,2,5])))
 def test_missing_arithmetic_bounds_rejected(self):
  with self.assertRaises(AssertionError):m.bounds_core([[[0,0,0],[1,1,1]]]*3)

 def parent_fixture(self):
  p=dict(w=4,h=3,elev=[3.]*12,vegetation=[0]*12,meta=dict(georef=dict(aE=10,aN=-10,bE=834500,bN=816500,W=4,H=3)))
  t=[[[m.old.f32(v)for v in q]for q in tri]for tri in m.old.parent_faces(p,[0,0,3,2])];return p,t
 def test_parent_cells_derived_from_captured_coordinates(self):
  p,t=self.parent_fixture();cells,domain,proof=m.captured_parent_grid(p,t);self.assertEqual(cells,[0,0,3,2]);self.assertTrue(proof['meshIndexOrdinalsNotUsedAsRasterIndices'])
 def test_parent_captured_winding_preserved_not_reinterpreted(self):
  p,t=self.parent_fixture();t=[list(reversed(q))for q in t];_,_,proof=m.captured_parent_grid(p,t);self.assertTrue(proof['capturedOrientationRetainedForConstruction'])
 def test_changed_parent_height_rejected(self):
  p,t=self.parent_fixture();t[0][0][1]+=1
  with self.assertRaises(AssertionError):m.captured_parent_grid(p,t)
 def test_missing_captured_parent_facet_rejected(self):
  p,t=self.parent_fixture()
  with self.assertRaises(AssertionError):m.captured_parent_grid(p,t[:-1])
if __name__=='__main__':unittest.main(verbosity=2)
