"""Retain nine earlier adversarial cases, reject closed hitchhikers/zero hosts."""
import unittest
import numpy as np
from complete_original_lower_opening_mounts_v3_20261011 import binding,verify
import test_complete_original_lower_opening_mounts_v2_20261011 as previous
box=previous.box
roof=previous.roof
class MountV3Tests(previous.MountTests):
 def check(self,b,h):
  t=np.concatenate([b,h]);body=list(range(len(b)));host=list(range(len(b),len(t)));return verify(t,body,host,expected_binding=binding(t,body,host))
 def test_changed_host_bytes_rejected(self):
  t=np.concatenate([box(),roof()]);body=list(range(10));host=[10,11];pin=binding(t,body,host);t[10,0,1]=.01
  with self.assertRaisesRegex(AssertionError,'binding'):verify(t,body,host,expected_binding=pin)
 def test_wrong_host_scope_rejected(self):
  t=np.concatenate([box(),roof()]);pin=binding(t,list(range(10)),[10,11])
  with self.assertRaisesRegex(AssertionError,'binding'):verify(t,list(range(10)),[10],expected_binding=pin)
 def test_closed_disconnected_tetrahedron_cannot_hitchhike(self):
  v=np.asarray([[2,2,2],[3,2,2],[2,3,2],[2,2,3]],float);tetra=v[np.asarray([[0,2,1],[0,1,3],[1,2,3],[2,0,3]])]
  with self.assertRaisesRegex(AssertionError,'one genuine'):self.check(np.concatenate([box(),tetra]),roof())
 def test_degenerate_host_cannot_receive_band_credit(self):
  degenerate=np.asarray([[[.5,0,.5],[.5,0,.5],[.5,0,.5]]])
  with self.assertRaisesRegex(AssertionError,'Degenerate original host'):self.check(box(),np.concatenate([roof(),degenerate]))
if __name__=='__main__':unittest.main()
