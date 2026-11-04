import unittest
from exact_closed_shell_point_20261009 import point_membership


def tetra():
    a,b,c,d=[0,0,0],[1,0,0],[0,1,0],[0,0,1]
    return [[a,c,b],[a,b,d],[a,d,c],[b,c,d]]


class ExactPointTests(unittest.TestCase):
    def test_strict_interior(self):
        self.assertTrue(point_membership([.1,.1,.1],tetra())['strictlyInside'])

    def test_detached_point(self):
        r=point_membership([2,2,2],tetra())
        self.assertFalse(r['strictlyInside']);self.assertEqual(r['classification'],'outside')

    def test_vertex_and_face_boundary_not_inside(self):
        for p in [[0,0,0],[.25,.25,0]]:
            self.assertEqual(point_membership(p,tetra())['classification'],'boundary')

    def test_arbitrarily_small_exterior_gap(self):
        self.assertFalse(point_membership([.1,.1,-1e-14],tetra())['strictlyInside'])

    def test_nonfinite_rejects(self):
        with self.assertRaises(AssertionError):point_membership([float('nan'),0,0],tetra())


if __name__=='__main__':unittest.main()
