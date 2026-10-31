import copy
import unittest
from original_coordinated_retained_contract_v1_20261027 import verify_metadata,verify_retained_entries,verify_terrain,verify_native_interfaces
from run import ROOT,HERE,read
P='government-xl-after-waterfront-ocean-four-corrected-'
class CoordinatedRetainedContractTest(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  b=ROOT/'docs/astra-city/government-import';cls.physical=read(b/'government-xl-ocean-four-original-physical-review-v2-20261027/ROOT-PHYSICAL-REVIEW.json');cls.sources=cls.physical['sourceSHA256ByUid'];cls.supports=cls.physical['supportByUid'];cls.owners=cls.physical['groundOwnerUids'];cls.original={r['uid']:r['candidate']['entry']for r in read(b/(P+'runtime-v1-20261027')/'selection.json.gz')['rows']};cls.models=read(HERE/'local/government-xl-ocean-four-atomic-lifecycle-stage-v1-20261027/catalogue.json')['models'];cls.patch=read(b/'government-xl-after-waterfront-ocean-four-nested-pair-surface-v1-20261027/summary.json');replaced=cls.patch['replacedNativeTerrain'][0];cls.old=read(ROOT/'3d-viewer'/replaced['url']);cls.new=read(ROOT/cls.patch['candidate']['path']);cls.oldsha=replaced['sha256'];cls.newsha=cls.patch['candidate']['sha256'];cls.scope=read(b/(P+'model-scope-v1-20261027')/'summary.json');cls.contacts=read(b/(P+'native-contacts-v1-20261027')/'summary.json');cls.current={m['uid']:m for url in read(ROOT/'3d-viewer/city/data/manifest.json')['officialModelCatalogues']for m in read(ROOT/'3d-viewer'/url)['models']}
 def metadata(self,models):return verify_metadata(models,self.sources,self.supports,self.original,self.owners)
 def terrain(self,old,new,owners=None):return verify_terrain(old,new,owners or self.owners,self.sources,self.patch,self.oldsha,self.newsha)
 def test_actual_metadata(self):self.assertTrue(self.metadata(self.models))
 def test_partial_activation_group_rejected(self):
  data=copy.deepcopy(self.models);data[0]['activationGroup'].pop()
  with self.assertRaises(AssertionError):self.metadata(data)
 def test_source_pose_edit_rejected(self):
  data=copy.deepcopy(self.models);data[0]['rootTranslation'][1]=1
  with self.assertRaises(AssertionError):self.metadata(data)
 def test_crop_metadata_rejected(self):
  data=copy.deepcopy(self.models);data[0]['partialSource']=True
  with self.assertRaises(AssertionError):self.metadata(data)
 def test_external_support_rejected(self):
  data=copy.deepcopy(self.models);next(m for m in data if m.get('supportDependencies'))['supportDependencies'][0]['uid']='landsd/1:0'
  with self.assertRaises(AssertionError):self.metadata(data)
 def test_actual_terrain_retention(self):self.assertEqual(self.terrain(self.old,self.new)['exactRetainedChildren'],14)
 def test_other_old_child_edit_rejected(self):
  data=copy.deepcopy(self.new);data['patches'][0]['meta']['testMutation']=True
  with self.assertRaises(AssertionError):self.terrain(self.old,data)
 def test_outer_grid_edit_rejected(self):
  data=copy.deepcopy(self.new);data['elev'][0]+=1
  with self.assertRaises(AssertionError):self.terrain(self.old,data)
 def test_upper_cannot_receive_ground_owner_credit(self):
  with self.assertRaises(AssertionError):self.terrain(self.old,self.new,list(self.sources))
 def test_existing_flags_cannot_be_rewritten(self):
  uid=next(iter(self.physical['retainedNativeEntries']));current=copy.deepcopy(self.current);current[uid]['publicationApproved']=not current[uid].get('publicationApproved',False)
  with self.assertRaises(AssertionError):verify_retained_entries(current,self.physical['retainedNativeEntries'],self.sources,6985)
 def test_actual_native_interface_scope(self):self.assertTrue(verify_native_interfaces(self.physical,self.scope,self.contacts,self.current,self.sources))
 def test_nonempty_native_pair_cannot_disappear(self):
  data=copy.deepcopy(self.contacts);data['rows'].pop()
  with self.assertRaises(AssertionError):verify_native_interfaces(self.physical,self.scope,data,self.current,self.sources)
if __name__=='__main__':unittest.main()
