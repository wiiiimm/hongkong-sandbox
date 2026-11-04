import unittest
from standalone_original_scope_v1_20261024 import SOURCES,verify_entry


class StandaloneScope(unittest.TestCase):
    def setUp(self):self.entry={'uid':'landsd/93417:0','sha256':SOURCES['landsd/93417:0']}
    def test_exact_original_without_dependencies(self):verify_entry(self.entry,SOURCES)
    def test_different_original_is_rejected(self):
        for changes in [{'uid':'landsd/6801:0'},{'sha256':'0'*64}]:
            with self.subTest(changes=changes),self.assertRaises(AssertionError):verify_entry({**self.entry,**changes},SOURCES)
    def test_different_approval_scope_is_rejected(self):
        with self.assertRaises(AssertionError):verify_entry(self.entry,{**SOURCES,'landsd/6801:0':'1'*64})
    def test_no_dependency_state_can_be_hidden(self):
        for key in ['supportDependencies','retainedBasicSupportDependencies']:
            for state in ['candidate','installed','fallback','surveyed-footprint-fallback']:
                with self.subTest(key=key,state=state),self.assertRaises(AssertionError):verify_entry({**self.entry,key:[{'uid':'landsd/45779:0','state':state}]},SOURCES)
    def test_malformed_dependencies_are_rejected(self):
        for value in [{},None,False,'']:
            with self.subTest(value=value),self.assertRaises(AssertionError):verify_entry({**self.entry,'supportDependencies':value},SOURCES)
    def test_suppression_partial_or_replacement_geometry_is_rejected(self):
        for changes in [{'suppressesBuildingUids':['landsd/121501:0']},{'footprintScope':{'uids':['landsd/121501:0']}},{'embeddedGeometry':{'position':[0,0,0]}}]:
            with self.subTest(changes=changes),self.assertRaises(AssertionError):verify_entry({**self.entry,**changes},SOURCES)

if __name__=='__main__':unittest.main()
