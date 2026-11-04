"""Reject destination collisions and scope expansion before publication."""
import copy
import unittest

import june_garden_guarded_publish_v1_20261103 as guard


class ExactPlan(unittest.TestCase):
    def setUp(self):
        self.surface = dict(members=[dict(
            member=name, candidate=dict(path='candidate-'+name+'.json', sha256=name),
            replaces=dict(url='old-'+name+'.json', sha256='old-'+name))
            for name in guard.DESTINATIONS])
        self.plan = dict(areas=[dict(area='June Garden unchanged originals',
            catalogue=str((guard.STAGE/'catalogue.json').relative_to(guard.ROOT)),
            destination='city/data/official-models/'+guard.QUALIFIED+'/catalogue.json')],
            topLevelTerrainPatches=[dict(source=m['candidate']['path'], sha256=m['candidate']['sha256'],
                destination=guard.DESTINATIONS[m['member']], resolution=2, area='original terrain',
                replaces=copy.deepcopy(m['replaces']), nativeReview=dict(path='review-'+m['member'], sha256='review'))
                for m in self.surface['members']])

    def test_exact_three_new_destinations(self):
        self.assertTrue(guard.exact_plan(self.plan, self.surface))

    def test_existing_terrain_destination(self):
        self.plan['topLevelTerrainPatches'][0]['destination'] = self.plan['topLevelTerrainPatches'][0]['replaces']['url']
        with self.assertRaises(AssertionError): guard.exact_plan(self.plan, self.surface)

    def test_missing_member(self):
        self.plan['topLevelTerrainPatches'].pop()
        with self.assertRaises(AssertionError): guard.exact_plan(self.plan, self.surface)

    def test_unreviewed_replacement(self):
        self.plan['topLevelTerrainPatches'][0]['replaces']['sha256'] = 'changed'
        with self.assertRaises(AssertionError): guard.exact_plan(self.plan, self.surface)

    def test_unrelated_catalogue(self):
        self.plan['areas'][0]['catalogue'] = 'unreviewed/catalogue.json'
        with self.assertRaises(AssertionError): guard.exact_plan(self.plan, self.surface)

    def test_installed_support_migration(self):
        self.plan['dependencyReviews'] = ['not-authorised']
        with self.assertRaises(AssertionError): guard.exact_plan(self.plan, self.surface)


if __name__ == '__main__': unittest.main()
