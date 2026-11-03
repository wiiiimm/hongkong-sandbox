"""Reject incomplete, duplicated, stale or altered private terrain membership."""
import copy
import unittest
from unittest.mock import patch
import silvercord_lippo_complete_floor_admission_v1_20261103 as subject


class ExactEffectiveMembers(unittest.TestCase):
    def setUp(self):
        self.ref = dict(path='docs/private-proof.json', sha256='a'*64)
        self.expected = {str(i): dict(id=str(i), nativeMesh=dict(position=[i, 0, 0], index=[0, 0, 0], source={})) for i in [12, 15, 17, *range(18, 30)]}
        self.expected['north'] = dict(id='north', nativeMesh=dict(position=[0, 0, 1], index=[0, 0, 0], source={}))
        self.marked = copy.deepcopy(self.expected)
        for name, node in self.marked.items():
            node['nativeMesh']['source']['coordinatedBoundary'] = dict(policy=subject.POLICY, proof=self.ref, member=name)
        self.parent = dict(patches=[node for name, node in self.marked.items() if name != 'north'])
        self.effective = [self.parent, self.marked['north']]

    def test_complete_nested_and_actual_top_level_member(self):
        self.assertEqual(subject.verify_exact_members(self.effective, self.expected, self.ref), 16)

    def test_missing_north_is_rejected(self):
        with self.assertRaises(AssertionError):
            subject.verify_exact_members([self.parent], self.expected, self.ref)

    def test_duplicate_north_is_rejected(self):
        with self.assertRaises(AssertionError):
            subject.verify_exact_members(self.effective+[self.marked['north']], self.expected, self.ref)

    def test_changed_full_member_body_is_rejected(self):
        changed = copy.deepcopy(self.effective)
        changed[0]['patches'][0]['nativeMesh']['position'][1] = .01
        with self.assertRaises(AssertionError):
            subject.verify_exact_members(changed, self.expected, self.ref)

    def test_stale_proof_or_unknown_member_is_rejected(self):
        for key, value in [('proof', dict(path='docs/old-proof.json', sha256='b'*64)), ('member', 'unowned')]:
            changed = copy.deepcopy(self.effective)
            changed[1]['nativeMesh']['source']['coordinatedBoundary'][key] = value
            with self.assertRaises(AssertionError):
                subject.verify_exact_members(changed, self.expected, self.ref)

    def test_private_context_restores_on_failure_and_delegates_unknown_policy(self):
        before_boundary = subject.nested.coordinated_boundary
        before_effective = subject.validator.validate_effective_coordinated_members
        unknown = dict(nativeMesh=dict(source=dict(coordinatedBoundary=dict(policy='unknown'))))
        with patch.object(subject.nested, 'coordinated_boundary', side_effect=AssertionError('Unknown policy')) as ordinary:
            with patch.object(subject, 'finite_callback', return_value=lambda *xyz: False):
                with self.assertRaisesRegex(AssertionError, 'Unknown policy'):
                    with subject.private_nested_contract(self.expected, self.parent, {}, self.ref,
                            [(name, 'north') for name in self.expected if name != 'north']):
                        subject.nested.coordinated_boundary(unknown, {})
            self.assertIs(subject.nested.coordinated_boundary, ordinary)
        self.assertIs(subject.nested.coordinated_boundary, before_boundary)
        self.assertIs(subject.validator.validate_effective_coordinated_members, before_effective)


if __name__ == '__main__':
    unittest.main()
