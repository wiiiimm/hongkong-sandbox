import unittest
from fractions import Fraction as F
import numpy as np
from original_bound_facet_wall_context_v3_20261010 import best_original_vertex_exposure
class SlopingOriginalVertices(unittest.TestCase):
 def test_lower_original_vertex_can_be_exposed_while_highest_is_buried(self):
  g=np.array([[[0,0,0],[10,10,0],[0,0,10]]],float);p=best_original_vertex_exposure([[1,2,1],[3,2.5,1],[3,2,1]],g);self.assertEqual(p['actualExposedOriginalVertexIndex'],0);self.assertEqual(F(p['exactExposureLowerBoundM']),1)
 def test_all_buried_vertices_remain_unexposed(self):
  g=np.array([[[0,5,0],[10,5,0],[0,5,10]]],float);p=best_original_vertex_exposure([[1,2,1],[3,3,1],[3,2,1]],g);self.assertEqual(F(p['exactExposureLowerBoundM']),-2)
 def test_highest_overlapping_surface_cannot_be_omitted(self):
  g=np.array([[[0,0,0],[10,0,0],[0,0,10]],[[0,5,0],[10,5,0],[0,5,10]]],float);p=best_original_vertex_exposure([[1,2,1],[3,3,1],[3,2,1]],g);self.assertEqual(F(p['exactExposureLowerBoundM']),-2)
 def test_uncovered_original_vertex_rejects(self):
  with self.assertRaises(AssertionError):best_original_vertex_exposure([[0,1,0],[2,1,0],[0,1,1]],np.array([[[0,0,0],[1,0,0],[0,0,1]]],float))
 def test_zero_exposure_never_becomes_positive(self):
  p=best_original_vertex_exposure([[0,0,0],[1,0,0],[0,0,1]],np.array([[[0,0,0],[1,0,0],[0,0,1]]],float));self.assertEqual(F(p['exactExposureLowerBoundM']),0);self.assertFalse(p['fullAcceptance'])
if __name__=='__main__':unittest.main()
