"""Actual source fixtures, preserving the old perpendicular seam failures."""
import unittest
import numpy as np
from run import ROOT,read,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_edge_finite_facade_distance_band_20261010 import verify
from original_local_finite_facade_boundary_diagnostic_20261010 import prepare_hosts,diagnose
class Actual(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  b=ROOT/'docs/astra-city/government-import';cls.graph=read(b/'xl-terrain-recovery-20261010-festival-podium-independent-original-support-v1/diagnostic.json.gz');row=next(r for r in read(b/'government-xl-festival-two-originals-full-physical-20261007/selection.json.gz')['rows'] if r['uid']=='landsd/91827:0');raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)=='786e89452ba921ce3b16ba1b899919d4965f829ea5fb7b1756cd6ab5ed4c2ef8';cls.tri=decode_original_world_triangles(raw);assert len(cls.tri)==18484 and digest(cls.tri.tobytes())=='d0878dc75f48e8766db5cf9e27318d3605ee69fad4ffdd5821e0ad0c9a090d0c';roots=cls.graph['resolvedOriginalComponents'];cls.ids=sorted(i for k in roots for i in cls.graph['components'][k]['globalOriginalFaces']);cls.prepared=prepare_hosts(cls.tri,cls.ids);cls.old=read(b/'xl-terrain-recovery-20261010-festival-original-three-mount-boundaries-v1/diagnostic.json.gz')['results'][1]
 def test_actual_two_old_seam_gaps_complete_finite_edge_band(self):
  rows=self.old['completeOriginalLoops'][0]['everyOriginalBoundaryEdgePerpendicularBand'];fail=[r for r in rows if not r['band']['verifiedCompleteOriginalEdgePerpendicularBand']];self.assertEqual([r['originalBoundaryFace'] for r in fail],[5316,5313])
  for r in fail:
   p=verify(r['originalBoundaryEdge'],self.tri[self.ids]);self.assertFalse(p['originalPerpendicularFootRoutePassed']);self.assertTrue(p['verifiedCompleteOriginalEdgeFiniteFacadeBand']);self.assertEqual(p['exactFacetAndEdgeCertifiedMergedIntervals'],[['0','1']]);self.assertFalse(p['structuralRootCredit'])
 def test_all_three_complete_original_openings(self):
  for k in [46,53,58]:
   p=diagnose(self.prepared,self.graph['components'][k]['globalOriginalFaces']);self.assertTrue(p['sourceOnlyBoundaryBandPassed']);self.assertFalse(p['visualRoleAccepted'])
 def test_real_outward_detachment_rejects(self):
  edge=np.asarray(self.old['completeOriginalLoops'][0]['everyOriginalBoundaryEdgePerpendicularBand'][0]['originalBoundaryEdge']);normal=np.cross(self.tri[9033,1]-self.tri[9033,0],self.tri[9033,2]-self.tri[9033,0]);normal/=np.linalg.norm(normal)
  self.assertFalse(verify(edge+.3*normal,self.tri[self.ids])['verifiedCompleteOriginalEdgeFiniteFacadeBand'])
 def test_omitted_actual_host_triangles_reject(self):
  rows=self.old['completeOriginalLoops'][0]['everyOriginalBoundaryEdgePerpendicularBand'];ids=[i for i in self.ids if i not in [9033,9034]]
  self.assertFalse(verify(rows[0]['originalBoundaryEdge'],self.tri[ids])['verifiedCompleteOriginalEdgeFiniteFacadeBand'])
if __name__=='__main__':unittest.main()
