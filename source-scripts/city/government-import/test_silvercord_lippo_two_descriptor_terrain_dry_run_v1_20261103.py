import copy
import unittest
from contextlib import nullcontext
from types import SimpleNamespace
from unittest.mock import patch, Mock
import silvercord_lippo_two_descriptor_terrain_dry_run_v1_20261103 as subject


class ExactTerrainDispatch(unittest.TestCase):
    def setUp(self):
        self.proof = dict(path='exact-proof',sha256='exact-sha')
        self.nodes = {key:dict(nativeMesh=dict(source={},position=[1,2,3])) for key in ['north','12']}
        marked = {}
        for name,node in self.nodes.items():
            marked[name] = copy.deepcopy(node)
            marked[name]['nativeMesh']['source']['coordinatedBoundary'] = dict(
                policy=subject.POLICY,proof=self.proof,member=name)
        self.parent = dict(patches=[marked['12']])
        self.children = [self.parent,marked['north'],dict(ordinary=True)]
        self.pub = SimpleNamespace(validate_grid=object(),validate_patch=object())
        self.original = (self.pub.validate_grid,self.pub.validate_patch)

    def context(self):
        return subject.exact_two_descriptor_validators(self.pub,self.nodes,self.parent,{},self.proof,[])

    def test_exact_members_and_ordinary_policies_both_checked(self):
        ordinary = Mock()
        with patch.object(subject,'complete_boundary_validators',return_value=nullcontext()), \
             patch.object(subject,'private_nested_contract',return_value=nullcontext()), \
             patch.object(subject.root_contract,'validate_effective_coordinated_members',ordinary):
            with self.context():
                subject.root_contract.validate_effective_coordinated_members(self.children)
            ordinary.assert_called_once_with([self.parent,dict(ordinary=True)])
            self.assertIs(subject.root_contract.validate_effective_coordinated_members,ordinary)
        self.assertEqual((self.pub.validate_grid,self.pub.validate_patch),self.original)

    def test_missing_duplicate_and_changed_member_fail_closed(self):
        changed = copy.deepcopy(self.children)
        changed[1]['nativeMesh']['position'][0] = 99
        for children in [self.children[:1],self.children+[self.children[1]],changed]:
            with patch.object(subject,'complete_boundary_validators',return_value=nullcontext()), \
                 patch.object(subject,'private_nested_contract',return_value=nullcontext()):
                previous = subject.root_contract.validate_effective_coordinated_members
                with self.assertRaises(AssertionError):
                    with self.context():
                        subject.root_contract.validate_effective_coordinated_members(children)
                self.assertIs(subject.root_contract.validate_effective_coordinated_members,previous)
            self.assertEqual((self.pub.validate_grid,self.pub.validate_patch),self.original)

    def test_ordinary_unknown_policy_failure_propagates_and_restores(self):
        ordinary = Mock(side_effect=AssertionError('unknown ordinary policy'))
        with patch.object(subject,'complete_boundary_validators',return_value=nullcontext()), \
             patch.object(subject,'private_nested_contract',return_value=nullcontext()), \
             patch.object(subject.root_contract,'validate_effective_coordinated_members',ordinary):
            with self.assertRaisesRegex(AssertionError,'unknown ordinary policy'):
                with self.context():
                    subject.root_contract.validate_effective_coordinated_members(self.children)
            self.assertIs(subject.root_contract.validate_effective_coordinated_members,ordinary)
        self.assertEqual((self.pub.validate_grid,self.pub.validate_patch),self.original)


if __name__ == '__main__':
    unittest.main()
