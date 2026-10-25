"""Frozen D evidence, synthetic in-memory acceptance only; no DB or asset writes."""
import copy,unittest
from unittest.mock import patch
import finite_basic_native_independent_admission_v1_20261026 as admission
BASE=admission.BASE;UID='landsd/255541:0';NATIVE='landsd/255544:0'
CFG=admission.read(BASE/'government-xl-beverly-d-finite-independent-original-install-config-v1-20261026.json')
def local_receipt(folder):
 r=admission.read(folder/'result.json');return r,{q['path']:q['sha256']for q in r['evidenceRefs']}
def fixture():
 retained={r['nativeUid']:r['rawCurrentNativeEntry']for r in admission.read(BASE/CFG['nativeContext']/'summary.json')['rows']}
 reports=[];images=[]
 for width in [390,1280]:
  p=BASE/CFG['browser']/str(width)/'staged-browser.json';r=admission.read(p);reports.append(dict(path=str(p.relative_to(admission.ROOT)),sha256=admission.digest(p.read_bytes())))
  for v in r['retainedNativeOwnViews']:
   path=p.parent/v['file'];images.append(dict(uid=v['uid'],width=width,time=v['time'],path=str(path.relative_to(admission.ROOT)),sha256=admission.digest(path.read_bytes())))
 manifest=admission.ROOT/'3d-viewer/city/data/manifest.json'
 return dict(testOnlySyntheticAcceptance=True,sourceSpecificPhysicalInterpretationAccepted=True,completeNeighbourInterpretationAccepted=True,completeFourWorldCanonicalRetainedBasicSupport=False,completeFourWorldFiniteRetainedBasicSupport=True,sourceGeometryChanges=0,sourcePoseChanges=0,terrainEdits=False,sourceSHA256ByUid=CFG['sources'],retainedBasicSupportDependencies=admission.read(BASE/CFG['finiteEvidence']/'support-bindings.json'),retainedNativeEntries=retained,currentManifest=dict(path=str(manifest.relative_to(admission.ROOT)),sha256=admission.digest(manifest.read_bytes())),retainedImagesActuallyViewed=images,browserReports=reports,runtimeAvailabilityDependenciesByUid={})
class IndependentFiniteNative(unittest.TestCase):
 def run_profile(self,review=None,config=None,change=None):
  original=admission.read
  def read(path):
   data=original(path);return change(path,data)if change else data
  with patch.object(admission,'authenticate',side_effect=local_receipt),patch.object(admission,'read',side_effect=read):return admission.replay(config or copy.deepcopy(CFG),review or fixture())
 def test_real_frozen_independent_profile_passes(self):self.assertTrue(self.run_profile())
 def test_canonical_failure_cannot_be_relabelled(self):
  r=fixture();r['completeFourWorldCanonicalRetainedBasicSupport']=True
  with self.assertRaises(AssertionError):self.run_profile(r)
 def test_source_sha_cannot_change(self):
  r=fixture();r['sourceSHA256ByUid']={UID:'0'*64}
  with self.assertRaises(AssertionError):self.run_profile(r)
 def test_native_publication_hold_cannot_change(self):
  r=fixture();r['retainedNativeEntries'][NATIVE]['publicationApproved']=True
  with self.assertRaises(AssertionError):self.run_profile(r)
 def test_missing_retained_image_refused(self):
  r=fixture();r['retainedImagesActuallyViewed'].pop()
  with self.assertRaises(AssertionError):self.run_profile(r)
 def test_incomplete_native_geometry_refused(self):
  def change(path,data):
   if str(path).endswith('255541:0--255544:0--original.json.gz')and CFG['nativeContext']in str(path):data['sourceFacesOmitted']=1
   return data
  with self.assertRaises(AssertionError):self.run_profile(change=change)
 def test_positive_native_contact_refused(self):
  def change(path,data):
   if str(path).endswith(CFG['nativeContext']+'/summary.json'):data['rows'][0]['modes'][0]['finiteContactPairs']=1
   if str(path).endswith(CFG['nativeContext']+'/255541:0--255544:0--original.json.gz'):data['contacts']=[{}]
   return data
  with self.assertRaisesRegex(AssertionError,'zero native detail'):self.run_profile(change=change)
 def test_positive_basic_fallback_contact_refused(self):
  def change(path,data):
   if str(path).endswith(CFG['nativeFallbackContext']+'/summary.json'):next(m for m in data['rows'][0]['modes']if m['mode']=='original')['finiteContactPairs']=1
   if str(path).endswith(CFG['nativeFallbackContext']+'/255541:0--255544:0--original.json.gz'):data['contacts']=[{}]
   return data
  with self.assertRaisesRegex(AssertionError,'zero native BASIC'):self.run_profile(change=change)
 def test_missing_fallback_world_refused(self):
  def change(path,data):
   if str(path).endswith(CFG['nativeFallbackContext']+'/summary.json'):data['rows'][0]['modes'].pop()
   return data
  with self.assertRaises(AssertionError):self.run_profile(change=change)
 def test_invented_availability_edge_refused(self):
  r=fixture();r['runtimeAvailabilityDependenciesByUid']={UID:NATIVE}
  with self.assertRaises(AssertionError):self.run_profile(r)
 def test_scope_cannot_omit_retained_native(self):
  def change(path,data):
   if str(path).endswith(CFG['scope']+'/summary.json'):data['rows'][0]['nearbyNativeActors']=[]
   return data
  with self.assertRaises(AssertionError):self.run_profile(change=change)
 def test_finite_profile_cannot_drop_coordinate_world(self):
  def change(path,data):
   if str(path).endswith(CFG['finiteModes']+'/mode-checks.json.gz'):data['rows'].pop()
   return data
  with self.assertRaises(AssertionError):self.run_profile(change=change)
if __name__=='__main__':unittest.main()
