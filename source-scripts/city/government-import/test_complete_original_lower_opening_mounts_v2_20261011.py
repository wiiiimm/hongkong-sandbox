"""Counterexamples for topology/min-height/whole-host-coverage and byte bindings."""
import unittest
import numpy as np
from complete_original_lower_opening_mounts_v2_20261011 import binding,verify

def box(bottom=.01,top=1.,open_top=False,dx=0):
 p=np.asarray([[dx, bottom,0],[dx+1,bottom,0],[dx+1,bottom,1],[dx,bottom,1],[dx,top,0],[dx+1,top,0],[dx+1,top,1],[dx,top,1]],float)
 quads=[[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7],([0,3,2,1]if open_top else[4,5,6,7])]
 return np.asarray([p[list(ix)]for a,b,c,d in quads for ix in [(a,b,c),(a,c,d)]])
def roof(y=0,xhi=1):return np.asarray([[[0,y,0],[xhi,y,1],[xhi,y,0]],[[0,y,0],[0,y,1],[xhi,y,1]]],float)
class MountTests(unittest.TestCase):
 def check(self,b,h):
  t=np.concatenate([b,h]);body=list(range(len(b)));host=list(range(len(b),len(t)));return verify(t,body,host,expected_binding=binding(t,body,host))
 def test_complete_bottom_open_box_associates_without_solid_or_root_credit(self):
  r=self.check(box(),roof());self.assertTrue(r['completeLowerOpeningAssociated']);self.assertFalse(r['closedSolidCertified']);self.assertFalse(r['structuralRootCredit']);self.assertFalse(r['structuralBridgeCredit'])
 def test_two_disconnected_opening_cycles_rejected(self):
  with self.assertRaises(AssertionError):self.check(np.concatenate([box(),box(dx=2)]),roof(xhi=3))
 def test_nonmanifold_incidence_rejected(self):
  b=box()
  with self.assertRaises(AssertionError):self.check(np.concatenate([b,b[:1]]),roof())
 def test_higher_opening_rejected_even_with_nearby_host(self):
  with self.assertRaisesRegex(AssertionError,'lowest boundary'):self.check(box(open_top=True),roof(y=1))
 def test_partial_host_coverage_rejected(self):self.assertFalse(self.check(box(),roof(xhi=.5))['completeLowerOpeningAssociated'])
 def test_point_only_host_corner_rejected(self):
  h=np.asarray([[[-1,0,-1],[0,0,0],[-1,0,0]]],float);self.assertFalse(self.check(box(),h)['completeLowerOpeningAssociated'])
 def test_outside_existing_band_rejected(self):self.assertFalse(self.check(box(bottom=.11),roof())['completeLowerOpeningAssociated'])
 def test_changed_host_bytes_rejected(self):
  t=np.concatenate([box(),roof()]);body=list(range(10));host=[10,11];pin=binding(t,body,host);t[10,0,1]=.01
  with self.assertRaisesRegex(AssertionError,'binding'):verify(t,body,host,expected_binding=pin)
 def test_wrong_host_scope_rejected(self):
  t=np.concatenate([box(),roof()]);pin=binding(t,list(range(10)),[10,11])
  with self.assertRaisesRegex(AssertionError,'binding'):verify(t,list(range(10)),[10],expected_binding=pin)
if __name__=='__main__':unittest.main()
