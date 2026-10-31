"""Retry changes only attempt paths and the device-specific selection policy."""
import unittest
from unittest.mock import patch
import north_pair_live_install_v2_20261028 as retry

class RetryPolicy(unittest.TestCase):
 def test_only_attempt_paths_and_device_policy_change(self):
  old=(retry.HERE/'north_pair_live_install_v1_20261027.py').read_text()
  new=(retry.HERE/'north_pair_live_install_v2_20261028.py').read_text()
  new=new.replace('north_pair_guarded_publish_v2_20261028','north_pair_guarded_publish_v1_20261027').replace("keepSelectedForRetainedCapture=['landsd/160070:0'] if width==390 else []","keepSelectedForRetainedCapture=['landsd/160070:0']")
  self.assertEqual(old,new)
 def test_mobile_keeps_real_selection_and_fallback_assertions(self):
  with patch.object(retry,'read',return_value={}),patch.object(retry,'retained_uids',return_value=['peer']):
   self.assertEqual(retry.browser_config(390)['keepSelectedForRetainedCapture'],['landsd/160070:0'])
   self.assertEqual(retry.browser_config(1280)['keepSelectedForRetainedCapture'],[])
  self.assertEqual(retry.BROWSER.name,'ronsdale_three_live_browser_v20_20261027.mjs')
 def test_publisher_only_attempt_namespace_changes(self):
  old=(retry.HERE/'north_pair_guarded_publish_v1_20261027.py').read_text()
  new=(retry.HERE/'north_pair_guarded_publish_v2_20261028.py').read_text().replace('original-installed-v2-20261028','original-installed-v1-20261027')
  self.assertEqual(old,new)

if __name__=='__main__': unittest.main()
