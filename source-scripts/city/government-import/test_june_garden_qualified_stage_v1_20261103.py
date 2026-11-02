"""Reject incomplete or stale visual evidence before creating a qualified stage."""
import copy
import tempfile
import unittest
from pathlib import Path
from run import digest
from june_garden_qualified_stage_v1_20261103 import inspected_exports


class ExportEvidence(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);(self.root/'capture.png').write_bytes(b'actual captured bytes')
        self.expected={'capture.png':digest((self.root/'capture.png').read_bytes())}
        self.inspection=dict(allListedExportsActuallyInspected=True,
            inspectionScope='complete-source-and-retained-desktop-mobile-exports',
            images=[dict(path=p,sha256=s) for p,s in self.expected.items()])
    def test_exact_inspected_bytes(self):
        inspected_exports(self.inspection,self.expected,self.root)
    def test_partial_inspection_rejected(self):
        self.inspection['inspectionScope']='partial-source-exports'
        with self.assertRaises(AssertionError):inspected_exports(self.inspection,self.expected,self.root)
    def test_uninspected_exports_rejected(self):
        self.inspection['allListedExportsActuallyInspected']=False
        with self.assertRaises(AssertionError):inspected_exports(self.inspection,self.expected,self.root)
    def test_missing_export_rejected(self):
        self.expected['missing.png']='missing'
        with self.assertRaises(AssertionError):inspected_exports(self.inspection,self.expected,self.root)
    def test_changed_capture_rejected(self):
        (self.root/'capture.png').write_bytes(b'different capture')
        with self.assertRaises(AssertionError):inspected_exports(self.inspection,self.expected,self.root)
    def test_duplicate_cannot_replace_missing_export(self):
        self.expected['second.png']='other'
        self.inspection['images'].append(copy.deepcopy(self.inspection['images'][0]))
        with self.assertRaises(AssertionError):inspected_exports(self.inspection,self.expected,self.root)


if __name__=='__main__':unittest.main()
