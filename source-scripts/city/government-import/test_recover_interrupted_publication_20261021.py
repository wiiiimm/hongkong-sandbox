import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import recover_interrupted_publication_20261021 as recovery

class RecoveryTests(unittest.TestCase):
 def fixture(self,root):
  doc=root/'evidence';prep=root/'prep';doc.mkdir();prep.mkdir();(root/'manifest.json').write_text('new');(root/'original.json').write_text('old');(root/'asset').write_text('asset')
  sha=lambda p:recovery.digest((root/p).read_bytes())
  (doc/'historical-input-context.json').write_text(json.dumps({'preInstallSnapshot':'before','mutableCurrentByteSnapshots':[{'originalPath':'manifest.json','originalSHA256':sha('original.json'),'savedHistoricalBytes':{'path':'original.json'}}]}))
  (prep/'publication-plan.json').write_text(json.dumps({'edits':[{'destination':'manifest.json','source':{'sha256':sha('manifest.json')}}],'assets':[{'destination':'asset','source':{'sha256':sha('asset')}}]}))
  return doc,prep
 def run_case(self,changed=False):
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder);doc,prep=self.fixture(root)
   if changed:(root/'manifest.json').write_text('someone else')
   with patch.object(recovery.reservations,'claim',return_value={'ok':True,'reservation':{}}),patch.object(recovery.reservations,'owns',return_value=True),patch.object(recovery.reservations,'release',return_value={'ok':True}):
    if changed:
     with self.assertRaises(AssertionError):recovery.recover(root,root,doc,prep,['test'])
     self.assertEqual((root/'manifest.json').read_text(),'someone else');self.assertTrue((root/'asset').exists())
    else:
     recovery.recover(root,root,doc,prep,['test']);self.assertEqual((root/'manifest.json').read_text(),'old');self.assertFalse((root/'asset').exists());self.assertTrue(json.loads((doc/'supervisor-recovery.json').read_text())['allPublicDestinationsRestored'])
 def test_exact_interrupted_publication_is_restored(self):self.run_case()
 def test_unexpected_mutation_is_not_overwritten(self):self.run_case(True)
if __name__=='__main__':unittest.main()
