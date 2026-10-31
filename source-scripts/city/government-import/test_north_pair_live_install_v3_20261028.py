"""Exact replay fails closed; original installation and publisher guards remain intact."""
import unittest
from unittest.mock import patch
from pathlib import Path
import north_pair_live_install_v3_20261028 as retry
import north_pair_completed_views_reuse_v1_20261028 as reuse
class ReplayTests(unittest.TestCase):
 def test_changed_public_byte_rejected(self):
  with self.assertRaises(AssertionError):reuse.assert_exact_hash_map({'a':'old'},{'a':'new'})
 def test_missing_public_file_rejected(self):
  with self.assertRaises(AssertionError):reuse.assert_exact_hash_map({'a':'x','b':'y'},{'a':'x'})
 def test_exact_public_replay(self):reuse.assert_exact_hash_map({'a':'x'},{'a':'x'})
 def test_joint_config_requests_both_sources_without_repeating_retained(self):
  cfg=reuse.joint_config({'additionalRetainedUids':['peer'],'failureTestUids':[]},{'two':'hash','one':'hash'})
  self.assertEqual(cfg['jointUids'],['one','two']);self.assertEqual(cfg['additionalRetainedUids'],[]);self.assertTrue(cfg['fitJointCameraMobile'])
 def test_missing_joint_evidence_remains_failure(self):
  with patch.object(reuse,'verify_republished_inputs',return_value={}):
   with self.assertRaises(AssertionError):reuse.combine(390,dict(passed=True,errors=[],views=[dict(time='x')]*4,jointViews=[]),Path('/tmp/unused'))
 def test_original_installer_guards_unchanged(self):
  old=(retry.HERE/'north_pair_live_install_v2_20261028.py').read_text();new=(retry.HERE/'north_pair_live_install_v3_20261028.py').read_text()
  new=new.replace('north_pair_guarded_publish_v3_20261028','north_pair_guarded_publish_v2_20261028').replace('\nimport north_pair_completed_views_reuse_v1_20261028 as completed','').replace(' return completed.joint_config(cfg,stage.SOURCES)',' return cfg').replace(' completed.archive_refs()\n','').replace(' paths.extend(completed.archive_refs())\n','').replace('   completed.verify_republished_inputs()\n   refs.extend(ref(p)for p in completed.archive_refs())\n','').replace("fresh=read(subdir/'live-browser.json');part=completed.combine(width,fresh,subdir)","part=read(subdir/'live-browser.json')")
  self.assertEqual(new,old)
 def test_publisher_only_changes_attempt_namespace(self):
  old=(retry.HERE/'north_pair_guarded_publish_v2_20261028.py').read_text();new=(retry.HERE/'north_pair_guarded_publish_v3_20261028.py').read_text().replace('original-installed-v3-20261028','original-installed-v2-20261028');self.assertEqual(new,old)
if __name__=='__main__':unittest.main()
