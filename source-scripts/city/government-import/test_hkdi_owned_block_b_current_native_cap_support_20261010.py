"""Actual complete HKDI B/carrier fixture plus meaningful invalid support cases."""
import copy,unittest
from run import ROOT,read
from hkdi_owned_block_b_current_native_cap_support_20261010 import verify,canonical
BASE=ROOT/'docs/astra-city/government-import'
class ActualNativeCarrierTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.proof=read(BASE/'government-xl-terrain-recovery-hkdi-block-b-current-exposed-native-cap-paths-v2-20261010/diagnostic.json.gz')
  cls.parts=read(BASE/'xl-terrain-recovery-20261010-hkdi-native-and-block-b-complete-original-support-v1/diagnostic.json.gz')['components']
  cls.roots=read(BASE/'government-xl-terrain-recovery-hkdi-current-native-literal-ground-roots-v3-20261010/diagnostic.json.gz')
 def bound(self,p,c,r):return dict(qualifiedCapProofSHA256=canonical(p),completeOriginalComponentsSHA256=canonical(c),actualFourRootProofSHA256=canonical(r))
 def call(self,p=None,c=None,r=None,expected=None):
  p=self.proof if p is None else p;c=self.parts if c is None else c;r=self.roots if r is None else r;b=self.bound(p,c,r)
  return verify(p,c,r,expected_binding=b if expected is None else expected,current_binding=b)
 def reject(self,mutate):
  p,c,r=copy.deepcopy((self.proof,self.parts,self.roots));mutate(p,c,r)
  with self.assertRaises(AssertionError):self.call(p,c,r)
 def test_actual_complete_345_parts_pass(self):self.assertTrue(self.call()['allOwnedComponentsSupported'])
 def test_buried_source_cap_rejects(self):self.reject(lambda p,c,r:p['completeCarrierCapsSourceContexts'][0].update(exactCertifiedLowerClearanceM='-1/1000'))
 def test_buried_literal_cap_rejects(self):self.reject(lambda p,c,r:p['completeCarrierCapsActualContexts'][0].update(exactCertifiedLowerClearanceM='0'))
 def test_missing_finite_ground_rejects(self):self.reject(lambda p,c,r:p['completeCarrierCapsActualContexts'][0].update(groundProjectionCovered=False))
 def test_missing_owned_component_rejects(self):self.reject(lambda p,c,r:c[157].update(actorUID='landsd/88343:0'))
 def test_uninstalled_A_bridge_rejects(self):self.reject(lambda p,c,r:p['completeQualifiedOwnedBPaths'][2].update(parent=100))
 def test_native_ramp_bridge_rejects(self):self.reject(lambda p,c,r:p['completeQualifiedOwnedBPaths'][2].update(parent=128))
 def test_failed_147_footing_bridge_rejects(self):self.reject(lambda p,c,r:p['completeQualifiedOwnedBPaths'][0].update(parent=147))
 def test_point_only_literal_contact_rejects(self):self.reject(lambda p,c,r:p['completeQualifiedOwnedBPaths'][0].update(literalIntersectionVertices=[['0','0','0']]))
 def test_point_only_source_contact_rejects(self):self.reject(lambda p,c,r:p['completeQualifiedOwnedBPaths'][0].update(sourceIntersectionVertices=[['0','0','0']]))
 def test_wrong_original_face_membership_rejects(self):self.reject(lambda p,c,r:p['completeQualifiedOwnedBPaths'][0].update(globalOriginalFaces=[999999,999998]))
 def test_omitted_legacy_warning_rejects(self):self.reject(lambda p,c,r:p['completeRaw61AffectedNativeFaceInventory'].pop())
 def test_native_reacceptance_rejects(self):self.reject(lambda p,c,r:p.update(nativeReacceptance=True))
 def test_missing_independent_actual_root_rejects(self):self.reject(lambda p,c,r:r.update(strictLiteralRenderedRoots=False))
 def test_context_tamper_stale_binding_rejects(self):
  p=copy.deepcopy(self.proof);p['completeCarrierCapsSourceContexts'][0]['minimum']['minimumGapM']+=1
  with self.assertRaises(AssertionError):self.call(p,expected=self.bound(self.proof,self.parts,self.roots))
 def test_component_tamper_stale_binding_rejects(self):
  c=copy.deepcopy(self.parts);c[144]['bounds'][0][1]+=1
  with self.assertRaises(AssertionError):self.call(c=c,expected=self.bound(self.proof,self.parts,self.roots))
if __name__=='__main__':unittest.main()
