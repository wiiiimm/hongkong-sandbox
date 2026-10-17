"""Counterexamples for stable primary lineage and full original geometry."""
import unittest
from datetime import datetime,timezone
import numpy as np
from popcorn_primary_original_identity_v2_20261009 import primary_proof
from run import digest
class PrimaryIdentityTests(unittest.TestCase):
 def setUp(self):
  uid='landsd/295421:0';csuid='4487218868T20110805';sha='a'*64
  self.form=dict(uid=uid,objectId=295421,buildingId=1810071419,buildingCSUID=csuid,structureType='Tower',rings=[[[0,0],[2,0],[2,2],[0,2],[0,0]]])
  self.row=dict(uid=uid,sourceSHA256=sha,modelId='B448721886801063C0',triangles=2,source={'building':self.form})
  self.proof=dict(uid=uid,sourceSHA256=sha,originalOwnership={'sourceGraphVerified':True},reasons=['current-target-does-not-cover-whole-georef-cell'])
  self.tri=np.array([[[0,5,0],[2,5,0],[2,5,2]],[[0,5,0],[2,5,2],[0,5,2]]],float)
  self.proof['worldTrianglesSHA256']=digest(self.tri.astype('<f8').tobytes())
  self.provider=dict(spatialReference={'wkid':2326},features=[dict(attributes=dict(OBJECTID=999,BuildingID=1810071419,BuildingCSUID=csuid,BuildingBlockType='Tower',GeoRefNo=csuid[:10],Status='Active',DateCreate=datetime(2011,8,5,tzinfo=timezone.utc).timestamp()*1000),geometry={'rings':[[[834500+x,816500-z] for x,z in self.form['rings'][0]]]})])
 def review(self):return primary_proof(self.proof,self.row,self.provider,self.tri,[])
 def change(self,key,value):self.provider['features'][0]['attributes'][key]=value;self.assertFalse(self.review()['passed'])
 def test_reindexed_provider_id_preserves_stable_identity_raw_failure_and_no_install_credit(self):
  p=self.review();self.assertTrue(p['passed']);self.assertEqual(p['primaryProviderObjectID'],999);self.assertEqual(p['currentViewerObjectID'],295421);self.assertEqual(p['rawWholeCellReasonsRetained'],self.proof['reasons']);self.assertFalse(p['wholeCoordinateCellUsedForSpatialCredit']);self.assertFalse(p['installationApproved'])
 def test_current_spatial_failure_not_replaced(self):self.proof['reasons'].append('full-source-target-coverage');self.assertFalse(self.review()['passed'])
 def test_duplicate_primary_rejects(self):self.provider['features']*=2;self.assertFalse(self.review()['passed'])
 def test_inactive_rejects(self):self.change('Status','Retired')
 def test_same_georef_different_csuid_rejects(self):self.change('BuildingCSUID','4487218868T20110806')
 def test_wrong_stable_id_rejects(self):self.change('BuildingID',1810071420)
 def test_wrong_type_rejects(self):self.change('BuildingBlockType','Podium')
 def test_wrong_creation_date_rejects(self):self.change('DateCreate',1312588800000)
 def test_wrong_crs_rejects(self):self.provider['spatialReference']['wkid']=3857;self.assertFalse(self.review()['passed'])
 def test_root_failure_rejects(self):
  self.proof['originalOwnership']['sourceGraphVerified']=False
  with self.assertRaises(AssertionError):self.review()
 def test_incomplete_source_rejects(self):
  self.tri=self.tri[:1]
  with self.assertRaises(AssertionError):self.review()
 def test_missing_primary_coverage_rejects(self):self.provider['features'][0]['geometry']['rings'][0][1][0]+=10;self.assertFalse(self.review()['passed'])
 def test_unrelated_overlap_retains_existing_limit(self):
  self.tri[:,:,0]+=1;self.proof['worldTrianglesSHA256']=digest(self.tri.astype('<f8').tobytes());foreign=dict(uid='landsd/foreign:0',rings=[[[2,0],[3,0],[3,2],[2,2],[2,0]]]);p=primary_proof(self.proof,self.row,self.provider,self.tri,[foreign]);self.assertIn('fresh-primary-full-source-spatial-bound:sourceExcessCoveredByUnrelatedFormsM2',p['reasons'])
 def test_other_source_cannot_use_named_contract(self):
  self.row['uid']='landsd/186723:0'
  with self.assertRaises(AssertionError):self.review()
 def test_y_only_world_change_rejects_even_when_full_projection_matches(self):
  self.tri[:,:,1]+=1
  with self.assertRaisesRegex(AssertionError,'decoded world triangles changed'):self.review()
if __name__=='__main__':unittest.main()
