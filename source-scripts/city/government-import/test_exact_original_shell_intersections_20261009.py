import unittest
from exact_original_shell_intersections_20261009 import shell_self_intersections


class ExactShellIntersectionTests(unittest.TestCase):
    def test_closed_tetrahedron_legal_contacts(self):
        v=[[0,0,0],[1,0,0],[0,1,0],[0,0,1]]
        faces=[[v[i] for i in f] for f in [[0,2,1],[0,1,3],[0,3,2],[1,2,3]]]
        r=shell_self_intersections(faces)
        self.assertTrue(r['selfIntersectionFree']);self.assertEqual(r['trianglePairsChecked'],6)

    def test_crossing_interiors_rejected(self):
        r=shell_self_intersections([[[0,0,0],[2,0,0],[0,2,0]],
                                  [[.5,.5,-1],[.5,.5,1],[1.5,.5,0]]])
        self.assertFalse(r['selfIntersectionFree'])

    def test_duplicate_coplanar_face_rejected(self):
        t=[[0,0,0],[1,0,0],[0,1,0]]
        self.assertFalse(shell_self_intersections([t,t])['selfIntersectionFree'])

    def test_coplanar_shared_edge_legal(self):
        a=[[0,0,0],[1,0,0],[0,1,0]];b=[[1,0,0],[0,1,0],[1,1,0]]
        self.assertTrue(shell_self_intersections([a,b])['selfIntersectionFree'])

    def test_coplanar_overlap_beyond_shared_vertex_rejected(self):
        a=[[0,0,0],[2,0,0],[0,2,0]];b=[[0,0,0],[1,0,0],[0,1,0]]
        self.assertFalse(shell_self_intersections([a,b])['selfIntersectionFree'])

    def test_small_real_gap_not_merged(self):
        a=[[0,0,0],[1,0,0],[0,1,0]];b=[[0,0,1e-12],[1,0,1e-12],[0,1,1e-12]]
        self.assertTrue(shell_self_intersections([a,b])['selfIntersectionFree'])

    def test_small_real_intersection_rejected(self):
        a=[[0,0,0],[1,0,0],[0,1,0]];b=[[.25,.25,-1e-12],[.25,.25,1e-12],[.5,.25,0]]
        self.assertFalse(shell_self_intersections([a,b])['selfIntersectionFree'])

    def test_shared_vertex_only_legal(self):
        a=[[0,0,0],[1,0,0],[0,1,0]];b=[[0,0,0],[-1,0,1],[0,-1,1]]
        self.assertTrue(shell_self_intersections([a,b])['selfIntersectionFree'])

    def test_noncoplanar_touch_along_unshared_edge_rejected(self):
        a=[[0,0,0],[1,0,0],[0,1,0]]
        b=[[.25,.25,0],[.5,.25,0],[.25,.25,1]]
        self.assertFalse(shell_self_intersections([a,b])['selfIntersectionFree'])

    def test_degenerate_source_rejected(self):
        with self.assertRaises(AssertionError):
            shell_self_intersections([[[0,0,0],[1,0,0],[2,0,0]],[[0,0,1],[1,0,1],[0,1,1]]])

    def test_single_degenerate_source_rejected(self):
        with self.assertRaises(AssertionError):
            shell_self_intersections([[[0,0,0],[1,0,0],[2,0,0]]])

if __name__=='__main__':unittest.main()
