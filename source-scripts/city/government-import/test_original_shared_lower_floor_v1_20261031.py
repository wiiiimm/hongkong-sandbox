import unittest
import numpy as np
from fractions import Fraction
from original_shared_lower_floor_v1_20261031 import floor_context
class FloorTests(unittest.TestCase):
    def setUp(self):self.t=np.array([[0,0,0],[0,0,2],[2,0,0]],float)
    def test_exact_original_surface(self):
        p=floor_context(self.t,[self.t]);self.assertTrue(p['completeLowerPeerCorrespondence']);self.assertTrue(p['exactlyCoincident']);self.assertFalse(p['groundRootCredit']);self.assertFalse(p['strictFoundationAccepted'])
    def test_split_original_plane(self):
        a=np.array([[0,0,0],[0,0,2],[1,0,1]],float);b=np.array([[0,0,0],[1,0,1],[2,0,0]],float);self.assertTrue(floor_context(self.t,[a,b])['completeLowerPeerCorrespondence'])
    def test_subnanometre_hole_is_not_rounded_away(self):
        peer=self.t.copy();peer[:,[0,2]]*=1-2**-40;p=floor_context(self.t,[peer]);self.assertFalse(p['completeLowerPeerCorrespondence']);self.assertGreater(Fraction(p['uncoveredProjectedAreaExact']),0)
    def test_existing_minimum_boundary_and_next_float(self):
        peer=self.t.copy();peer[:,1]=.1;self.assertTrue(floor_context(self.t,[peer])['withinExistingStrictNativeInterfaceInterval']);peer[:,1]=np.nextafter(.1,np.inf);self.assertFalse(floor_context(self.t,[peer])['withinExistingStrictNativeInterfaceInterval'])
    def test_existing_maximum_boundary_and_next_float(self):
        source=self.t.copy();source[:,1]=1;self.assertTrue(floor_context(source,[self.t])['withinExistingStrictNativeInterfaceInterval']);source[:,1]=np.nextafter(1.,np.inf);self.assertFalse(floor_context(source,[self.t])['withinExistingStrictNativeInterfaceInterval'])
    def test_missing_peer_is_a_measured_negative_result(self):
        p=floor_context(self.t,[]);self.assertFalse(p['completeLowerPeerCorrespondence']);self.assertIn('no-positive-area-original-peer-floor-nomination',p['reasons'])
    def test_wall_not_called_floor(self):
        with self.assertRaises(AssertionError):floor_context([[0,0,0],[0,1,0],[1,0,0]],[self.t])
if __name__=='__main__':unittest.main()
