import unittest
import numpy as np
from original_wall_skin_escape_v1_20261031 import wall_escape

class EscapeTests(unittest.TestCase):
    def setUp(self):
        self.tri=np.array([[[0,0,0],[0,1,0],[1,0,0]],[[0,1,0],[1,1,0],[1,0,0]],[[4,0,0],[4,1,0],[5,0,0]]],float)
    def test_clear_wall_does_not_need_horizontal_cap(self):
        p=wall_escape(self.tri,[0,1],[0],[0]);self.assertTrue(p['allTargetsReachClearOriginalWalls']);self.assertEqual(p['paths'][0]['originalWallPath'],[0,1]);self.assertFalse(p['groundRootCredit']);self.assertFalse(p['strictFoundationAccepted'])
    def test_wholly_negative_skin_gets_no_escape(self):
        self.assertFalse(wall_escape(self.tri,[0,1],[0,1],[0])['allTargetsReachClearOriginalWalls'])
    def test_disconnected_clear_wall_cannot_qualify(self):
        self.assertFalse(wall_escape(self.tri,[0,2],[0],[0])['allTargetsReachClearOriginalWalls'])
    def test_point_only_contact_cannot_bridge(self):
        self.tri[1]=[[0,1,0],[2,1,0],[2,2,0]]
        self.assertFalse(wall_escape(self.tri,[0,1],[0],[0])['allTargetsReachClearOriginalWalls'])
    def test_horizontal_face_cannot_be_called_wall(self):
        self.tri[1]=[[0,1,0],[1,1,0],[0,1,1]]
        with self.assertRaises(AssertionError):wall_escape(self.tri,[0,1],[0],[0])
    def test_nonnegative_target_is_rejected(self):
        with self.assertRaises(AssertionError):wall_escape(self.tri,[0,1],[0],[1])
if __name__=='__main__':unittest.main()
