import unittest
from west_kowloon_pair_original_identity_review_v1_20261027 import validate_primary, EXPECTED

class PrimaryIdentity(unittest.TestCase):
 def setUp(self):
  self.expected=EXPECTED['landsd/309340:0']
  self.form=dict(buildingCSUID=self.expected['csuid'],structureType='Tower',baseHeightHKPD=5.7,topHeightHKPD=12)
  self.primary=dict(BuildingCSUID=self.expected['csuid'],BuildingID=self.expected['buildingID'],Status='Active',GeoRefNo='3481019326',BuildingBlockType='Tower',BaseHeight=5.7,TopHeight=12,OBJECTID=309487)
 def test_exact_record_and_changed_service_object_id(self):
  validate_primary(self.form,self.primary,self.expected)
  validate_primary(self.form,dict(self.primary,OBJECTID=900001),self.expected)
 def test_changed_stable_identity_or_role_is_rejected(self):
  for key,value in [('BuildingCSUID','3481019326T20200101'),('BuildingID',1),('GeoRefNo','3481019327'),('Status','Demolished'),('BuildingBlockType','Podium'),('BaseHeight',6),('TopHeight',13),('OBJECTID',0)]:
   with self.subTest(key=key),self.assertRaises(AssertionError):validate_primary(self.form,dict(self.primary,**{key:value}),self.expected)

if __name__=='__main__':unittest.main()
