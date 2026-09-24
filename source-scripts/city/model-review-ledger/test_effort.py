import contextlib,json,os,tempfile,unittest,uuid
from pathlib import Path
from unittest.mock import patch
import ledger

class EffortValidation(unittest.TestCase):
 def test_unknown_is_not_zero(self):
  self.assertEqual(ledger.effort_metadata()['reasoning_effort'],'unknown')
  self.assertNotIn('input_tokens',ledger.effort_metadata())
 def test_invalid_metadata(self):
  for value in ({'reasoning_effort':'high'},{'method':'epic'},{'input_tokens':-1},{'duration_seconds':True},{'secret':'x'}):
   with self.assertRaises(ValueError):ledger.effort_metadata(value)
 def test_distinct_method_and_reasoning(self):
  value=ledger.effort_metadata({'method':'lightweight','ai_model':'gpt-6-astra','reasoning_effort':'high'})
  self.assertEqual(value['method'],'lightweight')
  self.assertEqual(value['reasoning_effort'],'high')

@unittest.skipUnless(os.getenv('MODELLING_EFFORT_LIVE_TEST')=='1','Explicit rollback-only Neon test')
class EffortDatabase(unittest.TestCase):
 def test_atomic_history_retry_and_fencing(self):
  key='effort-fixture-'+uuid.uuid4().hex
  with ledger.connect() as con:
   with con.transaction(force_rollback=True):
    con.execute("INSERT INTO astra_modelling.model_reviews(snapshot_id,uid,landmark_ids,source_state,source_sha256,initial_evidence) VALUES(%s,%s,'[]','prepared','fixture-sha','{}')",(key,key))
    @contextlib.contextmanager
    def shared():yield con
    group={'owner':'rollback-test','token':uuid.uuid4(),'resources':['building:'+key]}
    with tempfile.TemporaryDirectory() as d,patch.object(ledger,'connect',shared),patch.object(ledger.reservations,'_current',return_value=group) as current:
     receipt=Path(d)/'receipt.json';receipt.write_text('{}')
     args=(key,receipt,key,'held',__file__,'Rollback-only effort fixture')
     first={'method':'lightweight','ai_model':'gpt-6-astra','reasoning_effort':'medium','issue':'HKS-224'}
     ledger.record(*args,effort=first,request_id=key)
     self.assertTrue(ledger.record(*args,effort=first,request_id=key)['reused'])
     with self.assertRaises(ValueError):ledger.record(*args,effort={'method':'detailed'},request_id=key)
     ledger.record(*args,effort={'method':'detailed'},request_id=key+'-2')
     events=ledger.history(key)['events'];self.assertEqual(len(events),2)
     self.assertEqual(events[0]['effort']['method'],'lightweight')
     self.assertEqual(events[1]['effort']['reasoning_effort'],'unknown')
     self.assertEqual(events[0]['result']['source_sha256'],'fixture-sha')
     current.return_value=None
     with self.assertRaises(ValueError):ledger.record(*args,effort=first)
   self.assertIsNone(con.execute('SELECT uid FROM astra_modelling.model_reviews WHERE uid=%s',(key,)).fetchone())

if __name__=='__main__':unittest.main()
