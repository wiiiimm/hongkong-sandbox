from copy import deepcopy
import unittest
from private_multi_canopy_preview_catalogue_v1_20261029 import apply
from test_private_canopy_preview_catalogue_v1_20261029 import PreviewTests


class MultiPreviewTests(unittest.TestCase):
    def setUp(self):
        fixture = PreviewTests()
        fixture.setUp()
        self.models, self.sources, self.forms = fixture.models, fixture.sources, fixture.forms
        self.forms['landsd/3:0'] = dict(self.forms['landsd/2:0'], uid='landsd/3:0')
        self.reviews = [deepcopy(fixture.review), deepcopy(fixture.review)]
        for review in self.reviews:
            review['currentManifest'] = dict(path='manifest.json', sha256='c' * 64)
        second = self.reviews[1]
        second['basicUid'] = 'landsd/3:0'
        second['exactBasicForm'] = deepcopy(self.forms['landsd/3:0'])
        second['proposedSuppression']['suppressesBuildingUids'] = ['landsd/3:0']

    def check(self):
        return apply(self.models, self.sources, self.forms, self.reviews)

    def test_only_two_verified_ids_added(self):
        before = deepcopy(self.models)
        out = self.check()
        self.assertEqual(out[0].pop('suppressesBuildingUids'), ['landsd/2:0', 'landsd/3:0'])
        self.assertEqual(out, before)
        self.assertEqual(self.models, before)

    def test_duplicate_rejected(self):
        self.reviews[1] = deepcopy(self.reviews[0])
        with self.assertRaises(AssertionError): self.check()

    def test_changed_second_form_rejected(self):
        self.forms['landsd/3:0']['heightSource'] = 'surveyed'
        with self.assertRaises(AssertionError): self.check()

    def test_second_revision_rejected(self):
        self.reviews[1]['sourceSHA256'] = 'b' * 64
        with self.assertRaises(AssertionError): self.check()

    def test_different_manifest_rejected(self):
        self.reviews[1]['currentManifest']['sha256'] = 'b' * 64
        with self.assertRaises(AssertionError): self.check()

    def test_second_publication_rejected(self):
        self.reviews[1]['publication'] = True
        with self.assertRaises(AssertionError): self.check()


if __name__ == '__main__': unittest.main()
