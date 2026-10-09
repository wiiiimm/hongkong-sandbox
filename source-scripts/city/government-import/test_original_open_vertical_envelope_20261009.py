import unittest
import numpy as np
from original_open_vertical_envelope_20261009 import diagnose


def wall(ring=((0,0),(2,0),(2,1),(0,1))):
    faces=[]
    for a,b in zip(ring,ring[1:]+ring[:1]):
        lowa=(a[0],0,a[1]);lowa2=(b[0],0,b[1]);hi=(b[0],3,b[1]);hia=(a[0],3,a[1])
        faces.extend([[lowa,lowa2,hi],[lowa,hi,hia]])
    return np.asarray(faces,float)


class EnvelopeTests(unittest.TestCase):
    def check(self,t):return diagnose(t,list(range(len(t))))
    def test_original_open_ring_is_diagnostic_only(self):
        result=self.check(wall());self.assertEqual(result['enclosedPlanAreaM2'],2)
        self.assertEqual(result['originalTopAndBottomOpenEdges'],8)
        self.assertFalse(result['closedSolidCertified']);self.assertFalse(result['installationApproved'])
    def test_concave_ring_is_preserved(self):
        self.assertEqual(self.check(wall(((0,0),(3,0),(3,1),(1,1),(1,3),(0,3))))['enclosedPlanAreaM2'],5)
    def test_missing_face(self):
        with self.assertRaises(AssertionError):self.check(wall()[:-1])
    def test_duplicate_face(self):
        with self.assertRaises(AssertionError):self.check(np.concatenate([wall(),wall()[:1]]))
    def test_wrong_winding(self):
        t=wall();t[0]=t[0][::-1]
        with self.assertRaises(AssertionError):self.check(t)
    def test_tiny_original_warp_is_not_welded(self):
        t=wall();t[0,0,0]=np.nextafter(0.,1.)
        with self.assertRaises(AssertionError):self.check(t)
    def test_self_crossing_ring(self):
        with self.assertRaises(AssertionError):self.check(wall(((0,0),(3,2),(0,2),(2,0))))
    def test_disconnected_rings(self):
        with self.assertRaises(AssertionError):self.check(np.concatenate([wall(),wall(((10,0),(12,0),(12,1),(10,1)))]))
    def test_original_cap_is_not_ignored(self):
        cap=np.array([[[0,3,0],[2,3,0],[2,3,1]]],float)
        with self.assertRaises(AssertionError):self.check(np.concatenate([wall(),cap]))
    def test_slanted_or_nonuniform_height(self):
        t=wall();t[0,2,1]+=1e-10
        with self.assertRaises(AssertionError):self.check(t)
    def test_duplicate_source_ids(self):
        with self.assertRaises(AssertionError):diagnose(wall(),[0,0])
    def test_degenerate_face(self):
        t=wall();t[0,2]=t[0,0]
        with self.assertRaises(AssertionError):self.check(t)


if __name__=='__main__':unittest.main()
