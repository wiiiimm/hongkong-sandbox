"""Recovery must never overwrite unexpected bytes or trust a changed backup."""
import tempfile,unittest
from pathlib import Path
from recover_original_publication_v1_20261023 import expected_states
from run import digest
class RecoveryByteFenceTests(unittest.TestCase):
 def fixture(self,root):
  (root/'archive').write_bytes(b'before');(root/'manifest').write_bytes(b'before')
  history=dict(mutableCurrentByteSnapshots=[dict(originalPath='manifest',originalSHA256=digest(b'before'),savedHistoricalBytes=dict(path='archive',sha256=digest(b'before')))],allMutableDestinations=['manifest','3d-viewer/city/catalogue.json','3d-viewer/city/assets/body.glb.gz'])
  plan=dict(after={'manifest':digest(b'after'),'3d-viewer/city/catalogue.json':digest(b'catalogue')});cat=dict(models=[dict(asset='assets/body.glb.gz',sha256=digest(b'body'))])
  return history,plan,cat
 def test_unchanged_destinations_and_absent_new_outputs(self):
  with tempfile.TemporaryDirectory()as tmp:
   r=Path(tmp);h,p,c=self.fixture(r);saved,actual=expected_states(r,h,p,c,'city/catalogue.json');self.assertEqual(saved['manifest'],b'before');self.assertIsNone(saved['3d-viewer/city/catalogue.json']);self.assertIsNone(actual['3d-viewer/city/assets/body.glb.gz'])
 def test_exact_partial_publication_is_recoverable(self):
  with tempfile.TemporaryDirectory()as tmp:
   r=Path(tmp);h,p,c=self.fixture(r);(r/'manifest').write_bytes(b'after');a=r/'3d-viewer/city/assets/body.glb.gz';a.parent.mkdir(parents=True);a.write_bytes(b'body');saved,actual=expected_states(r,h,p,c,'city/catalogue.json');self.assertEqual(saved['manifest'],b'before');self.assertEqual(actual[str(a.relative_to(r))],digest(b'body'))
 def test_foreign_destination_bytes_refused_without_mutation(self):
  with tempfile.TemporaryDirectory()as tmp:
   r=Path(tmp);h,p,c=self.fixture(r);(r/'manifest').write_bytes(b'another publication')
   with self.assertRaises(AssertionError):expected_states(r,h,p,c,'city/catalogue.json')
   self.assertEqual((r/'manifest').read_bytes(),b'another publication')
 def test_changed_historical_backup_refused(self):
  with tempfile.TemporaryDirectory()as tmp:
   r=Path(tmp);h,p,c=self.fixture(r);(r/'archive').write_bytes(b'corrupted backup')
   with self.assertRaises(AssertionError):expected_states(r,h,p,c,'city/catalogue.json')
   self.assertEqual((r/'manifest').read_bytes(),b'before')
if __name__=='__main__':unittest.main()
