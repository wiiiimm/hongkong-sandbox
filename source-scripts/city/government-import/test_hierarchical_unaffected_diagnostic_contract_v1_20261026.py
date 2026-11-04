import copy
import unittest
from run import ROOT, read
from hierarchical_unaffected_diagnostic_contract_v1_20261026 import verify_context

class NonEffectDiagnosticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        base=ROOT/'docs/astra-city/government-import';prefix='government-xl-podium323546-after-beverly-d-'
        def load(name):return read(base/(prefix+name+'-20261026')/'summary.json')
        candidate=load('hierarchical-group-candidate-v2');old=candidate['replacedNativeTerrain'][0]
        cls.fixture=dict(prior=read(ROOT/'3d-viewer'/old['url']),successor=read(ROOT/candidate['candidate']['path']),owners=candidate['uids'],replacement={k:old[k]for k in ['url','sha256','retainedUids']},proof=load('whole-installed-change-scope-v2'),forms=load('hierarchical-forms-v2'),scope=load('three-current-neighbours-v1'))
    def check(self,change=None):
        f=copy.deepcopy(self.fixture)
        if change:change(f)
        return verify_context(**f)
    def test_actual_complete_non_effect_case(self):
        self.assertEqual(self.check()['retainedChildren'],13)
    def test_affected_installed_actor_rejected(self):
        with self.assertRaises(AssertionError):self.check(lambda f:f['proof'].update(affectedNativeUids=['landsd/323703:0']))
    def test_affected_basic_support_rejected(self):
        with self.assertRaises(AssertionError):self.check(lambda f:f['proof'].update(affectedRegisteredBasicSupportUids=['landsd/176739:0']))
    def test_missing_actual_asset_verification_rejected(self):
        with self.assertRaises(AssertionError):self.check(lambda f:f['proof'].update(allCurrentInstalledAssetBytesVerified=False))
    def test_changed_old_grid_rejected(self):
        with self.assertRaises(AssertionError):self.check(lambda f:f['successor']['elev'].__setitem__(0,f['successor']['elev'][0]+.01))
    def test_ordinary_regression_rejected(self):
        with self.assertRaises(AssertionError):self.check(lambda f:f['forms'].update(flagged=[{'uid':'landsd/1:0'}],ordinaryFlagged=1))
    def test_incomplete_current_native_scope_rejected(self):
        with self.assertRaises(AssertionError):self.check(lambda f:f['scope']['rows'][0].update(currentNativeActorsChecked=6958))
    def test_reapproval_of_legacy_holds_rejected(self):
        with self.assertRaises(AssertionError):self.check(lambda f:f['proof'].update(rawLegacyApprovalsChanged=True))
    def test_missing_retained_target_rejected(self):
        with self.assertRaises(AssertionError):self.check(lambda f:f['replacement']['retainedUids'].pop())

if __name__=='__main__':unittest.main()
