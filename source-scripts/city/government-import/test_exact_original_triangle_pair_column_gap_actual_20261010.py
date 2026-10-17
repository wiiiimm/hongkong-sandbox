"""Pinned Festival actual collapsed-facet counterexamples, no synthetic source."""
import unittest
from fractions import Fraction as F
import numpy as np
from run import ROOT,HERE,read,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_triangle_pair_column_gap_20261010 import verify
from exact_original_paired_finite_clearance_v2_20261010 import refine
class Actual(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  base=ROOT/'docs/astra-city/government-import';phys=base/'government-xl-terrain-recovery-festival-pair-original-terrain-current-v1-20261010';row=next(r for r in read(phys/'selection.json.gz')['rows'] if r['uid']=='landsd/91827:0');raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)=='786e89452ba921ce3b16ba1b899919d4965f829ea5fb7b1756cd6ab5ed4c2ef8';cls.tri=decode_original_world_triangles(raw);assert digest(cls.tri.tobytes())=='d0878dc75f48e8766db5cf9e27318d3605ee69fad4ffdd5821e0ad0c9a090d0c'
  runtime=next(r for r in read(HERE/'local'/phys.name/'runtime-geometry.json.gz')['rows'] if r['uid']==row['uid']);cls.ground=np.asarray(runtime['drawnGroundGeometry']).reshape(-1,3,3);cls.cached=read(base/'xl-terrain-recovery-20261010-festival-podium-current-paired-finite-clearance-v1/diagnostic.json.gz')['rows'][0];assert digest(cls.ground.tobytes())==cls.cached['completeGroundSHA256']
 def test_actual_upward_faces_preserve_raw_negative_but_local_finite_gap_positive(self):
  for i in [7093,7094,7361,7362]:
   raw=self.cached['allFaces'][i]['pairedExactOriginalFiniteBound'];self.assertLess(F(raw['exactCertifiedLowerClearanceM']),F(-1,2));new=refine(self.tri[i],self.ground,raw);self.assertTrue(new['existingOrdinaryClearanceBoundProved']);self.assertGreater(F(new['exactCertifiedLowerClearanceM']),1);self.assertEqual(new['rawPriorPairedProofVerbatim'],raw)
 def test_actual_local_gap_differs_from_unrelated_global_height_extrema(self):
  i=7361;raw=self.cached['allFaces'][i]['pairedExactOriginalFiniteBound'];p=next(p for p in raw['allExactFiniteSourceGroundPieces'] if p.get('collapsedProjectionConservative') and p['originalGroundFace']==4537);new=verify(self.tri[i],self.ground[4537]);self.assertLess(F(p['exactMinimumGapM']),-2);self.assertGreater(F(new['exactMinimumFiniteColumnGapM']),1)
 def test_actual_882_ground2703_is_accounted_not_dropped(self):
  raw=self.cached['allFaces'][882]['pairedExactOriginalFiniteBound'];new=refine(self.tri[882],self.ground,raw);pieces=[p for p in new['allExactFiniteSourceGroundPieces'] if p['originalGroundFace']==2703];self.assertEqual(len(pieces),1);self.assertTrue(pieces[0]['exactCompleteFiniteColumnProof']['exactClosedHorizontalProjectionsMeet']);self.assertTrue(new['existingOrdinaryClearanceBoundProved'])
 def test_genuine_burial_on_actual_same_column_rejects(self):
  s=self.tri[7361].copy();s[:,1]-=10;self.assertLess(F(verify(s,self.ground[4537])['exactMinimumFiniteColumnGapM']),F(-1,2))
 def test_changed_source_frozen_prior_rejects(self):
  s=self.tri[7361].copy();s[0,1]-=.001
  with self.assertRaises(AssertionError):refine(s,self.ground,self.cached['allFaces'][7361]['pairedExactOriginalFiniteBound'])
 def test_changed_current_ground_frozen_prior_rejects(self):
  g=self.ground.copy();g[4537,0,1]+=.001
  with self.assertRaises(AssertionError):refine(self.tri[7361],g,self.cached['allFaces'][7361]['pairedExactOriginalFiniteBound'])
 def test_real_tiny_projected_holes_remain_held(self):
  for i in [8458,8755]:
   new=refine(self.tri[i],self.ground,self.cached['allFaces'][i]['pairedExactOriginalFiniteBound']);self.assertFalse(new['groundProjectionCovered']);self.assertFalse(new['existingOrdinaryClearanceBoundProved']);self.assertGreater(F(new['exactCertifiedLowerClearanceM']),21)
if __name__=='__main__':unittest.main()
