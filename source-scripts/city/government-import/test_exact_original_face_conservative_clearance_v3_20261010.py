import unittest,numpy as np
from exact_original_face_conservative_clearance_v3_20261010 import verify
class FiniteBound(unittest.TestCase):
 def test_high_ground_vertex_outside_actual_projection_not_used(self):
  f=np.array([[0,1,0],[.1,1,0],[0,1,.1]]);g=np.array([[[-1,-1,-1],[10,10,-1],[-1,-1,10]]]);p=verify(f,g);self.assertTrue(p['existingOrdinaryClearanceBoundProved']);self.assertFalse(p['sourcePlaneInversionUsed'])
 def test_high_ground_inside_finite_projection_fails(self):
  f=np.array([[0,1,0],[.1,1,0],[0,1,.1]]);g=np.array([[[-1,2,-1],[10,2,-1],[-1,2,10]]]);self.assertFalse(verify(f,g)['existingOrdinaryClearanceBoundProved'])
 def test_nearly_vertical_source_keeps_actual_low_vertex(self):
  f=np.array([[0,60,0],[1,61,1],[.5,62,.500000000000001]]);g=np.array([[[-2,0,-2],[3,0,-2],[3,0,3]],[[-2,0,-2],[3,0,3],[-2,0,3]]]);self.assertEqual(verify(f,g)['exactCertifiedLowerClearanceM'],'60')
 def test_exact_vertical_line_projection(self):
  f=np.array([[0,2,0],[1,2,1],[1,3,1]]);g=np.array([[[-2,0,-2],[3,0,-2],[3,0,3]],[[-2,0,-2],[3,0,3],[-2,0,3]]]);self.assertTrue(verify(f,g)['existingOrdinaryClearanceBoundProved'])
 def test_point_projection(self):
  f=np.array([[0,2,0],[0,3,0],[0,4,0]]);g=np.array([[[-1,0,-1],[2,0,-1],[-1,0,2]]]);self.assertTrue(verify(f,g)['existingOrdinaryClearanceBoundProved'])
 def test_overlap_upper_surface_is_not_omitted(self):
  f=np.array([[0,1,0],[.1,1,0],[0,1,.1]]);g=np.array([[[-1,0,-1],[10,0,-1],[-1,0,10]],[[-1,2,-1],[10,2,-1],[-1,2,10]]]);self.assertFalse(verify(f,g)['existingOrdinaryClearanceBoundProved'])
 def test_real_burial_cannot_pass(self):
  f=np.array([[0,-.501,0],[.1,1,0],[0,1,.1]]);g=np.array([[[-1,0,-1],[10,0,-1],[-1,0,10]]]);self.assertFalse(verify(f,g)['existingOrdinaryClearanceBoundProved'])
 def test_no_finite_projection_coverage(self):
  f=np.array([[0,1,0],[1,1,0],[0,1,1]]);g=np.array([[[0,0,0],[.1,0,0],[0,0,.1]]]);self.assertFalse(verify(f,g)['existingOrdinaryClearanceBoundProved'])
class NonRenderingGround(unittest.TestCase):
 def test_exact_zero_area_retained_without_height_credit(self):
  f=np.array([[0,1,0],[1,1,0],[0,1,1]]);g=np.array([[[-1,0,-1],[3,0,-1],[-1,0,3]],[[.2,10,.2],[.3,20,.3],[.4,30,.4]]]);g[1]=[[.25,10,.25],[.5,20,.5],[.75,30,.75]];p=verify(f,g);self.assertTrue(p['existingOrdinaryClearanceBoundProved']);rows=[r for r in p['allExactOriginalTerrainIntersectionHeightPieces'] if r.get('exactZeroAreaNonRenderingGroundFacet')];self.assertEqual(len(rows),1);self.assertFalse(rows[0]['groundHeightOrCoverageCredit'])
 def test_nonzero_vertical_surface_never_discarded(self):
  f=np.array([[0,1,0],[1,1,0],[0,1,1]]);g=np.array([[[-1,0,-1],[3,0,-1],[-1,0,3]],[[.25,10,.25],[.5,20,.5],[.75,30+2**-30,.75]]]);p=verify(f,g);self.assertFalse(p['existingOrdinaryClearanceBoundProved']);self.assertFalse(any(r.get('exactZeroAreaNonRenderingGroundFacet') for r in p['allExactOriginalTerrainIntersectionHeightPieces']))
 def test_actual_terrain_face_1306_exact_collinearity(self):
  from run import HERE,read
  g=read(HERE/'local/government-xl-terrain-recovery-ko-fung-original-pair-current-physical-v3-20261010/runtime-geometry.json.gz')['rows'][1];ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3);tri=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)]
  p=verify(tri[438],ground);self.assertTrue(p['existingOrdinaryClearanceBoundProved']);self.assertTrue(next(r for r in p['allExactOriginalTerrainIntersectionHeightPieces'] if r['originalGroundFace']==1306)['exactZeroAreaNonRenderingGroundFacet'])
if __name__=='__main__':unittest.main()
