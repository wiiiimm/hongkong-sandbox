from copy import deepcopy
import unittest,numpy as np
from run import ROOT,HERE,read,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from one_peking_two_closed_low_grade_feature_proposal_20261011 import verify,SCOPE,cap_relation
class CompleteActualFeatures(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  b=ROOT/'docs/astra-city/government-import';p=b/'government-xl-one-peking-two-original-retained-hullett-child-current-physical-v5-20261010';rows=sorted(read(p/'selection.json.gz')['rows'],key=lambda r:r['uid'])
  cls.original=np.concatenate([decode_original_world_triangles((ROOT/r['candidate']['path']).read_bytes()) for r in rows]);rt={r['uid']:r for r in read(HERE/'local'/p.name/'runtime-geometry.json.gz')['rows']};cls.literal=np.concatenate([np.asarray(rt[r['uid']]['position'],dtype='<f8').reshape(-1,3)[np.asarray(rt[r['uid']]['index']).reshape(-1,3)] for r in rows]);cls.g=np.asarray(read(b/'government-xl-one-peking-original-ordinary-ground-graph-diagnostic-v2-20261010/complete-historical-ground-facets.json.gz')['triangles'],dtype='<f8');cls.wsha=digest(cls.original.tobytes());cls.gsha=digest(cls.g.tobytes())
 def check(self,**kw):
  args=dict(whole=self.original,component=13,ground=self.g,uid='landsd/233985:0',expected_world_sha=self.wsha,expected_ground_sha=self.gsha,complete_face_ids=SCOPE[13]['ids']);args.update(kw);return verify(**args)
 def fail(self,**kw):
  with self.assertRaises(AssertionError):self.check(**kw)
 def test_actual_both_original_complete_grade_features(self):
  for k in [13,15]:
   q=self.check(component=k,complete_face_ids=SCOPE[k]['ids']);self.assertTrue(q['sourceRoleProposalSupported']);self.assertFalse(q['sourceGroundRootAccepted']);self.assertFalse(q['closedSolidCertification']);self.assertEqual({c['sourceFaceA'] for c in q['completePositiveDimensionalSideGradeInterfaces']},set(SCOPE[k]['side']))
 def test_actual_both_literal_features_independent(self):
  for k in [13,15]:self.assertTrue(self.check(whole=self.literal,expected_world_sha=digest(self.literal.tobytes()),component=k,complete_face_ids=SCOPE[k]['ids'])['sourceRoleProposalSupported'])
 def test_no_current_or_function_or_support_credit(self):
  q=self.check()
  for key in ['structuralFunctionClaim','loadBearingClaim','physicalAccepted','installationApproved']:self.assertFalse(q[key])
 def test_wrong_actor(self):self.fail(uid='landsd/240487:0')
 def test_open_component12_has_no_closed_route(self):self.fail(component=12)
 def test_missing_side_inventory(self):self.fail(complete_face_ids=SCOPE[13]['ids'][:-1])
 def test_duplicate_face_inventory(self):self.fail(complete_face_ids=SCOPE[13]['ids']+[3759])
 def test_original_world_byte_mutation(self):
  a=self.original.copy();a[2427,0,1]+=.001;self.fail(whole=a)
 def test_nonfinite_original(self):
  a=self.original.copy();a[0,0,0]=np.nan;self.fail(whole=a)
 def test_nonfinite_ground(self):
  g=self.g.copy();g[0,0,0]=np.inf;self.fail(ground=g)
 def test_unknown_complete_ground_hash(self):self.fail(expected_ground_sha='0'*64)
 def test_changed_ground_bytes(self):
  g=self.g.copy();g[0,0,1]+=.01;self.fail(ground=g)
 def test_grade_above_exposed_caps_even_rebound(self):
  g=self.g.copy();g[:,:,1]+=10;self.fail(ground=g,expected_ground_sha=digest(g.tobytes()))
 def test_grade_below_bases_even_rebound(self):
  g=self.g.copy();g[:,:,1]-=10;self.fail(ground=g,expected_ground_sha=digest(g.tobytes()))
 def test_missing_actual_ground_coverage(self):self.fail(ground=self.g[:1],expected_ground_sha=digest(self.g[:1].tobytes()))
 def test_real_source_open_seam_even_rebound(self):
  a=self.original.copy();a[3759,0,0]+=.01;self.fail(whole=a,expected_world_sha=digest(a.tobytes()))
 def test_reversed_actual_cap_even_rebound(self):
  a=self.original.copy();a[2427]=a[2427,[0,2,1]];self.fail(whole=a,expected_world_sha=digest(a.tobytes()))
 def test_true_zero_area_face_no_closed_graph_bridge(self):
  a=self.original.copy();a[3759]=a[3759,0];self.fail(whole=a,expected_world_sha=digest(a.tobytes()))
if __name__=='__main__':unittest.main()
