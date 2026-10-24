"""Offline full-original fixtures + isolated temporary actual-history checks.

No current rebind/DB/lease. Prior23test source is reused as a fixture builder,
not modified or rerun. Synthetic current files never become numerical evidence.
"""
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import json
import unittest
import test_upton_adjacent_original_roof_wall_identity_context_draft_v1_20261011 as old
import upton_adjacent_original_roof_wall_identity_context_draft_v1_20261011 as P
import upton_adjacent_roof_wall_identity_only_wrapper_v1_20261011 as W
import upton_exact_actual_history_archive_bindings_draft_v1_20261011 as H

class WrapperTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  old.DraftTests.setUpClass()
  rows=P.read(old.ROOT,P.BASE+'government-xl-upton12728-12662-fresh-adjacent-identity-context-replay-draft-v1-20261011/identities.json')['rows']
  cls.foreign=next(x for x in rows if x['uid']==P.ADJACENT)
 def setUp(self):
  self.f=old.DraftTests();self.f.setUp();self.addCleanup(self.f.doCleanups)
  self.raw=deepcopy(self.foreign['rawFullCellIdentity']);self.owned=deepcopy(self.foreign['ownedIdentity'])
  self.raw['exactRouteManifestSHA256']=self.f.current['manifestSHA256']
 def apply(self):
  self.f.current['ordinaryProofCanonicalSHA256']=P.digest(P.canonical(self.f.proof));self.f.current['completeFormsCanonicalSHA256']=P.digest(P.canonical(self.f.forms))
  with patch.object(P,'frozen_context',return_value=(self.f.context,self.f.triangles)):
   return W.apply_identity_only(self.f.root,self.f.proof,self.raw,self.owned,self.f.forms,self.f.current,self.f.context_case,self.f.triangles)
 def reject(self):
  with self.assertRaises((AssertionError,KeyError,StopIteration,ValueError)):self.apply()
 def test_source_identification_only_with_complete_negatives_retained(self):
  r=self.apply();self.assertTrue(r['identityAccepted']);self.assertTrue(r['passed']);self.assertEqual(r['rawOrdinaryIdentityRetained'],self.f.proof)
  self.assertEqual(r['foreignOwnedProxyNegativesRetained'],self.owned);self.assertEqual(len(r['identityContext']['complete23ProperInteriorCrossingsRetained']),23)
  for k in ['physicalAccepted','installationApproved','foreignCollisionExemption','foreignTerrainExemption','sharedEdgeCredit','rootCredit','solidClearanceCredit','intentionalJointEstablished','engineeringOrLegalClaim']:self.assertFalse(r[k])
 def test_wrong_owned_uid(self):self.f.proof['uid']=P.ADJACENT;self.reject()
 def test_wrong_owned_source_sha(self):self.f.proof['sourceSHA256']='0'*64;self.reject()
 def test_changed_fme_root(self):self.f.context_case['context']['providerRootContext'][0]['originalRoot']['matrix'][13]+=1;self.reject()
 def test_missing_crossing(self):self.f.context_case['roles']['complete23ContactsRetained'].pop();self.reject()
 def test_crossing_substituted_with_point(self):self.f.context_case['roles']['complete23ContactsRetained'][0]['originalContact']['dimension']=0;self.reject()
 def test_missing_primary(self):self.f.context_case['roles']['primaryContexts']=[];self.reject()
 def test_changed_primary_page_evidence(self):self.f.context_case['roles']['primaryContexts'][0]['unwarpedExport']['sha256']='0'*64;self.reject()
 def test_foreign_uid_substitution(self):self.raw['uid']=P.UID;self.reject()
 def test_foreign_source_sha_substitution(self):self.raw['sourceSHA256']='0'*64;self.reject()
 def test_foreign_stale_scene(self):self.raw['exactRouteManifestSHA256']='0'*64;self.reject()
 def test_foreign_other_policy_not_accepted(self):self.raw['policy']='generic-pass';self.reject()
 def test_foreign_raw_failure_not_waived(self):self.raw['passed']=False;self.raw['reasons']=['full-source-unrelated-overlap'];self.reject()
 def test_foreign_extra_owned_reason_not_waived(self):self.owned['reasons'].append('full-source-extent');self.reject()
 def test_foreign_cache_replacement_accounting(self):self.raw['cachedShapeProxyReasonsReplaced'].pop();self.reject()
 def test_foreign_incomplete_cell(self):self.raw['exactWholeCellCoverage']['halves'][0]['exactProjectionCovered']=False;self.reject()
 def test_other_own_reason_retained_blocks_identity(self):
  self.f.proof['reasons'].append('full-source-extent');r=self.apply();self.assertFalse(r['passed']);self.assertFalse(r['identityAccepted']);self.assertEqual(r['reasons'],['full-source-extent'])

