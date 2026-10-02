import importlib.util
from pathlib import Path
import unittest
spec=importlib.util.spec_from_file_location('joint_diagnostic',Path(__file__).with_name('xl-yoho-mall-ii-acceptance.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class JointDiagnosticTests(unittest.TestCase):
    def setUp(self):m.PREPARE_MULTIPLE=False
    def test_default_rejects_multiple_components(self):
        with self.assertRaises(AssertionError):m.validate_diagnostic_scope(['a','b'],{'a':1,'b':1},{'a':1,'b':1},True)
    def test_explicit_prepare_opt_in_accepts_complete_pair(self):
        m.PREPARE_MULTIPLE=True;m.validate_diagnostic_scope(['a','b'],{'a':1,'b':1},{'a':1,'b':1},True)
    def test_opt_in_never_expands_publication_scope(self):
        m.PREPARE_MULTIPLE=True
        with self.assertRaises(AssertionError):m.validate_diagnostic_scope(['a','b'],{'a':1,'b':1},{'a':1,'b':1},False)
    def test_duplicate_or_missing_context_rejected(self):
        m.PREPARE_MULTIPLE=True
        for ids,ctx in [(['a','a'],{'a':1}),(['a','b'],{'a':1})]:
            with self.assertRaises(AssertionError):m.validate_diagnostic_scope(ids,{'a':1,'b':1},ctx,True)
if __name__=='__main__':unittest.main()
