import unittest
from copy import deepcopy
from ocean_four_original_identity_review_v1_20261027 import stable_identity

class IdentityBindings(unittest.TestCase):
 def setUp(self):
  self.form=dict(uid='landsd/234188:0',objectId=234188,buildingCSUID='3540017451P20060116',buildingId=1108247442,structureType='Podium',baseHeightHKPD=3.4,topHeightHKPD=17.2)
  self.entry={k:self.form[k]for k in ['uid','objectId','buildingCSUID']}
  self.primary=dict(OBJECTID=233817,BuildingID=1108247442,BuildingCSUID='3540017451P20060116',GeoRefNo='3540017451',BuildingBlockType='Podium',BaseHeight=3.4,TopHeight=17.2,Status='Active')
 def test_mutable_service_object_id_does_not_reassign_source(self):
  self.assertNotEqual(self.form['objectId'],self.primary['OBJECTID'])
  self.assertTrue(all(stable_identity(self.form,self.entry,self.primary,'B354001745102063C0').values()))
 def test_every_stable_source_contradiction_is_rejected(self):
  for key,bad in [('BuildingID',1),('BuildingCSUID','3540017451T20060116'),('GeoRefNo','0000000000'),('BuildingBlockType','Tower'),('BaseHeight',3.5),('TopHeight',17.3),('Status','Inactive')]:
   primary=deepcopy(self.primary);primary[key]=bad
   with self.subTest(field=key),self.assertRaises(AssertionError):stable_identity(self.form,self.entry,primary,'B354001745102063C0')
 def test_wrong_runtime_uid_or_object_id_is_rejected(self):
  for key,bad in [('uid','landsd/1:0'),('objectId',1),('buildingCSUID','wrong')]:
   entry=deepcopy(self.entry);entry[key]=bad
   with self.subTest(field=key),self.assertRaises(AssertionError):stable_identity(self.form,entry,self.primary,'B354001745102063C0')
if __name__=='__main__':unittest.main()
