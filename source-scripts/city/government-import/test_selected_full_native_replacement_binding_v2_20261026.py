"""Reject lost retained coverage or unproven expanded replacement envelopes."""
import unittest
from copy import deepcopy
from selected_full_native_replacement_binding_v2_20261026 import validate_envelope

class ExpandedBindingTests(unittest.TestCase):
    def setUp(self):
        self.cells=[515,411,520,417]
        self.old=[516,411,520,416]
        self.proof=dict(coarseCells=self.cells,allRetainedRenderedFacesAndMultiplicityPreserved=True,allExtraFacesMatchProductionRoot=True,geometryChangesToCapturedSurface=0,completeCapturedFaces=100783,existingRenderedFaces=100763,exactAddedRootFaces=20)
    def test_accepted_exact_expansion(self):
        validate_envelope(self.cells,self.cells,self.old,self.proof)
    def test_unchanged_envelope_preserved(self):
        validate_envelope(self.old,self.old,self.old,{})
    def test_reject_incomplete_or_changed_evidence(self):
        for key,value in [('allRetainedRenderedFacesAndMultiplicityPreserved',False),('allExtraFacesMatchProductionRoot',False),('geometryChangesToCapturedSurface',1),('exactAddedRootFaces',0),('completeCapturedFaces',100784),('coarseCells',[516,411,520,417])]:
            with self.subTest(key=key):
                proof=deepcopy(self.proof);proof[key]=value
                with self.assertRaises(AssertionError):validate_envelope(self.cells,self.cells,self.old,proof)
    def test_reject_lost_old_coverage_or_wrong_scope(self):
        for cells,scope in [([517,411,520,417],[517,411,520,417]),(self.cells,[515,411,520,418])]:
            with self.subTest(cells=cells,scope=scope):
                with self.assertRaises(AssertionError):validate_envelope(cells,scope,self.old,self.proof)

if __name__=='__main__':unittest.main()
