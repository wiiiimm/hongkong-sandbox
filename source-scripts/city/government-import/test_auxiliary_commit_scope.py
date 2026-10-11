"""A supporting original cannot masquerade as an XL installation or change pose."""
import copy
import importlib.util
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location('auxiliary_commit',Path(__file__).with_name('xl-commit-installed.py'))
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

class AuxiliaryCommitScopeTests(unittest.TestCase):
    def fixture(self):
        entry={'uid':'landsd/205663:0','objectId':205663,'buildingCSUID':'4104444986P20170306',
               'sha256':'original-sha','worldBounds':[[1,2,3],[4,5,6]]}
        inputs={'pairs':[{'uid':'landsd/207957:0','supportUid':entry['uid']}],
                'sources':[{'uid':entry['uid'],'sourceSHA256':entry['sha256'],
                    'source':{'building':{'structureType':'Podium'}},'candidate':{'entry':copy.deepcopy(entry)}}]}
        return inputs,[entry['uid']],{entry['uid']:entry['sha256']},{'models':[entry]},set()
    def test_exact_auxiliary_is_eligible(self):
        module.check_auxiliary_scope(*self.fixture())
    def test_xl_source_cannot_use_zero_credit_route(self):
        args=list(self.fixture());args[-1]=set(args[1])
        with self.assertRaises(AssertionError):module.check_auxiliary_scope(*args)
    def test_undeclared_support_cannot_be_committed(self):
        args=list(self.fixture());args[0]['pairs'][0]['supportUid']='landsd/other:0'
        with self.assertRaises(AssertionError):module.check_auxiliary_scope(*args)
    def test_source_and_pose_changes_are_rejected(self):
        for key,value in [('uid','landsd/other:0'),('objectId',1),('buildingCSUID','foreign'),
                          ('sha256','modified'),('worldBounds',[[1,1,1],[2,2,2]])]:
            with self.subTest(key=key):
                args=list(self.fixture());args[3]['models'][0][key]=value
                with self.assertRaises((AssertionError,KeyError)):module.check_auxiliary_scope(*args)
    def test_tower_cannot_be_labelled_auxiliary_podium(self):
        args=list(self.fixture());args[0]['sources'][0]['source']['building']['structureType']='Tower'
        with self.assertRaises(AssertionError):module.check_auxiliary_scope(*args)

if __name__=='__main__':unittest.main()
