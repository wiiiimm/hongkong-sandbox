import unittest
from source_blocker_reason_families import reason_families

class ReasonFamilies(unittest.TestCase):
    def test_runtime_footprint_error_is_not_budget(self):
        self.assertEqual(reason_families(['runtime-original-footprint-fit-failed']),['identity-or-component-coverage'])
    def test_all_failures_remain_visible(self):
        self.assertEqual(reason_families(['terrain-intersects-source-over-0.5m','whole-source-foundation','terrain-regresses-neighbour:landsd/3:0']),['neighbour-impact','terrain-or-foundation'])
    def test_actual_budget(self):
        self.assertEqual(reason_families(['mobile-runtime-budget']),['runtime-budget'])
    def test_no_inferred_processing_owner(self):
        self.assertEqual(reason_families(['unrecognised-check-error']),['other-validation-failure'])
    def test_missing_identity_and_pending_approval(self):
        self.assertEqual(reason_families(['no-exact-current-component','pinned-government-source-member-absent-from-current-archive','metadata-restoration-pending-explicit-approval-after-auto-review-rejection']),['explicit-approval-pending','identity-or-component-coverage','missing-government-source'])

if __name__=='__main__':unittest.main()
