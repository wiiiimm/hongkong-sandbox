import unittest
from exact_shell_context_accelerated_20261009 import shell_self_intersections
from exact_original_shell_intersections_20261009 import shell_self_intersections as exhaustive


class AcceleratedTests(unittest.TestCase):
    def test_shared_box_boundaries_not_excluded(self):
        faces=[[[0,0,0],[1,0,0],[0,1,0]],[[0,0,0],[0,1,0],[0,0,1]],
               [[0,0,0],[.5,.5,0],[.5,0,0]]]
        a,b=shell_self_intersections(faces),exhaustive(faces)
        self.assertEqual(a['invalidIntersections'],b['invalidIntersections'])
        self.assertEqual(a['legalSharedContacts'],b['legalSharedContacts'])
        self.assertGreater(a['exactIntersectionPairs'],0)

    def test_subpicometre_separation_is_not_contact(self):
        faces=[[[0,0,0],[1,0,0],[0,1,0]],[[0,0,1e-13],[1,0,1e-13],[0,1,1e-13]]]
        r=shell_self_intersections(faces)
        self.assertTrue(r['selfIntersectionFree']);self.assertEqual(r['exactIntersectionPairs'],0)
        self.assertEqual(r['disjointOriginalAABBExcludedPairs'],1)

    def test_crossing_and_duplicate_faces_preserved(self):
        faces=[[[0,0,0],[2,0,0],[0,2,0]],[[.5,.5,-1],[.5,.5,1],[1,.5,0]],
               [[0,0,0],[2,0,0],[0,2,0]]]
        self.assertEqual(shell_self_intersections(faces)['invalidIntersections'],exhaustive(faces)['invalidIntersections'])


if __name__=='__main__':unittest.main()
