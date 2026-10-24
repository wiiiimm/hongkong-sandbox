"""Hermetic actual-entry/adverse checks, not ROOT publication authorization."""
import unittest
from copy import deepcopy
from unittest.mock import patch
import heya_aqua_exact_rollback_recovery_20261011 as h
class ActualEntry(unittest.TestCase):
 def setUp(self):
  self.entry=h.read(h.ROLE/'private-stage-entry.json')
  self.approval=dict(reviewer='ROOT',independentlyVerified=True,approvedMetadataChanges=h.CHANGE,uid=h.T,sourceSHA256=h.SHA,manifestSHA256=h.CURRENT,snapshotId=h.PREVIOUS,originalEntry=h.ref(h.ROLE/'private-stage-entry.json'),sourceRootCertificate=h.ref(h.SOURCE_CERT),historicalContract=h.ref(h.HISTORY),geometryChanges=0,terrainChanges=0,currentInstallationCredit=False)
 def test_exact_three_changes_only(self):
  out=h.augmented_entry(self.entry,self.approval);self.assertEqual({k:out[k]for k in h.CHANGE},h.CHANGE);self.assertEqual({k:v for k,v in out.items()if k not in h.CHANGE},{k:v for k,v in self.entry.items()if k not in h.CHANGE})
 def test_nonroot_rejected(self):
  self.approval['reviewer']='agent'
  with self.assertRaises(AssertionError):h.augmented_entry(self.entry,self.approval)
 def test_unverified_rejected(self):
  self.approval['independentlyVerified']=False
  with self.assertRaises(AssertionError):h.augmented_entry(self.entry,self.approval)
 def test_changed_original_geometry_rejected(self):
  self.entry['rootTranslation'][0]+=1
  with self.assertRaises(AssertionError):h.augmented_entry(self.entry,self.approval)
 def test_wrong_identity_source_rejected(self):
  self.approval['sourceSHA256']='0'*64
  with self.assertRaises(AssertionError):h.augmented_entry(self.entry,self.approval)
 def test_missing_publication_flag_rejected(self):
  self.approval['approvedMetadataChanges']={**h.CHANGE,'publicationApproved':False}
  with self.assertRaises(AssertionError):h.augmented_entry(self.entry,self.approval)
 def test_changed_support_dependency_rejected(self):
  self.entry['supportDependencies'][0]['state']='candidate'
  with self.assertRaises(AssertionError):h.augmented_entry(self.entry,self.approval)
 def test_orphan_is_not_current_snapshot(self):
  self.approval['snapshotId']=h.ORPHAN
  with self.assertRaises(AssertionError):h.augmented_entry(self.entry,self.approval)
 def test_claimed_current_credit_rejected(self):
  self.approval['currentInstallationCredit']=True
  with self.assertRaises(AssertionError):h.augmented_entry(self.entry,self.approval)
 def test_actual_three_archives_are_complete(self):self.assertEqual(len(h.historical_refs()),3)
 def test_fourth_archive_rejected(self):
  old=h.read(h.HISTORY);old['actualHistoricalBytes'].append(deepcopy(old['actualHistoricalBytes'][0]))
  with patch.object(h,'read',return_value=old):
   with self.assertRaises(AssertionError):h.historical_refs()
 def test_historical_claim_current_credit_rejected(self):
  old=h.read(h.HISTORY);old['currentAcceptanceAfterSceneChange']=True
  with patch.object(h,'read',return_value=old):
   with self.assertRaises(AssertionError):h.historical_refs()
if __name__=='__main__':unittest.main()
