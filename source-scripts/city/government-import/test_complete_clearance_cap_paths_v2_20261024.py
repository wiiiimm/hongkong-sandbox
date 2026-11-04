import unittest
from complete_clearance_cap_paths_v2_20261024 import verify

WALL=[[0,-1,0],[1,1,0],[0,1,0]]
CAP=[[0,1,0],[1,1,0],[0,1,-1]]


class CompleteCapPaths(unittest.TestCase):
    def test_shared_complete_edge_reaches_clear_upward_cap(self):
        p=verify([WALL,CAP],[0]);self.assertTrue(p['allAffectedHavePaths']);self.assertEqual(p['paths'][0]['originalPath'],[0,1])
    def test_point_contact_never_bridges(self):self.assertFalse(verify([WALL,[[0,1,0],[-1,1,0],[0,1,1]]],[0])['allAffectedHavePaths'])
    def test_buried_nonwall_cannot_be_used_as_cap(self):
        p=verify([WALL,CAP],[0,1]);self.assertFalse(p['allAffectedHavePaths']);self.assertEqual(p['negativeNonWallFaces'],[1])
    def test_nonzero_authored_gap_is_not_welded(self):
        cap=[[x+.000001,y,z]for x,y,z in CAP];self.assertFalse(verify([WALL,cap],[0])['allAffectedHavePaths'])
    def test_collapsed_facet_cannot_become_a_bridge(self):
        p=verify([WALL,[[0,1,0],[0,1,0],[0,1,0]]],[0]);self.assertFalse(p['allAffectedHavePaths']);self.assertEqual(p['nonrenderingSourceFaces'],[1])
    def test_exact_partial_top_edge_resolves_without_welding(self):
        cap=[[.25,1,0],[.75,1,0],[.25,1,-1]];self.assertFalse(verify([WALL,cap],[0])['allAffectedHavePaths']);self.assertTrue(verify([WALL,cap],[0],[(0,1)])['allAffectedHavePaths'])
    def test_forged_detached_contact_rejected(self):
        cap=[[x+5,y,z]for x,y,z in CAP]
        with self.assertRaises((AssertionError,ValueError)):verify([WALL,cap],[0],[(0,1)])
    def test_point_only_additional_contact_rejected(self):
        with self.assertRaises(AssertionError):verify([WALL,[[0,1,0],[-1,1,0],[0,1,1]]],[0],[(0,1)])
    def test_missing_or_duplicate_negative_face_indices_rejected(self):
        for ids in [[0,0],[2],[-1]]:
            with self.subTest(ids=ids),self.assertRaises(AssertionError):verify([WALL,CAP],ids)

if __name__=='__main__':unittest.main()
