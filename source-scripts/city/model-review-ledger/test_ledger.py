import json,os,tempfile,unittest,uuid
from pathlib import Path
import ledger
class ValidationTests(unittest.TestCase):
 def test_reject_unknown_state_before_database(self):
  with self.assertRaises(ValueError):ledger.record('fixture','missing','uid','done','missing','x')
 def test_reject_external_evidence_before_database(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);(p/'receipt').write_text('{}');(p/'evidence').write_text('fixture')
   with self.assertRaises(ValueError):ledger.record('fixture',p/'receipt','uid','held',p/'evidence','x')
@unittest.skipUnless(os.getenv('MODELLING_INTEGRATION_TEST')=='1','Explicit live fixture test')
class NeonTests(unittest.TestCase):
 def test_idempotent_seed_and_live_reservation_fencing(self):
  snapshot='review-test-'+uuid.uuid4().hex;uid='landsd/'+str(uuid.uuid4().int)+':0'
  part={'uid':uid,'sourceProgress':'prepared-for-review','candidate':{'sha256':'test-fixture'},'name':'TEST FIXTURE','landmarkIds':[],'classification':[],'knownHold':None,'objectId':None}
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);report=p/'report.json';report.write_text(json.dumps({'snapshotId':snapshot,'parts':[part]}))
   ledger.seed(report);self.assertEqual(ledger.seed(report)['states'],{'pending':1})
   claim=ledger.reservations.claim(snapshot,['building:'+uid]);receipt=claim['reservation'];(p/'receipt').write_text(json.dumps(receipt,default=str))
   try:
    self.assertEqual(ledger.summary(snapshot)['states'],{'in-progress':1})
    ledger.record(snapshot,p/'receipt',uid,'held',__file__,'Test fixture; not a real model review')
    self.assertEqual(ledger.summary(snapshot)['states'],{'held':1})
    # Source decisions carry over only when the immutable asset identity agrees.
    inherited=snapshot+'-same';report.write_text(json.dumps({'snapshotId':inherited,'parts':[part]}))
    self.assertEqual(ledger.seed(report,inherit=snapshot)['states'],{'held':1})
    changed=snapshot+'-changed';replacement={**part,'candidate':{'sha256':'changed-fixture'}}
    report.write_text(json.dumps({'snapshotId':changed,'parts':[replacement]}))
    self.assertEqual(ledger.seed(report,inherit=snapshot)['states'],{'in-progress':1})
    self.assertEqual(ledger.summary(snapshot)['states'],{'held':1})
    with self.assertRaises(ValueError):ledger.record_many(snapshot,p/'receipt',[(uid,'installed-verified',__file__,'Atomic fixture',None),('landsd/0:0','held',__file__,'Unowned fixture',None)])
    self.assertEqual(ledger.summary(snapshot)['states'],{'held':1})
    ledger.reservations.release(receipt)
    with self.assertRaises(ValueError):ledger.record(snapshot,p/'receipt',uid,'held',__file__,'Stale fixture owner')
   finally:ledger.reservations.release(receipt)
if __name__=='__main__':unittest.main()
