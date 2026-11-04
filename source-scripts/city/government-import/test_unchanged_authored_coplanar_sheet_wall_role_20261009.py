import unittest,hashlib
from copy import deepcopy
import numpy as np
from test_unchanged_authored_crossing_wall_role_20261009 import packet
from unchanged_closed_column_role_v2_20261009 import canonical_sha
from unchanged_authored_coplanar_sheet_wall_role_20261009 import verify_wall_role
from original_coplanar_exterior_continuation_20261009 import diagnose

def sheet_packet():
 t=np.asarray([[[0,-2,0],[1,0,0],[0,0,0]],[[0,0,0],[1,0,0],[0,2,0]],[[1,0,0],[1,2,0],[0,2,0]],[[0,2,0],[1,2,0],[0,2,-1]]],float)
 p=packet(t);r=p[3]['expected_role'];r['exactCoplanarExteriorContinuationGroups']={'0':[0,1,2]};p[3]['current_binding']['reviewedOriginalWallRoleSHA256']=canonical_sha(r);p[3]['expected_binding']=deepcopy(p[3]['current_binding']);return p
def check(p):return verify_wall_role(*p[:3],**p[3])
class OriginalWallCounterexamples(unittest.TestCase):
 def test_crossing_wall_ordinary_route(self):self.assertTrue(check(packet())['verifiedWallRole'])
 def test_exact_original_sheet_crosses_ground(self):
  r=check(sheet_packet());self.assertTrue(r['verifiedWallRole']);self.assertEqual(r['creditedBelowFaceOriginalSheets'],[0]);self.assertEqual(r['originalOpenPaths']['faces'][0]['reasons'],['no-exposed-wall-witness']);self.assertFalse(r['installationApproved'])
 def test_unreviewed_sheet_rejects(self):
  p=sheet_packet();p[3]['expected_role'].pop('exactCoplanarExteriorContinuationGroups');p[3]['current_binding']['reviewedOriginalWallRoleSHA256']=canonical_sha(p[3]['expected_role']);p[3]['expected_binding']=deepcopy(p[3]['current_binding'])
  with self.assertRaisesRegex(AssertionError,'Unreviewed'):check(p)
 def test_changed_sheet_membership_rejects(self):
  p=sheet_packet();p[3]['expected_role']['exactCoplanarExteriorContinuationGroups']['0']=[0,1];p[3]['current_binding']['reviewedOriginalWallRoleSHA256']=canonical_sha(p[3]['expected_role']);p[3]['expected_binding']=deepcopy(p[3]['current_binding'])
  with self.assertRaisesRegex(AssertionError,'membership'):check(p)
 def test_parallel_tiny_offset_no_sheet_credit(self):
  t=sheet_packet()[0].copy();t[1:3,:,2]+=1e-10;p=packet(t)
  # No original coplanar path reaches the clear roof; do not invent a near-plane group.
  self.assertFalse(check(p)['verifiedWallRole'])
 def test_whole_sheet_buried_rejects(self):
  p=sheet_packet();p[2][1]['maximumObservedGapM']=-1;p[2][2]['maximumObservedGapM']=-1;p[3]['current_binding']['continuousFaceContextsSHA256']=canonical_sha(p[2]);p[3]['expected_binding']=deepcopy(p[3]['current_binding']);self.assertFalse(check(p)['verifiedWallRole'])
 def test_missing_ground_rejects(self):
  p=sheet_packet();p[2][0]['groundProjectionCovered']=False;p[3]['current_binding']['continuousFaceContextsSHA256']=canonical_sha(p[2]);p[3]['expected_binding']=deepcopy(p[3]['current_binding'])
  with self.assertRaisesRegex(AssertionError,'Missing whole-face'):check(p)
 def test_foreign_intersection_rejects(self):
  p=sheet_packet();q=packet(p[0],foreign=[[[.5,-1,-1],[.5,-1,1],[.5,1,0]]]);q[3]['expected_role']=p[3]['expected_role'];q[3]['current_binding']['reviewedOriginalWallRoleSHA256']=canonical_sha(q[3]['expected_role']);q[3]['expected_binding']=deepcopy(q[3]['current_binding']);self.assertFalse(check(q)['verifiedWallRole'])
 def test_changed_source_rejects(self):
  p=sheet_packet();p[3]['current_binding']['sourceSHA256']='changed'
  with self.assertRaises(AssertionError):check(p)
 def test_missing_actor_rejects(self):
  p=sheet_packet();p[3]['foreign_scope']['actors']=[]
  with self.assertRaisesRegex(AssertionError,'Omitted'):check(p)
if __name__=='__main__':unittest.main()
