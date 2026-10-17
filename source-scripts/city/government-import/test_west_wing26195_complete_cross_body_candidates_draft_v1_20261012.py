import unittest,numpy as np
from west_wing26195_complete_cross_body_candidates_draft_v1_20261012 import candidates
class Closed(unittest.TestCase):
 def test_complete_vs_allpairs(self):
  rng=np.random.default_rng(12);w=rng.integers(-4,5,(30,3,3)).astype(float);cs=[list(range(k,k+5))for k in range(0,30,5)];got,l=candidates(w,cs);lo=w.min(1);hi=w.max(1);expected=[(i,j)for i in range(30)for j in range(i+1,30)if l[i]!=l[j]and np.all(hi[i]>=lo[j])and np.all(hi[j]>=lo[i])];self.assertEqual(got,expected)
 def test_vertical_closed_touch_retained(self):
  w=np.array([[[0,0,0],[0,1,0],[0,1,1]],[[0,1,0],[0,2,0],[0,2,1]]],float);self.assertEqual(candidates(w,[[0],[1]])[0],[(0,1)])
 def test_point_closed_touch_retained(self):
  w=np.array([[[0,0,0]]*3,[[0,0,0],[1,0,0],[0,1,0]]],float);self.assertEqual(candidates(w,[[0],[1]])[0],[(0,1)])
 def test_tiny_exact_y_separation_excluded(self):
  w=np.array([[[0,0,0],[1,0,0],[0,0,1]],[[0,2**-40,0],[1,2**-40,0],[0,2**-40,1]]]);self.assertEqual(candidates(w,[[0],[1]])[0],[])
 def test_same_body_not_cross(self):
  w=np.zeros((2,3,3));self.assertEqual(candidates(w,[[0,1]])[0],[])
 def test_duplicate_missing_partition_rejected(self):
  with self.assertRaises(AssertionError):candidates(np.zeros((3,3,3)),[[0,1],[1]])
 def test_nonfinite_rejected(self):
  w=np.zeros((2,3,3));w[1,0,0]=np.nan
  with self.assertRaises(AssertionError):candidates(w,[[0],[1]])
class GraphGates(unittest.TestCase):
 def row(self,a,b,dimension=1,primitive=[2,2],crossing=False):return dict(originalBodyLabels=[a,b],dimension=dimension,actualFinitePrimitiveDimensions=primitive,bothRelativeInteriorSurfaceCrossing=crossing)
 def graph(self,rows,exclude=False):
  from west_wing26195_complete_current_body_contact_graph_draft_v1_20261012 import graph
  return graph(3,rows,exclude_interior=exclude)
 def test_point_does_not_bridge(self):self.assertEqual(self.graph([self.row(0,1,dimension=0)])['unreachedOriginalBodies'],[1,2])
 def test_actual_zero_face_does_not_bridge(self):self.assertEqual(self.graph([self.row(0,1,primitive=[1,2])])['unreachedOriginalBodies'],[1,2])
 def test_crossing_is_separate_negative(self):
  self.assertEqual(self.graph([self.row(0,1,crossing=True)])['unreachedOriginalBodies'],[2])
  self.assertEqual(self.graph([self.row(0,1,crossing=True)],True)['unreachedOriginalBodies'],[1,2])
 def test_transitive_surface_context_only(self):
  g=self.graph([self.row(0,1),self.row(1,2)]);self.assertEqual(g['unreachedOriginalBodies'],[]);self.assertTrue(g['root0IsConditionalNotAccepted']);self.assertTrue(g['positiveSurfaceContactIsNotStructuralSupport'])
if __name__=='__main__':unittest.main()
