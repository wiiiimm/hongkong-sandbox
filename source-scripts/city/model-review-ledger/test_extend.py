import unittest
from extend import build
class SourceExtension(unittest.TestCase):
 def test_order_independent_extension_preserves_existing_rows(self):
  old={'snapshotId':'old','parts':[{'uid':'a','candidate':{'sha256':'original'},'sourceProgress':'installed'}]};addition={'uid':'b','candidate':{'sha256':'new'},'sourceProgress':'prepared-for-review'}
  one=build(old,[{'parts':[addition]}]);two=build(old,[{'parts':[old['parts'][0],addition]}])
  self.assertEqual(one,two);self.assertEqual(one['parts'][0],old['parts'][0]);self.assertEqual(len(one['parts']),2)
 def test_conflicting_existing_source_requires_explicit_new_review(self):
  old={'snapshotId':'old','parts':[{'uid':'a','candidate':{'sha256':'original'}}]}
  with self.assertRaisesRegex(ValueError,'Conflicting'):build(old,[{'parts':[{'uid':'a','candidate':{'sha256':'changed'}}]}])
class SourceRefresh(unittest.TestCase):
 def fixture(self):
  old={'uid':'landsd/1:0','objectId':1,'csuid':'source1','identityEvidence':{'path':'original'},'landmarkIds':['old'],'candidate':{'sha256':'old'}}
  new={'uid':old['uid'],'objectId':1,'csuid':'source1','landmarkIds':['new'],'candidate':{'uid':old['uid'],'objectId':1,'buildingCSUID':'source1','sha256':'new'}}
  return {'snapshotId':'old','parts':[old]},new
 def test_explicit_refresh_preserves_provenance_and_membership(self):
  old,new=self.fixture();result=build(old,[{'parts':[new]}],[new['uid']]);p=result['parts'][0]
  self.assertEqual(p['candidate']['sha256'],'new');self.assertEqual(p['identityEvidence'],{'path':'original'});self.assertEqual(p['landmarkIds'],['new','old']);self.assertEqual(old['parts'][0]['candidate']['sha256'],'old')
 def test_identity_changes_and_duplicate_refresh_rejected(self):
  old,new=self.fixture()
  for change in ({'objectId':2},{'csuid':'other'},{'candidate':{**new['candidate'],'uid':'landsd/2:0'}}):
   with self.assertRaises(ValueError):build(old,[{'parts':[{**new,**change}]}],[new['uid']])
  with self.assertRaises(ValueError):build(old,[{'parts':[new,{**new,'name':'second'}]}],[new['uid']])
 def test_unknown_refresh_rejected(self):
  old,new=self.fixture()
  with self.assertRaises(ValueError):build(old,[],['landsd/99:0'])
if __name__=='__main__':unittest.main()

