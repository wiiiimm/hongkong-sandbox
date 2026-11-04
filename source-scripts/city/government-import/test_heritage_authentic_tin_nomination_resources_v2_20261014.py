"""Actual 45-actor preclaim setup; normalise is pure, no lease/DB/geometry."""
import unittest
from unittest.mock import patch
import heritage165054_authentic_tin_nomination_v2_20261014 as a
from run import reservations
class ActualCanonicalScope(unittest.TestCase):
    def actors(self):
        prior=a.BASE/'government-xl-heritage165054-authentic-tin-nomination-v1-20261014-proposal/draft-pins.json'
        actors=a.read(prior)['canonicalActors'];self.assertEqual(len(actors),45);self.assertIn('way/261065256:0',actors);return actors
    def test_actual_45_scope_normalises_before_claim_with_no_DB(self):
        actors=self.actors()
        with patch.object(reservations,'connect',side_effect=AssertionError('no DB allowed in fixture')): resources=a.canonical_resources(actors)
        self.assertEqual(len(resources),91);self.assertEqual(resources,reservations.normalise(resources))
        self.assertIn('foreign-form:way/261065256:0',resources);self.assertIn('terrain-patch:way/261065256:0',resources)
        self.assertNotIn('building:way/261065256:0',resources)
        self.assertEqual({q.split(':',1)[1] for q in resources if q.startswith(('building:','foreign-form:'))},set(actors))
    def test_actual_old_key_reproduces_exact_preclaim_failure_without_DB(self):
        actors=self.actors()
        with patch.object(reservations,'connect',side_effect=AssertionError('no DB allowed in fixture')),self.assertRaisesRegex(ValueError,'Building keys require'):
            reservations.normalise(['building:'+u for u in actors])
if __name__=='__main__':unittest.main()
