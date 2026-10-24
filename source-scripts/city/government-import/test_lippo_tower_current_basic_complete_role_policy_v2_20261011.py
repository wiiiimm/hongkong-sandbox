"""Current captured actual-report counterexamples; no mocked acceptance replay."""
import unittest,copy
from run import ROOT,read
from lippo_tower_current_basic_complete_role_policy_v2_20261011 import validate_semantics,staged_entry,DEPENDENCY
B=ROOT/'docs/astra-city/government-import'
class CurrentRolePolicyTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.identity=read(B/'government-xl-lippo-tower-current-complete-original-identity-diagnostic-v5-20261011/identity.json')
  cls.physical=read(B/'government-xl-lippo-tower-only-unchanged-current-ordinary-physical-v3-20261011/diagnostic.json.gz')
  cls.sep=read(B/'government-xl-lippo-tower-all-current-native-actual-position-separation-v2-20261011/diagnostic.json.gz')
  cls.role=read(B/'government-xl-lippo-mainbody-current-basic-join-source-proposal-v1-20261011/diagnostic.json.gz')
  cls.entry=read(B/'government-xl-lippo-tower-only-current-complete-inputs-v5-20261011/input.json.gz')['rows'][0]['candidate']['entry']
 def args(self):return [copy.deepcopy(v) for v in [self.identity,self.physical,self.sep,self.role,self.physical['currentManifest']]]
 def reject(self,fn):
  a=self.args();fn(a)
  with self.assertRaises((AssertionError,KeyError,ValueError,TypeError)):validate_semantics(*a)
 def test_actual_current_gates_ready_stage_only(self):r=validate_semantics(*self.args());self.assertTrue(r['scriptChecksPassed']);self.assertFalse(r['installationApproved']);self.assertEqual(r['currentBasicCarrierDependency'],DEPENDENCY)
 def test_unknown_numeric_reason(self):self.reject(lambda a:a[1]['ordinaryNumericReasons'].append('unrelated-collision'))
 def test_missing_raw_numeric_reason(self):self.reject(lambda a:a[1].update(ordinaryNumericReasons=[]))
 def test_unknown_runtime_concern(self):self.reject(lambda a:a[1]['rawRuntimeConcerns'][0]['concerns'].append('terrain-burial'))
 def test_foundation_failure(self):self.reject(lambda a:a[1].update(strictFoundationAccepted=False))
 def test_runtime_exception(self):self.reject(lambda a:a[1].update(runtimeExceptions=1))
 def test_loader_failure(self):self.reject(lambda a:a[1].update(loaderAccepted=0))
 def test_neighbour_regression(self):self.reject(lambda a:a[1]['neighbourRegressionReasons'].append({'uid':'other','reasons':['burial']}))
 def test_native_blocked(self):self.reject(lambda a:a[1]['rawNativeNeighbourChecks']['blocked'].append('other'))
 def test_identity_failure(self):self.reject(lambda a:a[0].update(passed=False))
 def test_unknown_identity_reason(self):self.reject(lambda a:a[0]['reasons'].append('extent'))
 def test_stale_current_physical_manifest(self):self.reject(lambda a:a[1]['currentManifest'].update(sha256='0'*64))
 def test_stale_current_global_native_manifest(self):self.reject(lambda a:a[2]['currentManifest'].update(sha256='0'*64))
 def test_missing_global_native_actor(self):self.reject(lambda a:a[2]['completeNativeActualBoundsCertificate']['rows'].pop())
 def test_false_unused_position_separation(self):self.reject(lambda a:a[2]['completeNativeActualBoundsCertificate'].update(allFourOwnedByThreeActualNativeWorldBoundsStrictlyDisjoint=False))
 def test_whole_basic_reapproval(self):self.reject(lambda a:a[3].update(wholeBasicReaccepted=True))
 def test_absent_GOV_podium_support(self):self.reject(lambda a:a[3].update(governmentPodiumUsedAsRuntimeSupport=True))
 def test_source_edit(self):self.reject(lambda a:a[3].update(sourceGeometryChanges=1))
 def test_terrain_edit(self):self.reject(lambda a:a[1].update(terrainGeometryChanges=1))
 def test_threshold_change(self):self.reject(lambda a:a[3].update(thresholdChanges=1))
 def test_stage_metadata_preserves_original_geometry_and_root(self):
  e=staged_entry(self.entry);self.assertEqual(e['supportDependencies'],[DEPENDENCY]);self.assertEqual(e['sha256'],self.entry['sha256']);self.assertEqual(e['worldBounds'],self.entry['worldBounds']);self.assertEqual(e['rootTranslation'],self.entry['rootTranslation']);self.assertFalse(e['proceduralWindows'])
 def test_wrong_stage_source(self):
  e=copy.deepcopy(self.entry);e['sha256']='0'*64
  with self.assertRaises(AssertionError):staged_entry(e)
 def test_conflicting_dependency_rejected(self):
  e=copy.deepcopy(self.entry);e['supportDependencies']=[{'uid':'other'}]
  with self.assertRaises(AssertionError):staged_entry(e)
if __name__=='__main__':unittest.main()
