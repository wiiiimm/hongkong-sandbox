import unittest
from copy import deepcopy
from pathlib import Path
import lippo_exact_pending_predecessor_routing_copies_v1_20261011 as m
ROOT=Path(__file__).resolve().parents[3]
class Copies(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.raw=(ROOT/m.CAPTURE_PATH).read_bytes();cls.oldraw=(ROOT/m.PREVIOUS_PATH).read_bytes();cls.newraw=(ROOT/m.PENDING_PATH).read_bytes()
  cls.bound=m.BoundRoutingCopies(cls.raw,cls.oldraw,cls.newraw)
 def fixtures(self):return deepcopy(self.bound.context),deepcopy(self.bound.previous),deepcopy(self.bound.pending)
 def bad(self,change):
  c,a,b=self.fixtures();change(c,a,b)
  with self.assertRaises((AssertionError,KeyError)):m.verify_copies(c,a,b)
 def test_actual_full_duplicate_contract(self):
  p=self.bound.proof();self.assertEqual(p['completeOldRecordsExactlyPreserved'],4944);self.assertEqual(p['newNumericGeometryExclusions'],0)
 def test_all_old_rows_bound(self):
  for p in self.bound.pointers:self.assertTrue(self.bound.verify_value(m.CAPTURE_PATH,p,m.at(self.bound.context,p))['completeDuplicateRoutingRowVerified'])
 def test_new_row_recursive(self):self.assertFalse(self.bound.handles(m.CAPTURE_PATH,self.bound.proof()['newCandidatePointer']))
 def test_current_role_recursive(self):self.assertFalse(self.bound.handles(m.CAPTURE_PATH,'/fixtureFiles/completeRole'))
 def test_stage_recursive(self):self.assertFalse(self.bound.handles(m.CAPTURE_PATH,'/fixtureFiles/stageAcceptance'))
 def test_unknown_old_subpointer_recursive(self):self.assertFalse(self.bound.handles(m.CAPTURE_PATH,'/fixtureFiles/previousInventory/parts/0/candidate'))
 def test_other_document_recursive(self):self.assertFalse(self.bound.handles('other.json','/fixtureFiles/previousInventory/parts/0'))
 def test_changed_old_record(self):self.bad(lambda c,a,b:a['parts'][0].update(name='changed'))
 def test_changed_old_pending_record(self):self.bad(lambda c,a,b:b['parts'][0].update(name='changed'))
 def test_missing_old_record(self):self.bad(lambda c,a,b:a['parts'].pop())
 def test_pending_removed_record(self):self.bad(lambda c,a,b:b['parts'].pop())
 def test_duplicate_uid(self):self.bad(lambda c,a,b:b['parts'].append(deepcopy(b['parts'][0])))
 def test_reordered_pending_records(self):self.bad(lambda c,a,b:b['parts'].reverse())
 def test_unknown_top_field(self):self.bad(lambda c,a,b:b.update(geometry=[1,2,3]))
 def test_changed_snapshot(self):self.bad(lambda c,a,b:b.update(snapshotId='other'))
 def test_changed_source_pin(self):self.bad(lambda c,a,b:c['exactLiveFiles']['previousInventory'].update(sha256='0'*64))
 def test_new_source_wrong_sha(self):self.bad(lambda c,a,b:next(r for r in b['parts'] if r['uid']==m.NEW_UID)['candidate'].update(sha256='0'*64))
 def test_new_source_extra_geometry(self):self.bad(lambda c,a,b:next(r for r in b['parts'] if r['uid']==m.NEW_UID).update(position=[1,2,3]))
 def test_new_source_installed_claim(self):self.bad(lambda c,a,b:next(r for r in b['parts'] if r['uid']==m.NEW_UID).update(sourceProgress='installed'))
 def test_changed_captured_duplicate(self):self.bad(lambda c,a,b:c['fixtureFiles']['pendingInventory']['parts'][0].update(name='changed'))
 def test_wrong_value_at_permitted_pointer(self):
  p=next(iter(self.bound.pointers));v=deepcopy(m.at(self.bound.context,p));v['name']='different'
  with self.assertRaises(AssertionError):self.bound.verify_value(m.CAPTURE_PATH,p,v)
 def test_raw_capture_mutation(self):
  with self.assertRaises(AssertionError):m.BoundRoutingCopies(self.raw+b' ',self.oldraw,self.newraw)
 def test_raw_previous_mutation(self):
  with self.assertRaises(AssertionError):m.BoundRoutingCopies(self.raw,self.oldraw+b' ',self.newraw)
 def test_raw_pending_mutation(self):
  with self.assertRaises(AssertionError):m.BoundRoutingCopies(self.raw,self.oldraw,self.newraw+b' ')
if __name__=='__main__':unittest.main()