class ActualHistoryTests(unittest.TestCase):
 def setUp(self):
  self.t=TemporaryDirectory();self.addCleanup(self.t.cleanup);self.root=Path(self.t.name)
  self.old=b'actual old immutable bytes';self.sha=H.digest(self.old)
  (self.root/'old.json').write_bytes(self.old);(self.root/'current.json').write_bytes(b'new current bytes')
  self.contract=dict(actualHistoricalBytesOnly=True,historicalArchives=[dict(originalPath='current.json',historicalSHA256=self.sha,actualArchive=dict(path='old.json',sha256=self.sha))])
 def load(self):
  p=self.root/'contract.json';p.write_bytes(json.dumps(self.contract).encode());return H.load_contract(self.root,'contract.json',H.digest(p.read_bytes()))
 def test_existing_root_actual_archives_exact(self):
  path=P.BASE+'government-xl-upton-actual-pre-heya-source-history-root-v1-20261011/root-actual-history-contract.json'
  c=H.load_contract(old.ROOT,path,'51b1ae85bd5cf3bf59e6e0fb1daa921a85835f2fe793d4d2ed00a9e0a5ee5a68');self.assertGreater(len(c['historicalArchives']),0)
 def test_exact_old_archive_maintains_original_reference(self):
  c=self.load();e=dict(path='current.json',sha256=self.sha);r=H.exact_ref(self.root,e,c)
  self.assertEqual(r['originalEvidenceRef'],e);self.assertEqual(r['actualVerifiedFile']['path'],'old.json');self.assertTrue(r['historicalArchiveUsed']);self.assertEqual((self.root/'current.json').read_bytes(),b'new current bytes')
 def test_direct_exact_actual_file_no_archive_needed(self):
  e=dict(path='old.json',sha256=self.sha);r=H.exact_ref(self.root,e,self.load());self.assertFalse(r['historicalArchiveUsed'])
 def test_wrong_archive_bytes(self):
  (self.root/'old.json').write_bytes(b'wrong bytes')
  with self.assertRaises(AssertionError):self.load()
 def test_wrong_archive_path(self):
  self.contract['historicalArchives'][0]['actualArchive']['path']='current.json'
  with self.assertRaises(AssertionError):self.load()
 def test_wrong_archive_sha(self):
  self.contract['historicalArchives'][0]['actualArchive']['sha256']='0'*64
  with self.assertRaises(AssertionError):self.load()
 def test_wrong_original_path_cannot_route(self):
  with self.assertRaises(AssertionError):H.exact_ref(self.root,dict(path='unknown.json',sha256=self.sha),self.load())
 def test_wrong_historical_sha_cannot_route(self):
  with self.assertRaises(AssertionError):H.exact_ref(self.root,dict(path='current.json',sha256='0'*64),self.load())
 def test_duplicate_route_rejected(self):
  self.contract['historicalArchives'].append(deepcopy(self.contract['historicalArchives'][0]))
  with self.assertRaises(AssertionError):self.load()
 def test_archive_traversal_rejected(self):
  self.contract['historicalArchives'][0]['actualArchive']['path']='../old.json'
  with self.assertRaises(AssertionError):self.load()
 def test_contract_hash_mismatch(self):
  self.load()
  with self.assertRaises(AssertionError):H.load_contract(self.root,'contract.json','0'*64)
 def test_live_bytes_cannot_be_relabelled_old(self):
  c=self.load();(self.root/'old.json').write_bytes((self.root/'current.json').read_bytes())
  with self.assertRaises(AssertionError):H.exact_ref(self.root,dict(path='current.json',sha256=self.sha),c)
if __name__=='__main__':unittest.main()
