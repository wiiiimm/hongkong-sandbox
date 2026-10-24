import unittest,numpy as np
from exact_original_projection_coverage_20261009 import exact_coverage
def face(points):return np.array([[x,0,z] for x,z in points],float)
class ExactCoverageTests(unittest.TestCase):
 def test_two_closed_facets_cover_source_across_shared_seam(self):
  source=face([(0,0),(1,0),(1,1)]);ground=np.array([face([(0,0),(1,0),(0,1)]),face([(1,0),(1,1),(0,1)])]);self.assertTrue(exact_coverage(source,ground)['exactProjectionCovered'])
 def test_real_tiny_area_gap_is_never_given_credit(self):
  source=face([(0,0),(1,0),(1,1)]);ground=np.array([face([(0,0),(1,0),(1,1-1e-12)])]);self.assertFalse(exact_coverage(source,ground)['exactProjectionCovered'])
 def test_vertical_wall_line_closed_union(self):
  source=np.array([[0,0,0],[1,1,0],[0,1,0]],float);ground=np.array([face([(0,-1),(1,-1),(0,1)]),face([(1,-1),(1,1),(0,1)])]);self.assertTrue(exact_coverage(source,ground)['exactProjectionCovered'])
 def test_real_tiny_interval_gap_is_not_buffered(self):
  source=np.array([[0,0,0],[1,1,0],[0,1,0]],float);ground=np.array([face([(0,-1),(.5,-1),(0,1)]),face([(.5,-1),(.5,1),(0,1)]),face([(.5+1e-12,-1),(1,-1),(.5+1e-12,1)]),face([(1,-1),(1,1),(.5+1e-12,1)])]);self.assertFalse(exact_coverage(source,ground)['exactProjectionCovered'])
 def test_original_point_on_closed_triangle_boundary(self):
  source=np.array([[0,0,0],[0,1,0],[0,2,0]],float);ground=np.array([face([(0,0),(1,0),(0,1)])]);self.assertTrue(exact_coverage(source,ground)['exactProjectionCovered'])
 def test_missing_point_ground_rejects(self):
  source=np.array([[0,0,0],[0,1,0],[0,2,0]],float);ground=np.array([face([(1,1),(2,1),(1,2)])]);self.assertFalse(exact_coverage(source,ground)['exactProjectionCovered'])
if __name__=='__main__':unittest.main()
