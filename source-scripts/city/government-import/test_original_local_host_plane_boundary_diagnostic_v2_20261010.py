import unittest
import numpy as np
from original_local_host_plane_boundary_diagnostic_v2_20261010 import prepare_hosts,diagnose

def quad(a,b,c,d):return [[a,b,c],[a,c,d]]
def fixture(gap=0,opposite=False,partial=False,two=False):
 # Four sides of an original open tube, with both authored end loops retained.
 a=[gap,0,0];b=[gap,1,0];c=[gap,1,1];d=[gap,0,1]
 aa=[gap+.03,0,0];bb=[gap+.03,1,0];cc=[gap+.03,1,1];dd=[gap+.03,0,1]
 detail=quad(a,aa,bb,b)+quad(b,bb,cc,c)+quad(c,cc,dd,d)+quad(d,dd,aa,a)
 if not two:detail+=quad(aa,dd,cc,bb)
 end=.5 if partial else 2
 host=quad([0,-1,-1],[0,2,-1],[0,2,end],[0,-1,end])
 if opposite:host+=quad([40,-1,-1],[40,2,-1],[40,2,2],[40,-1,2])
 return np.asarray(detail+host,float),list(range(len(detail))),list(range(len(detail),len(detail+host)))

class Tests(unittest.TestCase):
 def check(self,**kwargs):
  t,ids,roots=fixture(**kwargs);return diagnose(prepare_hosts(t,roots),ids)
 def test_local_plane_is_not_opposite_upper_envelope(self):self.assertTrue(self.check(opposite=True)['sourceOnlyBoundaryBandPassed'])
 def test_complete_two_original_openings(self):
  r=self.check(two=True);self.assertTrue(r['sourceOnlyBoundaryBandPassed']);self.assertEqual(len(r['completeOriginalLoops']),2)
 def test_partial_host_rejects(self):self.assertFalse(self.check(partial=True)['sourceOnlyBoundaryBandPassed'])
 def test_real_gap_rejects(self):self.assertFalse(self.check(gap=.101)['sourceOnlyBoundaryBandPassed'])
 def test_exact_band_passes(self):self.assertTrue(self.check(gap=.1)['sourceOnlyBoundaryBandPassed'])
 def test_next_float_outside_band_rejects(self):self.assertFalse(self.check(gap=np.nextafter(.1,1))['sourceOnlyBoundaryBandPassed'])
 def test_reversed_single_face_rejects(self):
  t,ids,roots=fixture();t[0]=t[0][::-1];self.assertFalse(diagnose(prepare_hosts(t,roots),ids)['sourceOnlyBoundaryBandPassed'])
 def test_detached_plane_only_rejects(self):
  t,ids,roots=fixture();t[roots,:,0]+=40;self.assertFalse(diagnose(prepare_hosts(t,roots),ids)['sourceOnlyBoundaryBandPassed'])
 def test_no_root_or_role_credit(self):
  r=self.check();self.assertFalse(r['structuralRootCredit']);self.assertFalse(r['visualRoleAccepted']);self.assertFalse(r['installationApproved'])
 def test_original_diagonal_facade_is_enumerated(self):
  t,ids,roots=fixture();x=t[:,:,0].copy();z=t[:,:,2].copy();t[:,:,0]=x+z;t[:,:,2]=-x+z;self.assertTrue(diagnose(prepare_hosts(t,roots),ids)["sourceOnlyBoundaryBandPassed"])
 def test_diagonal_real_gap_still_rejects(self):
  t,ids,roots=fixture(gap=.101);x=t[:,:,0].copy();z=t[:,:,2].copy();t[:,:,0]=x+z;t[:,:,2]=-x+z;self.assertFalse(diagnose(prepare_hosts(t,roots),ids)["sourceOnlyBoundaryBandPassed"])
 def test_nonfinite_rejects(self):
  t,ids,roots=fixture();t[0,0,0]=float('nan')
  with self.assertRaises(AssertionError):prepare_hosts(t,roots)
if __name__=='__main__':unittest.main()
