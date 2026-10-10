import unittest,numpy as np
from run import ROOT,read,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_edge_finite_facade_distance_band_v2_20261010 import verify
from original_geometric_finite_facade_boundary_diagnostic_v2_20261010 import prepare_hosts,diagnose
class Synthetic(unittest.TestCase):
 def wall(self):return np.asarray([[[0,0,0],[0,1,0],[0,1,1]],[[0,0,0],[0,1,1],[0,0,1]]],float)
 def test_exact_limit(self):self.assertTrue(verify([[.1,0,0],[.1,1,0]],self.wall())['verifiedCompleteOriginalEdgeFiniteFacadeBand'])
 def test_next_double_beyond_limit(self):self.assertFalse(verify([[np.nextafter(.1,1),0,0],[np.nextafter(.1,1),1,0]],self.wall())['verifiedCompleteOriginalEdgeFiniteFacadeBand'])
 def test_partial_host_rejects(self):self.assertFalse(verify([[0,0,0],[0,2,0]],self.wall())['verifiedCompleteOriginalEdgeFiniteFacadeBand'])
 def test_roof_not_facade(self):self.assertFalse(verify([[0,0,0],[1,0,1]],self.wall()[:,:,[1,0,2]])['verifiedCompleteOriginalEdgeFiniteFacadeBand'])
 def test_nonfinite_rejects(self):
  with self.assertRaises(AssertionError):verify([[float('nan'),0,0],[0,1,0]],self.wall())
 def test_no_acceptance(self):
  r=verify([[0,0,0],[0,1,0]],self.wall());self.assertFalse(r['visualRoleAccepted']);self.assertFalse(r['structuralRootCredit']);self.assertFalse(r['installationApproved']);self.assertEqual(r['strictBandM'],.1)
class Actual(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  b=ROOT/'docs/astra-city/government-import';cls.graph=read(b/'xl-terrain-recovery-20261010-festival-complete-original-pair-support-v1/diagnostic.json.gz');rows=read(b/'government-xl-festival-two-originals-full-physical-20261007/selection.json.gz')['rows'];by={r['uid']:r for r in rows};cls.tri=np.concatenate([decode_original_world_triangles((ROOT/by[a['uid']]['candidate']['path']).read_bytes()) for a in cls.graph['actors']]);assert len(cls.tri)==35006 and digest(cls.tri.tobytes())=='e748d91dfc7073785a840a0c127f9466c4b2028086fa064c47ff1d4052333a71';cls.rootfaces=sorted(i for k in cls.graph['resolvedOriginalComponents'] for i in cls.graph['components'][k]['globalOriginalFaces']);cls.prepared=prepare_hosts(cls.tri,cls.rootfaces);cls.prior=read(b/'xl-terrain-recovery-20261010-festival-pair-complete-geometric-boundary-bands-v1/diagnostic.json.gz')
 def get(self,k):return diagnose(self.prepared,self.graph['components'][k]['globalOriginalFaces'])
 def test_actual176_old_gaps_resolved(self):
  old=next(r for r in self.prior['results'] if r['component']==176);self.assertFalse(old['sourceOnlyBoundaryBandPassed']);r=self.get(176);self.assertTrue(r['sourceOnlyBoundaryBandPassed']);self.assertTrue(any(not e['band']['priorWholeFiniteBranchBandPassed'] for e in r['completeOriginalGeometricBoundaryBands']))
 def test_actual178_old_gaps_resolved(self):self.assertTrue(self.get(178)['sourceOnlyBoundaryBandPassed'])
 def test_actual219_real_remaining_band_gap_preserved(self):self.assertFalse(self.get(219)['sourceOnlyBoundaryBandPassed'])
 def test_actual_two_small_plates_not_blanket_credited(self):
  for k in [258,259]:self.assertFalse(self.get(k)['sourceOnlyBoundaryBandPassed'])
 def test_actual263_unresolved_long_roof_fascia_preserved(self):self.assertFalse(self.get(263)['sourceOnlyBoundaryBandPassed'])
 def test_real_translation_detaches(self):
  old=next(r for r in self.prior['results'] if r['component']==176);edge=np.asarray(old['completeOriginalGeometricBoundaryBands'][0]['originalBoundaryEdge']);self.assertFalse(verify(edge+[.3,0,-.3],self.tri[self.rootfaces])['verifiedCompleteOriginalEdgeFiniteFacadeBand'])
if __name__=='__main__':unittest.main()
