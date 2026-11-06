"""Exact visual reuse rejects stale, unviewed and different-subject evidence."""
import unittest
from pathlib import Path
from unittest.mock import patch
import islands_delivery_check as check


class VisualReuseTests(unittest.TestCase):
    def setUp(self):
        self.doc = Path('/tmp/islands-visual-reuse-fixture')
        self.subject = dict(uid='landsd/1:0', width=390, time='15:00',
                            sourceSHA256='source', originalTriangles=12)
        self.old = dict(self.subject, file='staged.png')
        self.new = dict(self.subject, file='live.png')
        self.inspection = dict(actuallyViewed=True, renderingAccepted=True,
            stagedBrowserSHA256='report', images=[dict(path='staged.png', sha256='pixels')])

    def run_reuse(self, new=None, changed=False):
        def read(path):
            return self.inspection if path.name == 'staged-inspection.json' else {'views': [self.old]}
        def sha(path):
            if path.name == 'solid-staged-browser.json': return 'report'
            if path.name == 'staged-inspection.json': return 'inspection'
            return 'changed' if changed and path.name == 'live.png' else 'pixels'
        with patch.object(Path, 'exists', return_value=True), patch.object(check, 'read', side_effect=read), \
             patch.object(check, 'sha', side_effect=sha), patch.object(check, 'rel', side_effect=lambda p: p.name):
            return check.exact_visual_reuse(self.doc, [new or self.new])

    def test_same_bytes_and_subject_reuse(self):
        changed, reused = self.run_reuse()
        self.assertEqual(changed, []); self.assertEqual(len(reused), 1)

    def test_changed_bytes_require_viewing(self):
        changed, reused = self.run_reuse(changed=True)
        self.assertEqual(changed, [self.new]); self.assertEqual(reused, [])

    def test_every_subject_field_is_required(self):
        for key in self.subject:
            with self.subTest(key=key):
                self.assertFalse(check.same_visual_subject(self.subject, {k: v for k, v in self.subject.items() if k != key}))
                self.assertFalse(check.same_visual_subject(self.subject, dict(self.subject, **{key: 'different'})))

    def test_equal_pixels_different_source_requires_viewing(self):
        changed, reused = self.run_reuse(dict(self.new, sourceSHA256='different'))
        self.assertEqual(len(changed), 1); self.assertEqual(reused, [])

    def test_unviewed_or_unaccepted_evidence_rejected(self):
        for key in ('actuallyViewed', 'renderingAccepted'):
            with self.subTest(key=key):
                self.inspection[key] = False
                with self.assertRaises(AssertionError): self.run_reuse()
                self.inspection[key] = True

    def test_stale_report_or_image_rejected(self):
        self.inspection['stagedBrowserSHA256'] = 'stale'
        with self.assertRaises(AssertionError): self.run_reuse()
        self.inspection['stagedBrowserSHA256'] = 'report'
        self.inspection['images'][0]['sha256'] = 'stale'
        with self.assertRaises(AssertionError): self.run_reuse()


if __name__ == '__main__': unittest.main()
