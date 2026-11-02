"""Live review cannot silently award credit for missing or rejected exports."""
import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import june_garden_live_install_v1_20261103 as worker


class LiveReview(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name); self.doc = self.root/'live'; self.doc.mkdir()
        rows = []
        for index in range(300):
            name = str(index)+'.png'; (self.doc/name).write_bytes(b'unit-test-export-'+str(index).encode())
            rows.append(dict(file=name, time='15:00'))
        atomic = self.doc/'atomic-live'; atomic.mkdir()
        for index in range(7): (atomic/(str(index)+'.png')).write_bytes(b'unit-test-atomic-'+str(index).encode())
        self.report = dict(views=rows[:24], retainedNativeOwnViews=rows[24:])
        self.images = [dict(path=str(p.relative_to(self.root)), sha256=hashlib.sha256(p.read_bytes()).hexdigest())
                       for p in self.doc.rglob('*.png')]
        self.inspection = dict(reviewer='ROOT', allListedExportsActuallyInspected=True, visualAcceptance=True,
            unresolvedVisualFailures=[], inspectionScope='complete-source-and-retained-desktop-mobile-exports',
            images=self.images)
        self.file = self.doc/'ROOT-LIVE-EXPORT-INSPECTION.json'
        self.root_patch = patch.object(worker, 'ROOT', self.root); self.root_patch.start(); self.addCleanup(self.root_patch.stop)
        self.guard_root_patch = patch.object(worker.guard, 'ROOT', self.root); self.guard_root_patch.start(); self.addCleanup(self.guard_root_patch.stop)
        self.doc_patch = patch.object(worker, 'DOC', self.doc); self.doc_patch.start(); self.addCleanup(self.doc_patch.stop)
        self.lease_patch = patch.object(worker.reservations, 'owns', return_value=True); self.lease_patch.start(); self.addCleanup(self.lease_patch.stop)

    def run_review(self):
        self.file.write_text(json.dumps(self.inspection))
        return worker.wait_for_root_inspection(self.report, {})

    def test_complete_hash_bound_actual_review(self):
        self.assertEqual(self.run_review()['path'], 'live/ROOT-LIVE-EXPORT-INSPECTION.json')

    def test_missing_review_times_out_without_acceptance(self):
        with patch.object(worker.time, 'monotonic', side_effect=[0, 1801]):
            with self.assertRaises(TimeoutError): worker.wait_for_root_inspection(self.report, {})
        self.assertFalse(self.file.exists())

    def test_unresolved_visual_failure(self):
        self.inspection['unresolvedVisualFailures'] = ['target not visible']
        with self.assertRaises(AssertionError): self.run_review()

    def test_partial_inspection(self):
        self.inspection['images'] = self.images[:-1]
        with self.assertRaises(AssertionError): self.run_review()

    def test_changed_export_since_review(self):
        (self.root/self.images[0]['path']).write_bytes(b'changed-after-inspection')
        with self.assertRaises(AssertionError): self.run_review()

    def test_lost_lease(self):
        with patch.object(worker.reservations, 'owns', return_value=False):
            with self.assertRaises(AssertionError): self.run_review()


class AtomicGroup(unittest.TestCase):
    def setUp(self):
        sources = [dict(uid=u, sha256=s) for u,s in worker.stage.SOURCES.items()]
        self.report = dict(passed=True, pageErrors=[], cases=[dict(failedUid=u, width=390 if u else 1280,
            baseOnlyRestoredCompleteGroup=True, completeGroupEvicted=True,
            failureKeptAllBasics=bool(u), audit=dict(violations=[]), sources=copy.deepcopy(sources))
            for u in [None, *worker.stage.SOURCES]])

    def test_each_peer_failure_and_full_group(self):
        self.assertTrue(worker.verify_atomic(self.report))

    def test_missing_peer_failure(self):
        self.report['cases'].pop()
        with self.assertRaises(AssertionError): worker.verify_atomic(self.report)

    def test_partial_native_activation(self):
        self.report['cases'][0]['audit']['violations'] = ['partial-native-group']
        with self.assertRaises(AssertionError): worker.verify_atomic(self.report)


if __name__ == '__main__': unittest.main()
