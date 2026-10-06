import unittest
from current_installed_support_acceptance import resolve_contact

class SupportAcceptanceTests(unittest.TestCase):
    def setUp(self):
        self.interface = {'passed': True, 'samples': 265, 'strictContacts': 265,
                          'wallIntersections': 0, 'unresolved': []}
        self.foundation = {'strictFoundationAccepted': True}
        self.reasons = ['ground-contact-unresolved', 'sampled-ground-gap-below-model-bottom',
                        'sampler-rendered-terrain-disagreement', 'terrain-intersects-source-over-0.5m',
                        'whole-source-foundation', 'mobile-runtime-budget', 'source-integrity']
    def test_complete_support_resolves_only_terrain_gap_diagnostics(self):
        self.assertEqual(resolve_contact(self.reasons, self.interface, self.foundation), self.reasons[2:])
    def test_any_unresolved_or_non_strict_interface_retains_all_reasons(self):
        for changes in ({'passed': False}, {'samples': 0}, {'strictContacts': 264},
                        {'wallIntersections': 1}, {'unresolved': [{'position': [0,0,0]}]}):
            self.assertEqual(resolve_contact(self.reasons, self.interface | changes, self.foundation), self.reasons)
    def test_incomplete_or_buried_foundation_retains_all_reasons(self):
        for foundation in ({}, {'strictFoundationAccepted': False}):
            self.assertEqual(resolve_contact(self.reasons, self.interface, foundation), self.reasons)
    def test_other_physical_diagnostics_never_resolve(self):
        reasons = ['sampled-terrain-above-model-bottom', 'native-neighbour-regression:landsd/1:0',
                   'incomplete-contact-check', 'terrain-coverage', 'strict-identity-fit']
        self.assertEqual(resolve_contact(reasons, self.interface, self.foundation), reasons)

if __name__ == '__main__': unittest.main()
