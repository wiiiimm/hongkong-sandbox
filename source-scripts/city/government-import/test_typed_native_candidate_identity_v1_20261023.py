import unittest
from copy import deepcopy
from typed_native_candidate_identity_v1_20261023 import qualify

def fixture():
    forms=[dict(uid='landsd/1:0',structureType='Tower',buildingCSUID='1234567890T20050430',objectId=1,buildingId=11,baseHeightHKPD=10,topHeightHKPD=50),dict(uid='landsd/2:0',structureType='Podium',buildingCSUID='1234567890P20050430',objectId=2,buildingId=12,baseHeightHKPD=4,topHeightHKPD=10)]
    matches=[dict(uid=f['uid'],buildingCSUID=f['buildingCSUID'],objectId=f['objectId'])for f in forms];modelid='B123456789001063C0';sha='a'*64
    row=dict(uid=forms[0]['uid'],modelId=modelid,sourceSHA256=sha,source=dict(building=forms[0]),native=dict(model=dict(modelId=modelid,asset=dict(sha256=sha),matching={k:deepcopy(matches)for k in ['officialCandidates','officialMatches','viewerMatches']})))
    primary=[dict(BuildingCSUID=f['buildingCSUID'],GeoRefNo='1234567890',Status='Active',BuildingBlockType=f['structureType'],BuildingID=f['buildingId'],BaseHeight=f['baseHeightHKPD'],TopHeight=f['topHeightHKPD'])for f in forms]
    raw=dict(uid=forms[0]['uid'],sourceSHA256=sha,originalOwnership=dict(sourceGraphVerified=True,originalRootName=modelid),exactCurrentComponentRoute=dict(qualified=True,uid=forms[0]['uid'],source=dict(building=forms[0]),official=matches[0]),reasons=['unique-viewerMatches','full-source-unrelated-overlap'])
    return raw,row,primary,forms

class TypedIdentity(unittest.TestCase):
    def test_only_metadata_reasons_replaced(self):
        args=fixture();before=deepcopy(args);r=qualify(*args);self.assertTrue(r['typedRoutingQualified']);self.assertFalse(r['passed']);self.assertEqual(r['reasons'],['full-source-unrelated-overlap']);self.assertEqual(args,before)
    def test_two_towers_remain_ambiguous(self):
        raw,row,primary,forms=fixture();forms[1]['structureType']='Tower'
        with self.assertRaises(AssertionError):qualify(raw,row,primary,forms)
    def test_foreign_native_candidate_rejected(self):
        raw,row,primary,forms=fixture();row['native']['model']['matching']['officialCandidates'][1]['buildingCSUID']='0000000000P20050430'
        with self.assertRaises(AssertionError):qualify(raw,row,primary,forms)
    def test_changed_source_hash_rejected(self):
        raw,row,primary,forms=fixture();row['sourceSHA256']='b'*64
        with self.assertRaises(AssertionError):qualify(raw,row,primary,forms)
    def test_wrong_model_subtype_rejected(self):
        raw,row,primary,forms=fixture();row['modelId']='B123456789002063C0'
        with self.assertRaises(AssertionError):qualify(raw,row,primary,forms)
    def test_stale_primary_record_rejected(self):
        raw,row,primary,forms=fixture();primary[0]['Status']='Inactive'
        with self.assertRaises(AssertionError):qualify(raw,row,primary,forms)
    def test_geographic_cell_failure_preserved(self):
        args=fixture();args[0]['reasons'].append('original-source-does-not-cover-whole-georef-cell');r=qualify(*args);self.assertIn('original-source-does-not-cover-whole-georef-cell',r['reasons'])

if __name__=='__main__':unittest.main()
