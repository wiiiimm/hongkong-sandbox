"""Hermetic captured own-pending phase adversaries; no mocked live replay."""
import copy
import unittest
from run import ROOT, read
from lippo_exact_own_pending_preapply_phase_guard_v1_20261011 import verify

CAPTURE = ROOT / 'docs/astra-city/government-import/government-xl-lippo-exact-preapply-pending-attempt-context-v1-20261011/capture.json.gz'

class PendingAttemptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.context = read(CAPTURE)

    def run_guard(self, c):
        return verify(c, c['liveReadOnlyNeonRows']['model_reviews'],
                      c['liveReadOnlyNeonRows']['model_review_events'],
                      c['exactLiveFiles'], c['fixtureFiles'])

    def reject(self, mutate):
        c = copy.deepcopy(self.context); mutate(c)
        with self.assertRaises((AssertionError, KeyError, ValueError, TypeError)):
            self.run_guard(c)

    def test_exact_own_pending_attempt(self):
        self.assertTrue(self.run_guard(self.context)['exactOwnApprovedPendingAttemptRecognised'])

    def test_empty_review_absence_not_resume(self):
        self.reject(lambda c: c['liveReadOnlyNeonRows']['model_reviews'].clear())
    def test_duplicate_review(self):
        self.reject(lambda c: c['liveReadOnlyNeonRows']['model_reviews'].append(copy.deepcopy(c['liveReadOnlyNeonRows']['model_reviews'][0])))
    def test_additional_event(self):
        self.reject(lambda c: c['liveReadOnlyNeonRows']['model_review_events'].append(copy.deepcopy(c['liveReadOnlyNeonRows']['model_review_events'][0])))
    def test_missing_event(self):
        self.reject(lambda c: c['liveReadOnlyNeonRows']['model_review_events'].clear())
    def test_wrong_uid(self):
        self.reject(lambda c: c.update(uid='landsd/231645:0'))
    def test_wrong_source(self):
        self.reject(lambda c: c.update(sourceSHA256='0'*64))
    def test_wrong_snapshot(self):
        self.reject(lambda c: c.update(snapshotId='0'*16))
    def test_installed_review(self):
        self.reject(lambda c: c['liveReadOnlyNeonRows']['model_reviews'][0].update(review_state='installed-verified'))
    def test_installed_event(self):
        self.reject(lambda c: c['liveReadOnlyNeonRows']['model_review_events'][0].update(review_state='installed-verified'))
    def test_other_request(self):
        self.reject(lambda c: c['liveReadOnlyNeonRows']['model_review_events'][0].update(request_id='other'))
    def test_other_event(self):
        self.reject(lambda c: c['liveReadOnlyNeonRows']['model_review_events'][0].update(id=11923))
    def test_other_owner(self):
        self.reject(lambda c: c['liveReadOnlyNeonRows']['model_review_events'][0].update(owner='other'))
    def test_other_token(self):
        self.reject(lambda c: c['liveReadOnlyNeonRows']['model_review_events'][0].update(token='00000000-0000-0000-0000-000000000000'))
    def test_current_manifest_drift(self):
        self.reject(lambda c: c['exactLiveFiles']['manifest'].update(sha256='0'*64))
    def test_other_evidence_file(self):
        self.reject(lambda c: c['exactLiveFiles']['attemptAcceptance'].update(path='docs/other.json'))
    def test_changed_approval_bytes(self):
        self.reject(lambda c: c['exactLiveFiles']['attemptAcceptance'].update(sha256='0'*64))
    def test_pointer_already_advanced(self):
        self.reject(lambda c: c['fixtureFiles']['pointer'].update(snapshotId='8d35b6f1d6f6bcdc'))
    def test_attempt_already_published(self):
        self.reject(lambda c: c['fixtureFiles']['attemptAcceptance'].update(publication=True))
    def test_attempt_installed_credit(self):
        self.reject(lambda c: c['fixtureFiles']['attemptAcceptance'].update(newlyInstalled=1))
    def test_attempt_geometry_edit(self):
        self.reject(lambda c: c['fixtureFiles']['attemptAcceptance'].update(modelGeometryChanges=1))
    def test_current_role_not_physical(self):
        self.reject(lambda c: c['fixtureFiles']['completeRole'].update(physicalAccepted=False))
    def test_stage_browser_failure(self):
        self.reject(lambda c: c['fixtureFiles']['stageAcceptance'].update(failures=['collision']))
    def test_inventory_source_changed(self):
        self.reject(lambda c: next(p for p in c['fixtureFiles']['pendingInventory']['parts'] if p['uid']=='landsd/239465:0')['candidate'].update(sha256='0'*64))
    def test_inventory_old_actor_changed(self):
        self.reject(lambda c: c['fixtureFiles']['pendingInventory']['parts'][0].update(name='other'))
    def test_inventory_reordered(self):
        self.reject(lambda c: c['fixtureFiles']['pendingInventory']['parts'].reverse())
    def test_snapshot_hash_not_recomputable(self):
        self.reject(lambda c: c['fixtureFiles']['attemptAcceptance'].update(qualification='mutated'))

if __name__ == '__main__':
    unittest.main()
