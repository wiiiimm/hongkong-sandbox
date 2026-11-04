"""Reject invented source adjacency in below-grade diagnostics."""
import unittest
import numpy as np
from original_below_grade_source_context_v1_20261101 import face_adjacency

class ExactSourceAdjacencyTests(unittest.TestCase):
    def test_reversed_nonzero_edge_connects(self):
        tri=np.array([[[0.,0,0],[1,0,0],[0,0,1]],[[1.,0,0],[0,0,0],[0,1,0]]])
        self.assertEqual(face_adjacency(tri)[0],{1})

    def test_point_only_never_bridges(self):
        tri=np.array([[[0.,0,0],[1,0,0],[0,0,1]],[[0.,0,0],[0,1,0],[0,1,1]]])
        self.assertFalse(face_adjacency(tri)[0])

    def test_one_ulp_edge_displacement_never_bridges(self):
        tri=np.array([[[0.,0,0],[1,0,0],[0,0,1]],[[1.,0,0],[0,0,0],[0,1,0]]])
        tri[1,:2,1]=np.nextafter(0.,1.)
        self.assertFalse(face_adjacency(tri)[0])

if __name__=='__main__':unittest.main()
