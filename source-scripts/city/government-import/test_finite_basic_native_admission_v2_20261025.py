"""Real frozen A evidence, synthetic acceptance fixture only; no DB or asset writes."""
import copy,unittest
from unittest.mock import patch
import finite_basic_native_admission_v2_20261025 as admission
BASE=admission.BASE
UID='landsd/255539:0';PARENT='landsd/256136:0'
CFG=dict(sources={UID:'5a9ae96e9b758dc4269a11021a873a5d2c0499e5b6fc655890789663cd9f8d51'},currentNativeActors=6957,finiteEvidence='government-xl-beverly-a-after-fe-finite-support-bindings-v1-20261025',finiteModes='government-xl-beverly-ad-after-fe-four-world-basic-v1-20261025',finitePaths='government-xl-beverly-255539-after-k-basic-roof-paths-v1-20261025',nativeContext='government-xl-beverly-ad-after-fe-native-contacts-v1-20261025',retainedNativeUids=[PARENT,'landsd/255543:0'],scope='government-xl-beverly-a-after-fe-model-scope-v1-20261025',nativeAvailabilityDependenciesByUid={UID:PARENT},nativeFallbackContext='government-xl-beverly-ad-after-fe-native-fallback-contacts-v1-20261025',nativeDependencyFailure='government-xl-beverly-a-after-fe-native-failure-recovered-v1-20261025',browser='government-xl-beverly-a-after-fe-private-browser-v1-20261025')
def local_receipt(folder):
 r=admission.read(folder/'result.json');return r,{q['path']:q['sha256']for q in r['evidenceRefs']}
def fixture():
 native=admission.read(BASE/CFG['nativeContext']/'summary.json')['rows'];retained={r['nativeUid']:r['rawCurrentNativeEntry']for r in native if r['uid']==UID}
 reports=[];images=[]
 for width in [390,1280]:
  p=BASE/CFG['browser']/str(width)/'staged-browser.json';r=admission.read(p);reports.append(dict(path=str(p.relative_to(admission.ROOT)),sha256=admission.digest(p.read_bytes())))
  for v in r['retainedNativeOwnViews']:
   path=p.parent/v['file'];images.append(dict(uid=v['uid'],width=width,time=v['time'],path=str(path.relative_to(admission.ROOT)),sha256=admission.digest(path.read_bytes())))
 manifest=admission.ROOT/'3d-viewer/city/data/manifest.json'
 return dict(testOnlySyntheticAcceptance=True,sourceSpecificPhysicalInterpretationAccepted=True,completeNeighbourInterpretationAccepted=True,completeFourWorldCanonicalRetainedBasicSupport=False,completeFourWorldFiniteRetainedBasicSupport=True,sourceGeometryChanges=0,sourcePoseChanges=0,terrainEdits=False,sourceSHA256ByUid=CFG['sources'],retainedBasicSupportDependencies=admission.read(BASE/CFG['finiteEvidence']/'support-bindings.json'),retainedNativeEntries=retained,currentManifest=dict(path=str(manifest.relative_to(admission.ROOT)),sha256=admission.digest(manifest.read_bytes())),retainedImagesActuallyViewed=images,browserReports=reports,runtimeAvailabilityDependenciesByUid={UID:PARENT})
class NativeFiniteAvailability(unittest.TestCase):
 def run_profile(self,review=None,config=None,change=None):
  original=admission.read
  def read(path):
   value=original(path);return change(path,value)if change else value
  with patch.object(admission,'authenticate',side_effect=local_receipt),patch.object(admission,'read',side_effect=read):return admission.replay(config or copy.deepcopy(CFG),review or fixture())
 def test_real_frozen_profile_passes(self):self.assertTrue(self.run_profile())
 def test_canonical_failure_cannot_be_relabelled(self):
  q=fixture();q['completeFourWorldCanonicalRetainedBasicSupport']=True
  with self.assertRaises(AssertionError):self.run_profile(q)
 def test_changed_source_refused(self):
  q=fixture();q['sourceSHA256ByUid']={UID:'0'*64}
  with self.assertRaises(AssertionError):self.run_profile(q)
 def test_native_hold_must_stay_unchanged(self):
  q=fixture();q['retainedNativeEntries'][PARENT]['publicationApproved']=True
  with self.assertRaises(AssertionError):self.run_profile(q)
 def test_all_retained_images_required(self):
  q=fixture();q['retainedImagesActuallyViewed'].pop()
  with self.assertRaises(AssertionError):self.run_profile(q)
 def test_missing_native_dependency_refused(self):
  q=copy.deepcopy(CFG);q['nativeAvailabilityDependenciesByUid']={}
  with self.assertRaises(AssertionError):self.run_profile(config=q)
 def test_wrong_native_dependency_refused(self):
  q=copy.deepcopy(CFG);q['nativeAvailabilityDependenciesByUid']={UID:'landsd/255543:0'}
  r=fixture();r['runtimeAvailabilityDependenciesByUid']=q['nativeAvailabilityDependenciesByUid']
  with self.assertRaises(AssertionError):self.run_profile(r,config=q)
 def test_incomplete_native_geometry_refused(self):
  def change(path,data):
   if str(path).endswith('255539:0--256136:0--original.json.gz'):data['sourceFacesOmitted']=1
   return data
  with self.assertRaises(AssertionError):self.run_profile(change=change)
 def test_missing_fallback_world_refused(self):
  def change(path,data):
   if str(path).endswith(CFG['nativeFallbackContext']+'/summary.json'):next(r for r in data['rows']if r['uid']==UID)['modes'].pop()
   return data
  with self.assertRaises(AssertionError):self.run_profile(change=change)
 def test_incomplete_fallback_geometry_refused(self):
  def change(path,data):
   if str(path).endswith(CFG['nativeFallbackContext']+'/255539:0--256136:0--original.json.gz'):data['sourceFacesOmitted']=1
   return data
  with self.assertRaises(AssertionError):self.run_profile(change=change)
 def test_failed_parent_requires_actual_own_basic_geometry(self):
  def change(path,data):
   if str(path).endswith(CFG['nativeDependencyFailure']+'/browser.json'):data['failed']['ownFeaturePresent']=False
   return data
  with self.assertRaises(AssertionError):self.run_profile(change=change)
 def test_retry_requires_exact_original_parent(self):
  def change(path,data):
   if str(path).endswith(CFG['nativeDependencyFailure']+'/browser.json'):data['recovered'][1]['sourceSHA256']='0'*64
   return data
  with self.assertRaises(AssertionError):self.run_profile(change=change)
if __name__=='__main__':unittest.main()
