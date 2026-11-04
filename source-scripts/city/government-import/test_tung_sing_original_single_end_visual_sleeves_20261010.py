import unittest,numpy as np
from run import ROOT,read
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from source_closed_components import components
from glorious_peak_original_mounted_detail_roles_v2_20261010 import component_role
from tung_sing_original_single_end_visual_sleeves_20261010 import source_roles,single_opening_role,SOURCE_SHA,WORLD_SHA,SPECS,FINITE_HOSTS
from exact_original_edge_finite_facade_distance_band_v2_20261010 import verify as finite_band
class ActualSource(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  x=read(ROOT/'docs/astra-city/government-import/government-xl-tung-sing-two-detached-original-context-20261010/diagnostic.json.gz');raw=next(ROOT/k for k in x['inputHashes'] if k.endswith('.glb.gz'));cls.tri=decode_original_world_triangles(raw.read_bytes());cls.parts=components(cls.tri)['components'];cls.host=cls.parts[1]['faceIndices']
 def test_actual_both_complete_visual_details_with_no_structural_credit(self):
  r=source_roles(self.tri,SOURCE_SHA,WORLD_SHA);self.assertEqual(r['all16OriginalVisualFacesRetained'],16)
  for v in r['completeSourceOnlyVisualRoles']:
   self.assertFalse(v['structuralRootCredit']);self.assertFalse(v['structuralBridgeCredit']);self.assertFalse(v['freeEndSupportCredit']);self.assertEqual(len(v['bothCompleteOriginalOpeningDispositions']),2);self.assertEqual(len(v['allOriginalFaces']),8)
   mount=v['bothCompleteOriginalOpeningDispositions'][v['completeOriginalMountedOpeningIndex']];self.assertTrue(all(e['completeOriginalFiniteEuclideanBand']['verifiedCompleteOriginalEdgeFiniteFacadeBand'] for e in mount['everyCompleteOriginalEdgeTrial']));self.assertEqual(len(mount['completeOriginalDirectedOpening']),4)
 def test_prior_two_end_axis_failures_remain(self):
  for k,faces in SPECS.items():
   with self.subTest(part=k),self.assertRaises(AssertionError):component_role(self.tri,faces,self.host,'authored-two-ended-mounted-visual-sleeve')
 def test_current_source_sha_mutation_rejected(self):
  with self.assertRaises(AssertionError):source_roles(self.tri,'0'*64,WORLD_SHA)
 def test_world_sha_mutation_rejected(self):
  with self.assertRaises(AssertionError):source_roles(self.tri,SOURCE_SHA,'0'*64)
 def test_unchanged_source_bytes_do_not_authorize_changed_world(self):
  t=self.tri.copy();t[9229,0,1]+=.000001
  with self.assertRaises(AssertionError):source_roles(t,SOURCE_SHA,WORLD_SHA)
 def test_geometry_mutation_cannot_supply_own_hash(self):
  import hashlib
  t=self.tri.copy();t[:,:,0]+=1
  with self.assertRaises(AssertionError):source_roles(t,SOURCE_SHA,hashlib.sha256(t.astype('<f8').tobytes()).hexdigest())
 def test_complete_eight_face_accounting_required(self):
  with self.assertRaises(AssertionError):single_opening_role(self.tri,SPECS[343][:-1],self.host,FINITE_HOSTS[343])
 def test_host_must_own_every_named_original_counterpart(self):
  with self.assertRaises(AssertionError):single_opening_role(self.tri,SPECS[343],self.host,FINITE_HOSTS[343]+[9229])
 def test_missing_host_rejected(self):
  with self.assertRaises(AssertionError):single_opening_role(self.tri,SPECS[343],[],FINITE_HOSTS[343])
 def test_detached_whole_opening_rejected(self):
  t=self.tri.copy();t[SPECS[343],:,1]+=20
  with self.assertRaises(AssertionError):single_opening_role(t,SPECS[343],self.host,FINITE_HOSTS[343])
 def test_wrong_source_winding_rejected(self):
  t=self.tri.copy();t[9229]=t[9229,::-1]
  with self.assertRaises(AssertionError):single_opening_role(t,SPECS[343],self.host,FINITE_HOSTS[343])
 def test_nan_world_rejected(self):
  t=self.tri.copy();t[0,0,0]=float('nan')
  with self.assertRaises(AssertionError):source_roles(t,SOURCE_SHA,WORLD_SHA)
class CompleteFiniteEdge(unittest.TestCase):
 def wall(self,xlo=-1,xhi=3):return np.asarray([[[xlo,-1,0],[xhi,-1,0],[xhi,1,0]],[[xlo,-1,0],[xhi,1,0],[xlo,1,0]]],float)
 def test_complete_finite_edge_accepted(self):self.assertTrue(finite_band([[0,0,.05],[2,0,.05]],self.wall())['verifiedCompleteOriginalEdgeFiniteFacadeBand'])
 def test_strict_band_no_increase(self):self.assertFalse(finite_band([[0,0,.100001],[2,0,.100001]],self.wall())['verifiedCompleteOriginalEdgeFiniteFacadeBand'])
 def test_partial_foot_cannot_cover_full_opening(self):self.assertFalse(finite_band([[0,0,.05],[2,0,.05]],self.wall(-1,.5))['verifiedCompleteOriginalEdgeFiniteFacadeBand'])
 def test_two_near_endpoints_do_not_cover_interior_gap(self):
  host=np.concatenate([self.wall(-.2,.2),self.wall(1.8,2.2)]);self.assertFalse(finite_band([[0,0,.05],[2,0,.05]],host)['verifiedCompleteOriginalEdgeFiniteFacadeBand'])
 def test_point_only_contact_rejected(self):self.assertFalse(finite_band([[0,0,0],[2,0,0]],self.wall(-1,0))['verifiedCompleteOriginalEdgeFiniteFacadeBand'])
 def test_infinite_plane_extension_not_finite_credit(self):self.assertFalse(finite_band([[4,0,.05],[6,0,.05]],self.wall())['verifiedCompleteOriginalEdgeFiniteFacadeBand'])
if __name__=='__main__':unittest.main()
