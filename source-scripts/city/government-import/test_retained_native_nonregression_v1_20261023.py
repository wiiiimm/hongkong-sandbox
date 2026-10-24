"""Adversarial checks against accidental legacy approval transfer."""
import copy, unittest
from retained_native_nonregression_v1_20261023 import terrain_decision
class Guard(unittest.TestCase):
 def setUp(self):
  self.raw=dict(uid='tower',passed=False,terrain=dict(minimumGapBefore=7.,minimumGapAfter=7.,maximumBurialIncrease=0,newlyWhollyBuried=0,newlyUpwardWhollyBuried=0))
  self.ctx=dict(nativeUid='tower',supportUid='podium',rawNativeRegression=copy.deepcopy(self.raw),proposalTerrainNonRegressionProved=True,existingNativeReaccepted=False,rawSupportPolicyPassed=False,sourceGeometryChanges=0,rows=[dict(uid=u,sourceSHA256=u,exactRenderedTerrainMultisetUnchanged=True,completeIntersectingTerrainFaces=3,completeFourWorldBounds=[[[0,0,0],[1,1,1]]]*4)for u in ['tower','podium']])
  self.inst={u:dict(sha256=u)for u in ['tower','podium']}
 def test_retains_negative_and_does_not_mutate(self):
  before=copy.deepcopy(self.raw);r=terrain_decision(self.raw,self.ctx,self.inst);self.assertTrue(r['passed']);self.assertFalse(r['rawNativeRegression']['passed']);self.assertFalse(r['existingNativeReaccepted']);self.assertEqual(before,self.raw)
 def test_changed_support_source(self):
  self.inst['podium']['sha256']='changed'
  with self.assertRaises(AssertionError):terrain_decision(self.raw,self.ctx,self.inst)
 def test_changed_whole_terrain(self):
  self.ctx['rows'][0]['exactRenderedTerrainMultisetUnchanged']=False
  with self.assertRaises(AssertionError):terrain_decision(self.raw,self.ctx,self.inst)
 def test_missing_world(self):
  self.ctx['rows'][1]['completeFourWorldBounds']=self.ctx['rows'][1]['completeFourWorldBounds'][:3]
  with self.assertRaises(AssertionError):terrain_decision(self.raw,self.ctx,self.inst)
 def test_new_burial(self):
  self.raw['terrain']['newlyWhollyBuried']=1;self.ctx['rawNativeRegression']=copy.deepcopy(self.raw)
  with self.assertRaises(AssertionError):terrain_decision(self.raw,self.ctx,self.inst)
 def test_unbound_actor(self):
  self.raw['uid']='different'
  with self.assertRaises(AssertionError):terrain_decision(self.raw,self.ctx,self.inst)
 def test_reacceptance_flag(self):
  self.ctx['existingNativeReaccepted']=True
  with self.assertRaises(AssertionError):terrain_decision(self.raw,self.ctx,self.inst)
if __name__=='__main__':unittest.main()
