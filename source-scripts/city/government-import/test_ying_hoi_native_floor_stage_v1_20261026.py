"""An installed native floor dependency cannot be omitted or replaced by BASIC."""
import copy
import unittest
from run import ROOT, read
from ying_hoi_native_wall_admission_v1_20261026 import UID, PARENT, SOURCE_SHA, PARENT_SHA
from ying_hoi_native_floor_stage_v1_20261026 import expected_dependencies


class ExactFloorDependency(unittest.TestCase):
    def setUp(self):
        parent = read(ROOT / 'docs/astra-city/government-import/government-xl-after-ferry-ying-hoi-support-binding-v1-20261026/summary.json')['installedNativeEntry']
        self.review = dict(sourceSHA256ByUid={UID: SOURCE_SHA}, runtimeAvailabilityDependenciesByUid={UID: PARENT},
                           retainedBasicSupportDependencies=[], retainedNativeEntries={PARENT: parent})

    def test_exact_approved_native_is_required(self):
        deps = expected_dependencies(UID, self.review)
        self.assertEqual(len(deps), 1)
        self.assertEqual((deps[0]['uid'], deps[0]['state'], deps[0]['sha256']), (PARENT, 'installed', PARENT_SHA))

    def test_other_source_is_not_admitted(self):
        with self.assertRaises(AssertionError):
            expected_dependencies('landsd/336667:0', self.review)

    def test_basic_cannot_replace_original_floor(self):
        changed = copy.deepcopy(self.review)
        changed['retainedBasicSupportDependencies'] = [dict(uid=UID, supportUid=PARENT)]
        with self.assertRaises(AssertionError):
            expected_dependencies(UID, changed)

    def test_missing_native_edge_is_rejected(self):
        changed = copy.deepcopy(self.review)
        changed['runtimeAvailabilityDependenciesByUid'] = {}
        with self.assertRaises(AssertionError):
            expected_dependencies(UID, changed)

    def test_unapproved_parent_cannot_be_reapproved(self):
        changed = copy.deepcopy(self.review)
        changed['retainedNativeEntries'][PARENT]['publicationApproved'] = False
        with self.assertRaises(AssertionError):
            expected_dependencies(UID, changed)


if __name__ == '__main__':
    unittest.main()
