"""Reject changed source metadata using the actual five-original browser fixture."""
import copy
import unittest
from run import ROOT, HERE, read
from original_candidate_atomic_catalogue_contract_v1_20261103 import verify

BASE = ROOT/'docs/astra-city/government-import'


class TestedOriginalCatalogue(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        selected = read(BASE/'government-xl-silvercord-lippo-five-original-floor-runtime-v1-20261103/selection.json.gz')['rows']
        cls.sources = {r['uid']:r['sourceSHA256'] for r in selected}
        cls.entries = {r['uid']:r['candidate']['entry'] for r in selected}
        cls.proposal = read(BASE/'government-xl-silvercord-lippo-private-dependency-proposal-v1-20261103/summary.json')
        cls.models = read(HERE/'local/government-xl-silvercord-lippo-private-six-part-browser-v4-20261103/catalogue.json')['models']
        cls.supports = cls.proposal['supportByUid']
        cls.owners = set(cls.sources)-set(cls.supports)

    def check(self, models):
        return verify(models, self.sources, self.supports, self.entries, self.owners)

    def test_exact_browser_metadata_preserved(self):
        models = copy.deepcopy(self.models)
        self.assertTrue(self.check(models))
        self.assertEqual(models, self.models)

    def test_source_pose_group_and_unknown_fields_rejected(self):
        for key, value in [('sha256','changed'), ('rootTranslation',[0,0,0]),
                           ('activationGroup',[]), ('verticalPlacementOffsetHKPD',1),
                           ('partialSource',True), ('surpriseField',True)]:
            models = copy.deepcopy(self.models); models[0][key] = value
            with self.assertRaises(AssertionError, msg=key): self.check(models)

    def test_wrong_missing_duplicate_or_fallback_support_rejected(self):
        for kind in ['state', 'uid', 'sha256', 'missing', 'duplicate']:
            models = copy.deepcopy(self.models)
            model = next(m for m in models if m['uid'] in self.supports)
            if kind == 'missing': model['supportDependencies'] = []
            elif kind == 'duplicate': model['supportDependencies'] *= 2
            else: model['supportDependencies'][0][kind] = 'fallback' if kind == 'state' else 'changed'
            with self.assertRaises(AssertionError, msg=kind): self.check(models)

    def test_duplicate_model_and_wrong_ground_owner_rejected(self):
        with self.assertRaises(AssertionError): self.check(self.models+[self.models[0]])
        with self.assertRaises(AssertionError):
            verify(self.models,self.sources,self.supports,self.entries,set(self.sources))


if __name__ == '__main__': unittest.main()
