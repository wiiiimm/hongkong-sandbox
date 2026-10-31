"""Exercise restoration of actual files without touching the public viewer."""
import tempfile,unittest
from pathlib import Path
import esplanade_original_live_install_v1_20261015 as installer

class RollbackTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.original=installer.ROOT;installer.ROOT=Path(self.temp.name)
 def tearDown(self):
  installer.ROOT=self.original;self.temp.cleanup()
 def test_restore_replaced_and_remove_new_files(self):
  root=installer.ROOT;(root/'3d-viewer/city/data').mkdir(parents=True)
  manifest='3d-viewer/city/data/manifest.json'
  for path in ['existing.bin','new.bin',manifest]:(root/path).write_bytes(b'changed')
  self.assertEqual(installer.restore({'existing.bin':b'old asset','new.bin':None,manifest:b'old manifest'}),[])
  self.assertEqual((root/'existing.bin').read_bytes(),b'old asset');self.assertFalse((root/'new.bin').exists());self.assertEqual((root/manifest).read_bytes(),b'old manifest')
 def test_rollback_failure_is_reported(self):
  (installer.ROOT/'directory').mkdir();errors=installer.restore({'directory':None})
  self.assertEqual(len(errors),1);self.assertEqual(errors[0]['path'],'directory')
if __name__=='__main__':unittest.main()
