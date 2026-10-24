"""Actual current-source fixtures and adverse retained-source/dependency cases."""
import copy,unittest
from run import ROOT,read
from skytower_original_catalogue_scope_v1_20261024 import *
B=ROOT/'docs/astra-city/government-import';P='government-xl-next-six-after-plaza-'
class Scope(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  r=next(r for r in read(B/(P+'normalized-runtime-v1-20261024')/'selection.json.gz')['rows']if r['uid']==UID);m=copy.deepcopy(r['candidate']['entry']);m.update(proceduralWindows=False,supportDependencies=[dict(uid=PARENT,state='installed',buildingCSUID=PARENT_CSUID,sha256=PARENT_SHA)])
  cls.model=[m];cls.scope=read(B/(P+'current-scope-v1-20261024')/'summary.json');cls.native=read(B/(P+'current-native-contacts-v1-20261024')/'summary.json');manifest=read(ROOT/'3d-viewer/city/data/manifest.json');cls.current={e['uid']:e for url in manifest['officialModelCatalogues']for e in read(ROOT/'3d-viewer'/url)['models']}
 def reject_model(self,mutate):
  models=copy.deepcopy(self.model);mutate(models[0])
  with self.assertRaises((AssertionError,KeyError)):verify_metadata(models)
 def test_actual_metadata(self):self.assertTrue(verify_metadata(self.model))
 def test_actual_complete_native_scope(self):self.assertTrue(verify_native_scope(self.scope,self.native,self.current))
 def test_wrong_source_sha(self):self.reject_model(lambda m:m.update(sha256='0'*64))
 def test_missing_parent(self):self.reject_model(lambda m:m.update(supportDependencies=[]))
 def test_wrong_parent_revision(self):self.reject_model(lambda m:m['supportDependencies'][0].update(sha256='0'*64))
 def test_wrong_parent_uid(self):self.reject_model(lambda m:m['supportDependencies'][0].update(uid=NEIGHBOUR))
 def test_pose_edit(self):self.reject_model(lambda m:m.update(verticalPlacementOffsetHKPD=.01))
 def test_partial_geometry(self):self.reject_model(lambda m:m.update(partialGeometry=True))
 def test_foreign_suppression(self):self.reject_model(lambda m:m.update(suppressesBuildingUids=[NEIGHBOUR]))
 def test_missing_retained_scope(self):
  scope=copy.deepcopy(self.scope);r=next(r for r in scope['rows']if r['uid']==UID);r['nearbyNativeActors']=r['nearbyNativeActors'][:1]
  with self.assertRaises(AssertionError):verify_native_scope(scope,self.native,self.current)
 def test_changed_existing_dependency(self):
  current=copy.deepcopy(self.current);current[NEIGHBOUR]['supportDependencies']=[]
  with self.assertRaises(AssertionError):verify_native_scope(self.scope,self.native,current)
 def test_dropped_coordinate_stream(self):
  native=copy.deepcopy(self.native);r=next(r for r in native['rows']if r['uid']==UID);r['modes']=r['modes'][:3]
  with self.assertRaises(AssertionError):verify_native_scope(self.scope,native,self.current)
 def test_area_contact_count_cannot_be_relabelled(self):
  native=copy.deepcopy(self.native);r=next(r for r in native['rows']if r['uid']==UID and r['nativeUid']==NEIGHBOUR);r['modes'][0]['areaContactPairs']=0
  with self.assertRaises(AssertionError):verify_native_scope(self.scope,native,self.current)
 def test_stale_census(self):
  current=copy.deepcopy(self.current);current.pop(next(u for u in current if u not in RETAINED))
  with self.assertRaises(AssertionError):verify_native_scope(self.scope,self.native,current)
if __name__=='__main__':unittest.main()
