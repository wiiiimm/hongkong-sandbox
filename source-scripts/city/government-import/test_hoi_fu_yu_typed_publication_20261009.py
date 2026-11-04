"""Actual pair evidence rejects unrelated failures and broken dependency scope."""
import copy
import unittest
from run import ROOT,read
from hoi_fu_yu_typed_publication_20261009 import resolve_pair_member,PODIUM,TOWER

class PairPublicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        parent=ROOT/'docs/astra-city/government-import'
        source=parent/'government-xl-hoi-fu-yu-complete-original-physical-v2-20261009'
        cls.roles={'column':read(parent/'xl-terrain-recovery-20261009-hoi-fu-column-role-v2/typed-role.json.gz'),
                   'support':read(parent/'government-xl-hoi-yu-attached-support-proof-20261009/proof.json')}
        cls.foundations={r['uid']:r for r in read(source/'foundation.json')['rows']}
        cls.decisions={r['uid']:r for r in read(source/'physical-decisions.json')['rows']}

    def resolve(self,uid,roles=None,raw=None,foundation=None):
        f=foundation or self.foundations[uid];d=self.decisions[uid]
        return resolve_pair_member(uid,f['sourceSHA256'],raw if raw is not None else d['numericReasons'],
                                   d['diagnosticResolution']['remaining'],f,roles or self.roles)

    def test_current_complete_pair_preserves_raw_failures(self):
        for uid in [PODIUM,TOWER]:
            result=self.resolve(uid)
            self.assertTrue(result['passed']);self.assertFalse(result['publication'])
            self.assertEqual(result['rawNumericReasons'],self.decisions[uid]['numericReasons'])
        self.assertFalse(self.resolve(PODIUM)['rawFoundationAccepted'])

    def test_mobile_budget_failure_cannot_receive_role_credit(self):
        for uid in [PODIUM,TOWER]:
            with self.assertRaises(AssertionError):
                self.resolve(uid,raw=self.decisions[uid]['numericReasons']+['mobile-runtime-budget'])

    def test_other_source_cannot_inherit_original_pair_support(self):
        roles=copy.deepcopy(self.roles);roles['support']['supportSHA256']='0'*64
        with self.assertRaises(AssertionError):self.resolve(TOWER,roles=roles)

    def test_omitted_foreign_actor_scope_is_not_accepted(self):
        roles=copy.deepcopy(self.roles);roles['column']['currentForeignActorsChecked']-=1
        with self.assertRaises(AssertionError):self.resolve(PODIUM,roles=roles)

    def test_buried_roof_still_blocks_column_route(self):
        f=copy.deepcopy(self.foundations[PODIUM]);f['foundation']['fullyBuriedUpwardTriangles']=1
        with self.assertRaises(AssertionError):self.resolve(PODIUM,foundation=f)

    def test_missing_tower_component_does_not_get_support_credit(self):
        roles=copy.deepcopy(self.roles);roles['support']['verifiedAttachments'].pop()
        with self.assertRaises(AssertionError):self.resolve(TOWER,roles=roles)

if __name__=='__main__':unittest.main()
