import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from basic_fallback_protections import stage_basic_fallback_protections,validated


class ProtectionTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
  self.cat=self.root/'3d-viewer/compound/catalogue.json';self.cat.parent.mkdir(parents=True)
  asset=self.cat.parent/'original.gz';asset.write_bytes(b'original compound')
  self.owner=dict(uid='landsd/2:0',sha256=hashlib.sha256(asset.read_bytes()).hexdigest(),asset='original.gz',publicationApproved=False,suppressesBuildingUids=['landsd/1:0','landsd/3:0'])
  self.cat.write_text(json.dumps({'models':[self.owner]}));self.original={'officialModelCatalogues':['compound/catalogue.json']}
  self.target=dict(uid='landsd/1:0',buildingCSUID='one',sha256='a'*64,publicationApproved=True,placementReviewed=True,identityReviewApproved=True)
  self.row=dict(uid=self.target['uid'],buildingCSUID='one',sourceSHA256='a'*64,suppressorUid=self.owner['uid'],suppressorSourceSHA256=self.owner['sha256'])
 def stage(self,rows=None,edits=None,new=None,original=None):
  manifest=copy.deepcopy(original or self.original);report={}
  stage_basic_fallback_protections(self.root,{'basicFallbackProtections':[self.row]if rows is None else rows},original or self.original,manifest,edits or {},{self.target['uid']:self.target}if new is None else new,report,lambda p:json.loads(p.read_bytes()),lambda p:hashlib.sha256(p.read_bytes()).hexdigest())
  return manifest,report
 def test_exact_new_source_and_unchanged_held_compound(self):
  before=self.cat.read_bytes();manifest,report=self.stage()
  self.assertEqual(manifest['basicFallbackProtections'],[self.row]);self.assertEqual(self.cat.read_bytes(),before)
  self.assertFalse(json.loads(before)['models'][0]['publicationApproved']);self.assertEqual(report['basicFallbackProtections']['retained'],0)
 def test_stale_missing_or_unaccepted_targets_reject(self):
  for key,value in [('sourceSHA256','b'*64),('buildingCSUID','wrong'),('suppressorSourceSHA256','b'*64),('suppressorUid','missing')]:
   with self.subTest(key=key),self.assertRaises(AssertionError):self.stage([{**self.row,key:value}])
  with self.assertRaises(AssertionError):self.stage(new={})
  for flag in ['publicationApproved','placementReviewed','identityReviewApproved']:
   with self.subTest(flag=flag),self.assertRaises(AssertionError):self.stage(new={self.target['uid']:{**self.target,flag:False}})
 def test_unrelated_suppressions_metadata_and_changed_bytes_reject(self):
  with self.assertRaises(AssertionError):self.stage([{**self.row,'uid':'landsd/4:0'}],new={'landsd/4:0':{**self.target,'uid':'landsd/4:0'}})
  with self.assertRaises(AssertionError):self.stage(edits={self.cat:json.dumps({'models':[{**self.owner,'publicationApproved':True}]}).encode()})
  (self.cat.parent/'original.gz').write_bytes(b'changed')
  with self.assertRaises(AssertionError):self.stage()
 def test_malformed_duplicate_and_existing_policies_are_checked(self):
  with self.assertRaises(AssertionError):validated(None)
  for rows in [{},[self.row,self.row],[{**self.row,'extra':True}],[{**self.row,'suppressorUid':self.row['uid']}]]:
   with self.subTest(rows=rows),self.assertRaises(AssertionError):self.stage(rows)
  original={**self.original,'basicFallbackProtections':[self.row]}
  with self.assertRaises(AssertionError):self.stage(original=original)
  manifest,_=self.stage([],original=original)
  self.assertEqual(manifest['basicFallbackProtections'],[self.row])
  with self.assertRaises(AssertionError):self.stage([],new={self.target['uid']:{**self.target,'sha256':'b'*64}},original=original)


if __name__=='__main__':unittest.main()
