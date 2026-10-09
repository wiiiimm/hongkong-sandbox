"""Actual complete untouched source fixtures, not nearest-point substitutes."""
import unittest
import numpy as np
from run import ROOT,read,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_local_perpendicular_boundary_diagnostic_20261010 import prepare_hosts,diagnose
class ActualSourceTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  base=ROOT/'docs/astra-city/government-import';selection=read(base/'government-xl-terrain-recovery-ying-hoi-existing-terrain-current-v1-20261010/selection.json.gz');cls.graph=read(base/'xl-terrain-recovery-20261010-ying-hoi-fresh-original-support-replay-v1/diagnostic.json.gz');expected={'landsd/205663:0':'97f824a1699c079e1d0e98962dd76175e384500340bbf22a732f5b92730ac502','landsd/207957:0':'82e6a654d9ac5451271f8fce1cf82c0a234dd9e67649a47f4e51bfffeb2088be'};parts=[]
  for row in selection['rows']:
   raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==expected[row['uid']]==row['sourceSHA256'];parts.append(decode_original_world_triangles(raw))
  cls.tri=np.concatenate(parts);assert cls.tri.shape==(11590,3,3) and digest(cls.tri.tobytes())=='1ea98c6dd5f75c1102842aa585a2b8a1fde1eb39a3ccc5e406fe56866af427e6';assert len(cls.graph['components'])==655 and len(cls.graph['resolvedOriginalComponents'])==455;ids=sorted(i for k in cls.graph['resolvedOriginalComponents'] for i in cls.graph['components'][k]['globalOriginalFaces']);cls.prepared=prepare_hosts(cls.tri,ids)
 def check_component(self,k):return diagnose(self.prepared,self.graph['components'][k]['globalOriginalFaces'])
 def test_actual_complete_opening_passes(self):self.assertTrue(self.check_component(223)['sourceOnlyBoundaryBandPassed'])
 def test_actual_above_band_separation_rejects(self):
  self.assertFalse(self.check_component(276)['sourceOnlyBoundaryBandPassed']);self.assertFalse(self.check_component(277)['sourceOnlyBoundaryBandPassed'])
 def test_nearest_facet_minima_do_not_replace_whole_perimeter(self):self.assertFalse(self.check_component(565)['sourceOnlyBoundaryBandPassed'])
 def test_actual_original_winding_conflict_stays_rejected(self):self.assertIn('nonmanifold-or-inconsistent-original-winding',self.check_component(254)['reasons'])
 def test_actual_source_cannot_gain_role_or_root_credit(self):
  d=self.check_component(223);self.assertFalse(d['visualRoleAccepted']);self.assertFalse(d['structuralRootCredit']);self.assertFalse(d['installationApproved'])
if __name__=='__main__':unittest.main()
