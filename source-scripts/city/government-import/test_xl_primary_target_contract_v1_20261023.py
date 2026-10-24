import copy,unittest
from xl_primary_target_contract_v1_20261023 import compare_target

class ExactTargetTests(unittest.TestCase):
    def setUp(self):
        self.source=dict(uid='landsd/1:0',originalModelId='B123456789001062G0',sourceKey='cache/B123456789001062G0',indexedSourceSHA256='source')
        self.form=dict(uid='landsd/1:0',buildingCSUID='1234567890T20000101',buildingId='building',structureType='Tower',baseHeightHKPD=5.,topHeightHKPD=30.,objectId=1)
        self.record=dict(GeoRefNo='1234567890',BuildingCSUID=self.form['buildingCSUID'],BuildingID='building',BuildingBlockType='Tower',BaseHeight=5.,TopHeight=30.,Status='Active',OBJECTID=9)
    def test_exact_metadata_is_not_source_or_install_approval(self):
        d=compare_target(self.source,self.form,[self.record]);self.assertTrue(d['exactTargetMetadataQualified']);self.assertTrue(d['officialObjectIdChanged']);self.assertFalse(d['sourceIdentityAccepted']);self.assertFalse(d['installationApproved'])
    def test_subtype_disambiguates_same_georef(self):
        other=dict(self.record,BuildingBlockType='Podium',BuildingCSUID='1234567890P20000101')
        self.assertTrue(compare_target(self.source,self.form,[other,self.record])['exactTargetMetadataQualified'])
    def test_revised_csuid_is_not_silently_substituted(self):
        record=dict(self.record,BuildingCSUID='1234567890T20261023');d=compare_target(self.source,self.form,[record]);self.assertIn('official-current-field-differs:BuildingCSUID',d['reasons']);self.assertFalse(d['permanentRejection'])
    def test_wrong_source_subtype_rejected(self):
        form=dict(self.form,structureType='Podium');self.assertIn('current-target-subtype-differs',compare_target(self.source,form,[self.record])['reasons'])
    def test_duplicate_official_records_not_collapsed(self):
        d=compare_target(self.source,self.form,[self.record,copy.deepcopy(self.record)]);self.assertIn('typed-official-record-ambiguous',d['reasons'])
    def test_height_drift_preserved(self):
        d=compare_target(self.source,self.form,[dict(self.record,BaseHeight=5.001)]);self.assertEqual(d['fieldDifferences']['BaseHeight'],{'official':5.001,'viewer':5.})
    def test_missing_target_and_primary_are_pending(self):
        d=compare_target(self.source,None,[]);self.assertFalse(d['exactTargetMetadataQualified']);self.assertIn('current-viewer-target-missing',d['reasons']);self.assertFalse(d['permanentRejection'])
    def test_unmapped_source_key_preserved(self):
        source=dict(self.source,uid=None,sourceKey='cache/unmapped-original');d=compare_target(source,None,[]);self.assertIsNone(d['uid']);self.assertEqual(d['sourceKey'],'cache/unmapped-original');self.assertFalse(d['installationApproved'])
    def test_wrong_georef_cannot_match(self):
        form=dict(self.form,buildingCSUID='9999999999T20000101');self.assertIn('current-target-georef-differs',compare_target(self.source,form,[self.record])['reasons'])

if __name__=='__main__':unittest.main()
