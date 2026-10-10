import unittest
from copy import deepcopy
from original_literal_rebound_role_accounting_20261010 import account
class Cases(unittest.TestCase):
 def setUp(self):
  self.old='a'*64;self.current={'path':'3d-viewer/city/data/manifest.json','sha256':'b'*64};self.owned={'landsd/1:0':'c'*64};self.retained={'landsd/2:0':'d'*64}
  self.role=dict(currentTypedPhysicalAccepted=True,reasons=[],sourceGeometryChanges=0,publication=False,newlyInstalled=0,installationApproved=False,currentManifest={'path':self.current['path'],'sha256':self.old},uids=list(self.owned),sourceSHA256s=self.owned,completeOriginalFaces=10,completeOriginalComponents=2,contract='fixture',currentOwnedIdentity={'historical':True},rawPhysicalReasonsPreserved=['real-raw-warning'],qualifiedOwnedNativeSupport={'credit':'unchanged'})
  self.region=dict(verifiedDisjointGlobalManifestRebind=True,allFrozenNumericAndSourceInputHashesUnchanged=True,numericAcceptanceRecomputed=False,installationApproved=False,oldManifestSHA256=self.old,currentManifestSHA256=self.current['sha256'],completeFrozenRegionWorldXZBounds=[0,0,5,5],changedCompleteInventory=[dict(kind='native',id='remote',before=None,after=dict(id='remote',completeWorldXZBounds=[10,10,20,20]))])
  self.identities=[dict(uid='landsd/1:0',sourceSHA256='c'*64,passed=True,reasons=[],exactRouteManifestSHA256=self.current['sha256'])]
  self.scope=[dict(kind=k,uid=u,sourceSHA256=s,allOriginalVerticesAccounted=True,completeOriginalLiteralAndFloat32Bounds=[[[1,0,1],[4,5,4]]]*3)for k,d in [('owned',self.owned),('retained-native',self.retained)]for u,s in d.items()]
 def call(self):return account(self.role,self.region,self.identities,expected_owned=self.owned,expected_retained=self.retained,protected_scope=self.scope,old_manifest=self.old,current_manifest=self.current)
 def rejects(self,change):change();self.assertRaises(AssertionError,self.call)
 def test_positive_preserves_raw(self):
  before=deepcopy(self.role);r=self.call();self.assertEqual(r['rawPhysicalReasonsPreserved'],before['rawPhysicalReasonsPreserved']);self.assertEqual(r['qualifiedOwnedNativeSupport'],before['qualifiedOwnedNativeSupport']);self.assertFalse(r['newNumericalAcceptanceCredit']);self.assertFalse(r['currentNativeReacceptance']);self.assertEqual(self.role,before)
 def test_old_unaccepted(self):self.rejects(lambda:self.role.update(currentTypedPhysicalAccepted=False))
 def test_old_unresolved(self):self.rejects(lambda:self.role.update(reasons=['unrooted']))
 def test_changed_geometry(self):self.rejects(lambda:self.role.update(sourceGeometryChanges=1))
 def test_bad_source(self):self.rejects(lambda:self.role.update(sourceSHA256s={'landsd/1:0':'e'*64}))
 def test_stale_current_identity(self):self.rejects(lambda:self.identities[0].update(exactRouteManifestSHA256=self.old))
 def test_failed_identity(self):self.rejects(lambda:self.identities[0].update(passed=False))
 def test_omitted_identity(self):self.rejects(lambda:self.identities.clear())
 def test_missing_retained(self):self.rejects(lambda:self.scope.pop())
 def test_missing_literal_strip(self):self.rejects(lambda:self.scope[0].update(completeOriginalLiteralAndFloat32Bounds=self.scope[0]['completeOriginalLiteralAndFloat32Bounds'][:2]))
 def test_float32_outside(self):self.rejects(lambda:self.scope[0]['completeOriginalLiteralAndFloat32Bounds'][2][1].__setitem__(0,5.00001))
 def test_actor_touches(self):self.rejects(lambda:self.region['changedCompleteInventory'][0]['after'].update(completeWorldXZBounds=[5,1,7,2]))
 def test_regional_numeric_changed(self):self.rejects(lambda:self.region.update(allFrozenNumericAndSourceInputHashesUnchanged=False))
 def test_empty_changes(self):self.rejects(lambda:self.region.update(changedCompleteInventory=[]))
 def test_manifest_same(self):self.rejects(lambda:self.current.update(sha256=self.old))
if __name__=='__main__':unittest.main()
