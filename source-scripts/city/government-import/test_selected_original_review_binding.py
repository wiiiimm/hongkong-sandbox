import unittest
from copy import deepcopy
from selected_original_physical_review_v1 import validate_decision_binding

class ReviewBinding(unittest.TestCase):
    def fixture(self):
        raw=dict(uid='landsd/1:0',sourceSHA256='a'*64,sourceFormSHA256='b'*64,worldTrianglesSHA256='c'*64,passed=False,reasons=['full-source-target-coverage'])
        decision={k:raw[k]for k in ['uid','sourceSHA256','sourceFormSHA256','worldTrianglesSHA256']}
        decision.update(reviewer='ROOT',sourceIdentityInterpretationApproved=True,expectedRawReasons=raw['reasons'][:])
        return raw,decision
    def test_exact_decision(self):
        validate_decision_binding(*self.fixture())
    def test_changed_source_or_form_or_world_rejected(self):
        for key in ['sourceSHA256','sourceFormSHA256','worldTrianglesSHA256']:
            raw,decision=self.fixture();raw[key]='d'*64
            with self.assertRaises(AssertionError):validate_decision_binding(raw,decision)
    def test_unrelated_or_cell_failure_cannot_be_added_to_decision(self):
        for reason in ['full-source-unrelated-overlap','geographic-cell-proof:invalid']:
            raw,decision=self.fixture();raw['reasons'].append(reason);decision['expectedRawReasons']=raw['reasons'][:]
            with self.assertRaises(AssertionError):validate_decision_binding(raw,decision)
if __name__=='__main__':unittest.main()
