"""Pinned real dense terrain and original/runtime source fixture; no acceptance."""
import unittest,numpy as np
from run import HERE,ROOT,read,digest
from exact_original_projection_coverage_20261009 import exact_coverage as old
from exact_original_projection_coverage_v2_20261010 import exact_coverage as new
from exact_original_face_conservative_clearance_v5_20261010 import verify
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
class ActualGreen18(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  p=HERE/'local/government-xl-terrain-recovery-green18-original-terrain-current-v1-20261010/runtime-geometry.json.gz';assert digest(p.read_bytes())=='66300f194bc3ba6238e797bc4b610c85d5526892af69cb6badb18e6169f842a6'
  r=read(p)['rows'][0];assert r['uid']=='landsd/6462:0';cls.world=np.asarray(r['position']).reshape(-1,3)[np.asarray(r['index']).reshape(-1,3)];cls.ground=np.asarray(r['drawnGroundGeometry']).reshape(-1,3,3)
  source=HERE/'local/government-xl-terrain-recovery-green18-original-terrain-current-v1-20261010/assets/d2d2c62ed2d29ffbf7ec4060c108f1c53eb784558120cb153a5d9482d60d493f.glb.gz';raw=source.read_bytes();assert digest(raw)=='d2d2c62ed2d29ffbf7ec4060c108f1c53eb784558120cb153a5d9482d60d493f';cls.original=decode_original_world_triangles(raw);assert cls.original.shape==cls.world.shape==(11088,3,3) and np.max(np.abs(cls.original-cls.world))<=1e-9
 def test_actual_47_facet_area_result_equal_frozen_algorithm(self):self.assertEqual(new(self.world[0],self.ground),old(self.world[0],self.ground))
 def test_actual_391_facet_interval_result_equal_frozen_algorithm(self):self.assertEqual(new(self.world[175],self.ground),old(self.world[175],self.ground))
 def test_actual_dense_617_facet_original_and_runtime_exact_coverage(self):
  for face in [self.original[12],self.world[12]]:
   proof=new(face,self.ground);self.assertIs(proof['exactProjectionCovered'],True);self.assertEqual(proof['exactUncoveredAreaM2'],'0');self.assertEqual(proof['conservativeAABBCandidateGroundFacets'],617);self.assertEqual(proof['nonzeroExactProjectedCandidateFacets'],605);self.assertEqual(proof['completeOriginalGroundTrianglesAccounted'],2505)
 def test_dense_proof_equals_recorded_frozen_algorithm(self):
  # Exact independent legacy output from the 191.00325382687151-second run.
  expected=dict(exactProjectionCovered=True,method='closed-facet-area-union',completeOriginalGroundTrianglesAccounted=2505,conservativeAABBCandidateGroundFacets=617,nonzeroExactProjectedCandidateFacets=605,sourceFaceSHA256='dbec73def2cd3886bd8ada6d91b4cb899d52e4640ad472e06414ecac91063ee5',completeGroundSHA256='0e49631bd9b4429a3c7a55c384d242b9b47d3419a8123b6452b70a8b4d4c6e57',noToleranceOrBufferCredit=True,exactUncoveredAreaM2='0',exactSourceProjectedAreaM2='30747137/262144',remainingPositiveAreaPieces=0)
  self.assertEqual(new(self.world[12],self.ground),expected)
 def test_missing_dense_terrain_rejects(self):self.assertIs(new(self.world[12],self.ground[:1])['exactProjectionCovered'],False)
 def test_dense_actual_conservative_bound_retains_limit(self):
  p=verify(self.world[12],self.ground);self.assertIs(p['existingOrdinaryClearanceBoundProved'],True);self.assertIs(p['fullAcceptance'],False);self.assertIs(p['installationApproved'],False)
if __name__=='__main__':unittest.main()
