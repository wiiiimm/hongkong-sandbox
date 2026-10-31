import unittest
from fractions import Fraction as F
import numpy as np
from polyu_compatible_current_parent_regions_v1_draft_20261014 import forbidden_projection,strictly_enclosing_f32_hull,downward_parent_pieces,compatible_piece
def proof(points,gaps):return dict(violatesExistingOrdinaryBound=True,existingOrdinaryLowerBoundM='-1/2',completeConvexMaskedPairVertices=[dict(exactOriginalSourcePoint=list(map(str,p)),exactGapM=str(g))for p,g in zip(points,gaps)])
class Regions(unittest.TestCase):
 def test_partial_negative_subregion_is_exact(self):
  p=forbidden_projection(proof([(0,0,0),(2,0,0),(0,0,2)],[-1,0,0]));self.assertEqual(set(p),{(F(0),F(0)),(F(1),F(0)),(F(0),F(1))})
 def test_boundary_only_is_not_invented_failure(self):
  with self.assertRaises(AssertionError):forbidden_projection(proof([(0,0,0),(1,0,0),(0,0,1)],[F(-1,2)]*3))
 def test_vertical_bad_column_retains_closed_line(self):
  p=forbidden_projection(proof([(0,0,0),(0,0,1),(0,1,0)],[-1,-1,0]));self.assertEqual({x for x,z in p},{F(0)})
  hull,cells=strictly_enclosing_f32_hull(p);self.assertTrue(len(hull)>=4);self.assertTrue(cells)
 def test_exact_f32_point_gets_strict_adjacent_cells(self):
  hull,cells=strictly_enclosing_f32_hull([(F(1),F(2))]);self.assertEqual(len(hull),4)
  self.assertLess(F(cells[0]['strictXCell'][0]),1);self.assertGreater(F(cells[0]['strictXCell'][1]),1)
 def test_non_dyadic_cell_is_not_distance_buffer(self):
  _,cells=strictly_enclosing_f32_hull([(F(1,3),F(2,3))]);lo,hi=map(F,cells[0]['strictXCell']);self.assertLess(lo,F(1,3));self.assertGreater(hi,F(1,3))
  self.assertEqual(float(np.nextafter(np.float32(float(lo)),np.float32(np.inf))),float(hi))
 def test_parent_height_floor_never_lifts_plane(self):
  face=[(F(0),F(1,3),F(0)),(F(1),F(1,3),F(0)),(F(0),F(1,3),F(1))]
  pieces=downward_parent_pieces(face,face,{})
  self.assertTrue(pieces);self.assertTrue(all(F(v)<=0 for p in pieces for v in p['exactOwnParentPlanePackingResidualM']))
 def test_real_burial_rejected_and_other_world_retained(self):
  w=np.array([[[0,0,0],[1,0,0],[0,0,1]]],dtype='<f8');lo=w[:,:,[0,2]].min(1);hi=w[:,:,[0,2]].max(1)
  out=compatible_piece([[0,1,0],[1,1,0],[0,1,1]],{'a':(w,lo,hi,'a'),'b':(w,lo,hi,'b')})
  self.assertFalse(out['eligible']);self.assertEqual(len(out['worlds']),2)
if __name__=='__main__':unittest.main()
