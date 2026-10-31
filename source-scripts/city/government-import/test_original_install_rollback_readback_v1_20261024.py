import copy,hashlib,tempfile,unittest
from pathlib import Path
from original_install_rollback_readback_v1_20261024 import verify

class RollbackTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.addCleanup(self.tmp.cleanup)
        for name in ['old','saved']:(self.root/name).write_bytes(b'original')
        sha=hashlib.sha256(b'original').hexdigest();self.history=dict(allMutableDestinations=['old','new'],mutableCurrentByteSnapshots=[dict(originalPath='old',originalSHA256=sha,savedHistoricalBytes=dict(path='saved',sha256=sha))]);self.failure=dict(allPublicDestinationsRestored=True,currentPointerRestoredNotDerivedCredit=True,derivedInstalledReviewHistoryRetained=False,rollbackErrors=[])
    def test_all_actual_states_read_back(self):self.assertEqual(len(verify(self.root,self.failure,self.history)),2)
    def rejects(self):
        with self.assertRaises(AssertionError):verify(self.root,self.failure,self.history)
    def test_changed_current_bytes(self):(self.root/'old').write_bytes(b'changed');self.rejects()
    def test_unremoved_new_asset(self):(self.root/'new').write_bytes(b'residue');self.rejects()
    def test_changed_historical_bytes(self):(self.root/'saved').write_bytes(b'changed');self.rejects()
    def test_installed_history_blocks_retry(self):self.failure['derivedInstalledReviewHistoryRetained']=True;self.rejects()
    def test_duplicate_destinations(self):self.history['allMutableDestinations'].append('old');self.rejects()
    def test_path_escape(self):self.history['allMutableDestinations'].append('../escaped');self.rejects()

if __name__=='__main__':unittest.main()
