import ast
import copy
import json
import unittest
from pathlib import Path
from nested_coordinated_parent_contract_v1_20261027 import POLICY, verify_parent
from nested_coordinated_native_boundary_v1_20261027 import canonical_sha


class ParentContract(unittest.TestCase):
    def setUp(self):
        old=dict(meta=dict(targetUids=['landsd/1:0'],parentTerrain='old.json',parentSha256='old'),
                 nativeMesh=dict(position=[0,5,0],index=[0,0,0],source={}))
        self.prior=dict(w=4,h=4,elev=[5]*16,renderedElev=[5]*16,vegetation=[0]*16,
                        meta=dict(targetUids=['landsd/1:0'],unchanged='yes'),
                        patches=[old,dict(meta=dict(targetUids=[]),retained='exact')])
        before=copy.deepcopy(old);before['meta'].update(parentTerrain='prior.json',parentSha256='prior')
        north=copy.deepcopy(before);north['meta']['targetUids']=['landsd/1:0','landsd/2:0']
        south=copy.deepcopy(before);south['meta']['targetUids']=['landsd/2:0']
        self.refs={'before':before,'north':north,'south':south}
        self.proof=dict(parentBinding=dict(policy=POLICY,retainedMember='north',newMember='south',
                      retainedChildIndex=0,newTargetUids=['landsd/2:0']),members={})
        for name in ['north','south']:
            self.proof['members'][name]=dict(before='before',candidate=name,canonicalSHA256=canonical_sha(self.refs[name]))
        self.marker=dict(policy='finite-native-shared-boundary-v1',proof=dict(path='proof',sha256='sha'),member='north')
        self.successor=copy.deepcopy(self.prior)
        for name,index in [('north',0),('south',2)]:
            node=copy.deepcopy(self.refs[name]);node['nativeMesh']['source']['coordinatedBoundary']={**self.marker,'member':name}
            if index==2:self.successor['patches'].append(node)
            else:self.successor['patches'][index]=node
        self.successor['meta']['targetUids']=['landsd/1:0','landsd/2:0']

    def verify(self):
        return verify_parent(self.prior,self.successor,self.proof,self.marker,self.refs.__getitem__,canonical_sha)

    def test_exact_pair_preserves_inputs(self):
        old=json.dumps([self.prior,self.successor],sort_keys=True)
        self.assertTrue(self.verify()['bothExactMembersPresent'])
        self.assertEqual(old,json.dumps([self.prior,self.successor],sort_keys=True))

    def test_each_grid_and_bystander_change_rejected(self):
        for field in ['elev','renderedElev','vegetation']:
            with self.subTest(field=field):
                self.successor[field][0]+=1
                with self.assertRaises(AssertionError):self.verify()
                self.successor[field][0]-=1
        self.successor['patches'][1]['retained']='changed'
        with self.assertRaises(AssertionError):self.verify()

    def test_missing_mate_rejected(self):
        self.successor['patches'].pop()
        with self.assertRaises(AssertionError):self.verify()

    def test_changed_mate_rejected(self):
        self.successor['patches'][-1]['nativeMesh']['position'][1]+=1
        with self.assertRaises(AssertionError):self.verify()

    def test_foreign_proof_marker_rejected(self):
        self.successor['patches'][-1]['nativeMesh']['source']['coordinatedBoundary']['proof']={'path':'other','sha256':'other'}
        with self.assertRaises(AssertionError):self.verify()

    def test_changed_historical_retained_geometry_rejected(self):
        self.refs['before']['nativeMesh']['position'][1]+=1
        with self.assertRaises(AssertionError):self.verify()

    def test_parent_metadata_change_rejected(self):
        self.successor['meta']['unchanged']='no'
        with self.assertRaises(AssertionError):self.verify()


class ValidatorParity(unittest.TestCase):
    def test_driver_only_admits_two_more_original_source_diagnostics(self):
        here=Path(__file__).parent
        old=ast.parse((here/'original_leased_diagnostic_sequence_v11_20261026.py').read_text())
        new=ast.parse((here/'original_leased_diagnostic_sequence_v12_20261027.py').read_text())
        def allowed(tree):
            return next(n for n in tree.body if isinstance(n,ast.Assign)
                        and any(isinstance(t,ast.Name) and t.id=='ALLOWED' for t in n.targets))
        a,b=allowed(old),allowed(new)
        self.assertEqual(ast.literal_eval(b.value)-ast.literal_eval(a.value),{
            'selected_original_overlapping_native_contacts_v3_20261024.py',
            'selected_original_native_fallback_contacts_v2_20261026.py'})
        b.value=a.value
        self.assertEqual(ast.dump(old),ast.dump(new))

    def test_native_validator_only_changes_coordinated_import(self):
        here=Path(__file__).parent
        old=ast.parse((here.parent/'island-detail-integration/native_terrain_validation.py').read_text())
        new=ast.parse((here/'nested_native_terrain_validation_v1_20261027.py').read_text())
        changes=0
        for node in ast.walk(new):
            if isinstance(node,ast.ImportFrom) and node.module=='nested_coordinated_native_boundary_v1_20261027':
                node.module='coordinated_native_boundary';changes+=1
        self.assertEqual(changes,1)
        self.assertEqual(ast.dump(old),ast.dump(new))

    def test_all_other_coordinated_guards_unchanged(self):
        here=Path(__file__).parent
        old=ast.parse((here.parent/'island-detail-integration/coordinated_native_boundary.py').read_text())
        new=ast.parse((here/'nested_coordinated_native_boundary_v1_20261027.py').read_text())
        count=0
        for node in ast.walk(new):
            if isinstance(node,ast.FunctionDef) and node.name=='coordinated_boundary':
                for index,statement in enumerate(node.body):
                    if isinstance(statement,ast.If) and ast.unparse(statement.test)=="proof.get('parentBinding') is None":
                        self.assertEqual(len(statement.body),1)
                        self.assertIsInstance(statement.body[0],ast.Assert)
                        node.body[index:index+1]=statement.body;count+=1;break
        self.assertEqual(count,1)
        self.assertEqual(ast.dump(old),ast.dump(new))

    def test_patch_guards_unchanged_and_complete_pair_check_added(self):
        here=Path(__file__).parent
        def function(path):
            return next(n for n in ast.parse(path.read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='validate_patch')
        old=function(here.parent/'island-detail-integration/publish.py')
        new=function(here/'nested_terrain_patch_validation_v1_20261027.py')
        self.assertEqual(ast.unparse(new.body[-1]),'validate_effective_coordinated_members(children)')
        new.body.pop()
        self.assertEqual(ast.dump(old),ast.dump(new))


if __name__=='__main__':unittest.main()
