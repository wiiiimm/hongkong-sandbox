"""Reject invented source adjacency in below-grade diagnostics."""
import unittest
import numpy as np
from original_below_grade_source_context_v2_20261101 import face_adjacency, exact_plane_key

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

class ExactPlaneTests(unittest.TestCase):
    def test_exact_tilted_plane_is_preserved(self):
        a=np.array([[0.,2,0],[2,3,0],[0,1,4]])
        b=np.array([[2.,3,0],[2,2,4],[0,1,4]])
        self.assertEqual(exact_plane_key(a),exact_plane_key(b))

    def test_one_ulp_out_of_plane_is_not_rounded(self):
        a=np.array([[0.,2,0],[2,3,0],[0,1,4]])
        b=np.array([[2.,3,0],[2,2,4],[0,1,4]])
        b[1,1]=np.nextafter(b[1,1],np.inf)
        self.assertNotEqual(exact_plane_key(a),exact_plane_key(b))

if __name__=='__main__':unittest.main()
