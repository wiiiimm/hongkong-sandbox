from copy import deepcopy
import unittest
from run import ROOT,read
from lippo_two_positive_identity_collection_binding_20261011 import verify
class ExactActualCollection(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.stored=read(ROOT/'docs/astra-city/government-import/government-xl-lippo-two-original-disjoint-current-parent-physical-v2-20261011/owned-source-identity.json');cls.policy=cls.stored['rows'][0]['policy']
 def test_actual_both_complete_proofs(self):
  for p in self.stored['rows']:self.assertEqual(verify(p,self.stored,p['uid'],self.policy),p)
 def fail(self,stored,replay=None,uid=None):
  p=self.stored['rows'][0] if replay is None else replay
  with self.assertRaises((AssertionError,KeyError)):verify(p,stored,p['uid'] if uid is None else uid,self.policy)
 def test_old_scalar_vs_pair_is_not_accepted(self):self.fail(self.stored['rows'][0])
 def test_missing_tower(self):self.fail({'rows':self.stored['rows'][:1]})
 def test_duplicate_podium(self):self.fail({'rows':[self.stored['rows'][0]]*2})
 def test_unknown_actor(self):
  s=deepcopy(self.stored);s['rows'][1]['uid']='landsd/233997:0';self.fail(s)
 def test_changed_source_hash(self):
  p=deepcopy(self.stored['rows'][0]);p['sourceSHA256']='0'*64;self.fail(self.stored,p)
 def test_changed_whole_world(self):
  p=deepcopy(self.stored['rows'][0]);p['worldTrianglesSHA256']='0'*64;self.fail(self.stored,p)
 def test_unknown_reason(self):
  s=deepcopy(self.stored);s['rows'][1]['reasons']=['new-unresolved-foreign'];self.fail(s)
 def test_changed_policy(self):
  s=deepcopy(self.stored);s['rows'][1]['policy']='waived';self.fail(s)
 def test_wrong_actor_binding(self):self.fail(self.stored,self.stored['rows'][1],self.stored['rows'][0]['uid'])
if __name__=='__main__':unittest.main()
