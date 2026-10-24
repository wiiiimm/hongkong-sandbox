"""Source-only acquisition reservation scope, no claim, DB or geometry."""
import unittest
from unittest.mock import patch
import heritage165054_south20b_terrain_acquisition_v2_20261014 as a
class ApplicableOriginalSourceResources(unittest.TestCase):
    def test_actual_45_context_kept_with_exact_source_only_keys(self):
        scope=a.read(a.NORTH/'proposal-input.json')['scope']['allActorsForNominationLease'];before=list(scope)
        from run import reservations
        with patch.object(reservations,'connect',side_effect=AssertionError('DB forbidden')):r=a.canonical_resources(scope)
        self.assertEqual(scope,before);self.assertEqual(len(scope),45);self.assertEqual(r,sorted(['building:'+a.UID,'immutable-source-sheet:7-SW-20B','immutable-source-proof:'+a.BATCH]));self.assertFalse(any(q.startswith('terrain-patch:') for q in r))
    def test_incomplete_context_cannot_be_silently_changed_to_match_narrow_lease(self):
        with self.assertRaises(AssertionError):a.canonical_resources([a.UID])
if __name__=='__main__':unittest.main()
