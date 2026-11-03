import copy
import unittest
from types import SimpleNamespace
from unittest.mock import patch
import silvercord_lippo_registered_boundary_v1_20261103 as subject
import nested_coordinated_native_boundary_v1_20261027 as nested
import nested_terrain_patch_validation_v1_20261027 as validator


class RegisteredFloorContract(unittest.TestCase):
    def setUp(self):
        self.nodes = {n:dict(coarseCells=[0,0,1,1],nativeMesh=dict(source={},position=[int(n) if n!='north' else 99,0,0])) for n in subject.NAMES}
        self.marked = copy.deepcopy(self.nodes)
        for name,node in self.marked.items():
            node['nativeMesh']['source']['coordinatedBoundary'] = dict(policy=subject.POLICY,proof=subject.PROOF,member=name)
        self.parent = dict(patches=[self.marked[n] for n in sorted(subject.NAMES-{'north'})],grid='exact')
        self.contract = object.__new__(subject.ExactContract)
        self.contract.nodes,self.contract.parent,self.contract.root = self.nodes,self.parent,dict(root='exact')
        self.rootnodes = [self.parent,self.marked['north']]

    def test_complete_root_and_nested_members(self):
        self.assertEqual(self.contract.verify_effective(self.rootnodes,root=True),16)
        self.assertEqual(self.contract.verify_effective(self.parent['patches'],root=False),15)

    def test_missing_duplicate_and_changed_body_rejected(self):
        bad = copy.deepcopy(self.rootnodes)
        bad[1]['nativeMesh']['position'][0] += 1
        for nodes in [self.rootnodes[:1],self.rootnodes+[self.marked['north']],bad]:
            with self.assertRaises(AssertionError):
                self.contract.verify_effective(nodes,root=True)

    def test_stale_proof_unknown_member_and_parent_rejected(self):
        for change in ['proof','member','parent']:
            nodes = copy.deepcopy(self.rootnodes)
            if change=='parent':nodes[0]['grid']='changed'
            elif change=='proof':nodes[1]['nativeMesh']['source']['coordinatedBoundary']['proof']={'path':'wrong','sha256':'wrong'}
            else:nodes[1]['nativeMesh']['source']['coordinatedBoundary']['member']='unknown'
            with self.assertRaises(AssertionError):
                self.contract.verify_effective(nodes,root=True)

    def test_north_cannot_hide_in_nested_parent(self):
        parent = copy.deepcopy(self.parent)
        parent['patches'].append(self.marked['north'])
        with self.assertRaises(AssertionError):
            self.contract.verify_effective([parent],root=True)
        with self.assertRaises(AssertionError):
            self.contract.verify_effective(parent['patches'],root=False)

    def test_scalar_parent_identity(self):
        self.contract.callbacks={n:[lambda x,y,z:True] for n in subject.NAMES}
        self.assertTrue(self.contract.boundary(self.marked['12'],self.parent)(1,2,3))
        with self.assertRaises(AssertionError):
            self.contract.boundary(self.marked['12'],dict(grid='wrong'))

    def test_ordinary_failure_propagates_and_every_hook_restores(self):
        def ordinary(*unused):raise AssertionError('ordinary unknown policy')
        legacy=SimpleNamespace(coordinated_boundary=ordinary,validate_effective_coordinated_members=ordinary)
        before=(nested.coordinated_boundary,nested.validate_effective_coordinated_members,validator.validate_effective_coordinated_members)
        with self.assertRaisesRegex(AssertionError,'ordinary unknown policy'):
            with subject.registered_validator(legacy):
                legacy.validate_effective_coordinated_members([dict(ordinary=True)])
        self.assertIs(legacy.coordinated_boundary,ordinary)
        self.assertIs(legacy.validate_effective_coordinated_members,ordinary)
        self.assertEqual(before,(nested.coordinated_boundary,nested.validate_effective_coordinated_members,validator.validate_effective_coordinated_members))

    def test_registered_root_dispatch_and_nested_dispatch_are_both_strict(self):
        calls=[]
        legacy=SimpleNamespace(coordinated_boundary=lambda n,p:None,validate_effective_coordinated_members=lambda ns:calls.append(ns))
        self.contract.verify_inputs=lambda:None
        with patch.object(subject,'ExactContract',return_value=self.contract),subject.registered_validator(legacy):
            legacy.validate_effective_coordinated_members(self.rootnodes)
            self.assertEqual(calls,[ [self.parent] ])
            with self.assertRaises(AssertionError):
                legacy.validate_effective_coordinated_members(self.rootnodes[:1])


if __name__=='__main__':unittest.main()
