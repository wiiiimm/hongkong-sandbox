import unittest
from component_type_resolution import resolve


class ComponentResolutionTests(unittest.TestCase):
    def setUp(self):
        self.tower = {'building': {'uid': 'landsd/1:0', 'objectId': 1, 'buildingCSUID': '3450016500T20250101', 'structureType': 'Tower'}}
        self.podium = {'building': {'uid': 'landsd/2:0', 'objectId': 2, 'buildingCSUID': '3450016500P20250101', 'structureType': 'Podium'}}
        self.model = {'modelId': 'B345001650001063C0', 'matching': {'officialCandidates': [s['building'] for s in [self.tower, self.podium]]}}

    def test_tower_and_podium_are_distinct_even_with_same_georef(self):
        result = resolve(self.model, [self.tower, self.podium])
        self.assertEqual(result['uid'], 'landsd/1:0')
        self.assertFalse(result['identityAccepted'])
        self.assertFalse(result['installationApproved'])

    def test_duplicate_tower_parts_remain_ambiguous(self):
        second = {'building': {**self.tower['building'], 'uid': 'landsd/1:1'}}
        self.assertFalse(resolve(self.model, [self.tower, second])['qualified'])

    def test_wrong_structure_or_georef_does_not_match(self):
        for changes in [{'structureType': 'Podium'}, {'buildingCSUID': '3450116500T20250101'}]:
            altered = {'building': {**self.tower['building'], **changes}}
            self.assertFalse(resolve(self.model, [altered])['qualified'])

    def test_official_object_identity_must_match_and_be_unique(self):
        for candidates in [[], [{**self.tower['building'], 'objectId': 9}], [self.tower['building'], self.tower['building']]]:
            model = {**self.model, 'matching': {'officialCandidates': candidates}}
            self.assertFalse(resolve(model, [self.tower])['qualified'])


if __name__ == '__main__': unittest.main()
