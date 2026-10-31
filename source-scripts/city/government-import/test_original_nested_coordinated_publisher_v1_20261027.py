import copy
import unittest
from original_nested_coordinated_publisher_v1_20261027 import publisher
from run import ROOT,HERE,read
from primrose_compound_foundation_v2_20261015 import module
class NarrowPublisherAdapterTest(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  b=ROOT/'docs/astra-city/government-import';cls.patch=read(b/'government-xl-after-waterfront-ocean-four-nested-pair-surface-v1-20261027/summary.json');p=read(b/'government-xl-ocean-four-original-physical-review-v2-20261027/ROOT-PHYSICAL-REVIEW.json');cls.sources=p['sourceSHA256ByUid'];cls.owners=p['groundOwnerUids'];cls.old=ROOT/'3d-viewer'/cls.patch['replacedNativeTerrain'][0]['url'];cls.new=ROOT/cls.patch['candidate']['path'];cls.pub,_=publisher('test_narrow_nested_publisher',cls.old,cls.new,cls.owners,cls.sources,cls.patch)
 def test_all_other_canonical_functions_unchanged(self):
  old=module('test_canonical_publisher_reference',HERE.parent/'island-detail-integration/publish.py')
  names=[n for n,v in vars(old).items()if callable(v)and getattr(v,'__module__',None)==old.__name__ and n!='validate_patch']
  self.assertGreater(len(names),10)
  for n in names:self.assertEqual(getattr(self.pub,n).__code__,getattr(old,n).__code__,n)
 def test_wrong_root_rejected_before_nested_validation(self):
  with self.assertRaisesRegex(AssertionError,'Exact current root terrain required'):self.pub.validate_patch(read(self.new),{})
 def test_unrelated_invalid_patch_keeps_canonical_rejection(self):
  with self.assertRaises(KeyError):self.pub.validate_patch({}, {})
 def test_changed_candidate_checksum_rejected(self):
  patch=copy.deepcopy(self.patch);patch['candidate']['sha256']='0'*64
  with self.assertRaises(AssertionError):publisher('test_changed_candidate_rejected',self.old,self.new,self.owners,self.sources,patch)
 def test_changed_installed_parent_checksum_rejected(self):
  patch=copy.deepcopy(self.patch);patch['replacedNativeTerrain'][0]['sha256']='0'*64
  with self.assertRaises(AssertionError):publisher('test_changed_parent_rejected',self.old,self.new,self.owners,self.sources,patch)
if __name__=='__main__':unittest.main()
