from copy import deepcopy
import unittest
from conditional_canopy_install_contract_v1_20261029 import form_sha
from test_conditional_canopy_install_contract_v1_20261029 import ContractTests
from multi_conditional_canopy_install_contract_v1_20261029 import verify


class MultiContractTests(unittest.TestCase):
    def setUp(self):
        f = ContractTests()
        f.setUp()
        self.models, self.review, self.physical, self.lifecycle, self.forms = f.models, f.review, f.physical, f.lifecycle, f.forms
        basic = 'landsd/3:0'
        self.forms[basic] = dict(self.forms[f.basic], uid=basic)
        replacements = [deepcopy(f.review['conditionalCanopyReplacement']) for _ in range(2)]
        replacements[1].update(basicUid=basic, basicFormSHA256=form_sha(self.forms[basic]))
        for review in [self.review, self.physical]:
            review.pop('conditionalCanopyReplacement')
            review['conditionalCanopyReplacements'] = deepcopy(replacements)
        self.features = [deepcopy(f.feature), {**deepcopy(f.feature), 'basicUid': basic, 'exactBasicForm': deepcopy(self.forms[basic])}]
        self.basics = [f.basic, basic]
        self.models[0]['suppressesBuildingUids'] = self.basics[:]
        for case in self.lifecycle['cases']:
            for row in case['canopyLifecycle']:
                visible = row.pop('basicCanopyVisible')
                row['canopies'] = [dict(uid=b, basicCanopyVisible=visible) for b in self.basics]

    def check(self):
        return verify(self.models, self.review, self.physical, self.lifecycle, self.features, self.forms)

    def test_exact_pair(self): self.assertTrue(self.check()['completeLifecycleVerified'])

    def test_hidden_extra_rejected(self):
        self.models[0]['suppressesBuildingUids'].append('landsd/4:0')
        with self.assertRaises(AssertionError): self.check()

    def test_changed_second_form_rejected(self):
        self.forms[self.basics[1]]['heightSource'] = 'surveyed'
        with self.assertRaises(AssertionError): self.check()

    def test_second_not_restored_rejected(self):
        self.lifecycle['cases'][0]['canopyLifecycle'][1]['canopies'][1]['basicCanopyVisible'] = False
        with self.assertRaises(AssertionError): self.check()

    def test_duplicate_canopy_rejected(self):
        self.lifecycle['cases'][0]['canopyLifecycle'][0]['canopies'][1]['uid'] = self.basics[0]
        with self.assertRaises(AssertionError): self.check()

    def test_missing_phase_rejected(self):
        self.lifecycle['cases'][1]['canopyLifecycle'].pop()
        with self.assertRaises(AssertionError): self.check()

    def test_missing_second_feature_rejected(self):
        self.features.pop()
        with self.assertRaises(AssertionError): self.check()

    def test_second_approval_absent_rejected(self):
        self.physical['conditionalCanopyReplacements'][1]['approved'] = False
        with self.assertRaises(AssertionError): self.check()


if __name__ == '__main__': unittest.main()
