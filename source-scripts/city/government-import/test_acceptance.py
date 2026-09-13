import importlib.util
from pathlib import Path
import unittest
spec=importlib.util.spec_from_file_location('policy',Path(__file__).with_name('acceptance-policy.py'));policy=importlib.util.module_from_spec(spec);spec.loader.exec_module(policy)
class AcceptanceTests(unittest.TestCase):
 def setUp(self):
  self.row={'state':'runtime-validated-awaiting-acceptance','sourceSHA256':'a'}
  self.m={'sourcePreserved':True,'sourceSHA256':'a','minSurfaceGap':-.2,'minLowGap':-.2,'maxLowGap':.2,'maxSamplerDelta':0,'missingTerrain':0,'lowRimChecks':10,'identity':{'overlap':1,'centroidDistance':0},'budget':{'triangles':10,'geometryBytes':100,'residentBytes':1000}}
  self.profile={'triangles':20,'geometryBytes':200,'residentBytes':2000}
 def test_grounded_original_passes_without_architectural_ai(self):self.assertEqual(policy.reasons(self.row,self.m,self.profile),[])
 def test_prior_hold_never_promoted(self):
  self.row['state']='retained-pending-placement';self.assertIn('prior-validation-held',policy.reasons(self.row,self.m,self.profile))
 def test_burial_gap_and_mismatched_drawn_ground_are_held(self):
  for key,value,reason in [('minSurfaceGap',-.51,'terrain-intersects-source-over-0.5m'),('minLowGap',.11,'ground-contact-unresolved'),('maxLowGap',1.01,'ground-contact-unresolved'),('maxSamplerDelta',.005,'sampler-rendered-terrain-disagreement')]:
   m={**self.m,key:value};self.assertIn(reason,policy.reasons(self.row,m,self.profile))
 def test_missing_changed_and_invalid_evidence_never_passes(self):
  for changes in [{'sourceSHA256':'different'},{'minSurfaceGap':float('nan')},{'missingTerrain':1},{'lowRimChecks':0},{'error':'load failed'}]:self.assertTrue(policy.reasons(self.row,{**self.m,**changes},self.profile))
 def test_identity_and_runtime_limits(self):
  self.m['identity']['overlap']=.97;self.m['budget']['triangles']=21
  self.assertEqual(set(policy.reasons(self.row,self.m,self.profile)),{'strict-identity-fit','mobile-runtime-budget'})
if __name__=='__main__':unittest.main()
