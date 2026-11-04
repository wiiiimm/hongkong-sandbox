import unittest,hashlib
from diagnostic_plan_cli_preflight_v1_20261030 import ROOT,check

class PlanPreflight(unittest.TestCase):
 def plan(self,name):return ROOT/'docs/astra-city/government-import'/name
 def test_valid_view_plan_does_not_run_phase(self):
  manifest=ROOT/'3d-viewer/city/data/manifest.json';before=hashlib.sha256(manifest.read_bytes()).hexdigest()
  r=check(self.plan('government-xl-after-disneyland-piers-next-five-scope-views-plan-v2-20261030.json'))
  self.assertEqual(r['checkedPhases'],1);self.assertEqual(r['phaseCommandsExecuted'],0);self.assertEqual(r['leasesClaimed'],0);self.assertFalse(r['modelAcceptanceGranted']);self.assertEqual(before,hashlib.sha256(manifest.read_bytes()).hexdigest())
 def test_actual_bad_view_argument_rejected(self):
  with self.assertRaisesRegex(AssertionError,'unsupported arguments: --attributes'):check(self.plan('government-xl-after-disneyland-piers-next-five-safe-contacts-views-plan-v1-20261030.json'))
 def test_actual_duplicate_report_uids_rejected(self):
  with self.assertRaisesRegex(AssertionError,'Duplicate report UIDs'):check(self.plan('government-xl-after-disneyland-piers-academic309823-additive-followthrough-plan-v1-20261030.json'))
if __name__=='__main__':unittest.main()
