import unittest,numpy as np
import test_one_peking_two_closed_low_grade_feature_proposal_20261011 as fixtures
from one_peking_open_low_grade_feature_proposal_20261011 import verify,IDS
from run import digest
class CompleteOpenFeature(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  fixtures.CompleteActualFeatures.setUpClass();cls.src=fixtures.CompleteActualFeatures
 def check(self,**kw):
  s=self.src;args=dict(whole=s.original,ground=s.g,uid='landsd/233985:0',component=12,expected_world_sha=s.wsha,expected_ground_sha=s.gsha,complete_face_ids=IDS);args.update(kw);return verify(**args)
 def fail(self,**kw):
  with self.assertRaises(AssertionError):self.check(**kw)
 def test_actual_original_open_feature(self):
  q=self.check();self.assertTrue(q['openSurfaceExplicit']);self.assertEqual(len(q['completePositiveDimensionalWallGradeInterfaces']),21)
 def test_independent_actual_literal_open_feature(self):
  q=self.check(whole=self.src.literal,expected_world_sha=digest(self.src.literal.tobytes()));self.assertTrue(q['sourceRoleProposalSupported'])
 def test_no_solid_or_function_or_current_acceptance(self):
  q=self.check()
  for k in ['closedSolidCertification','structuralFunctionClaim','loadBearingClaim','sourceGroundRootAccepted','physicalAccepted','installationApproved']:self.assertFalse(q[k])
 def test_missing_one_whole_source_face(self):self.fail(complete_face_ids=IDS[:-1])
 def test_closed_box_cannot_take_open_route(self):self.fail(component=13)
 def test_wrong_current_uid(self):self.fail(uid='landsd/240487:0')
 def test_source_y_mutation(self):
  a=self.src.original.copy();a[3723,0,1]+=.001;self.fail(whole=a)
 def test_nonfinite_ground(self):
  g=self.src.g.copy();g[0,0,1]=np.nan;self.fail(ground=g)
 def test_rebound_raised_ground_buries_clear_cap(self):
  g=self.src.g.copy();g[:,:,1]+=2;self.fail(ground=g,expected_ground_sha=digest(g.tobytes()))
 def test_rebound_lowered_ground_removes_grade(self):
  g=self.src.g.copy();g[:,:,1]-=10;self.fail(ground=g,expected_ground_sha=digest(g.tobytes()))
 def test_real_disconnected_source_edge_even_rebound(self):
  a=self.src.original.copy();a[3723,0,0]+=.01;self.fail(whole=a,expected_world_sha=digest(a.tobytes()))
 def test_collapsed_source_face_cannot_glue(self):
  a=self.src.original.copy();a[2418]=a[2418,0];self.fail(whole=a,expected_world_sha=digest(a.tobytes()))
if __name__=='__main__':unittest.main()
