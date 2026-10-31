"""Negative publication-contract checks against the actual qualified metadata."""
import copy
import unittest
import sha_tin_guarded_publish_v1_20261029 as guard


class ExactShaTinContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = guard.read(guard.stage.STAGE / 'plan.json')
        cls.models = guard.read(guard.stage.STAGE / 'catalogue.json')['models']
        inputs = guard.read(guard.stage.BASE / (guard.stage.P + 'source-bound-production-fixture-v1-20261029') / 'fixture-inputs.json')
        cfg = guard.read(guard.ROOT / inputs['configPath'])
        cls.originals = guard.read(guard.ROOT / cfg['stage'] / 'catalogue.json')['models']
        cls.hashes = {m['uid']: m['sha256'] for m in cls.models}

    def test_exact_reviewed_metadata_passes(self):
        self.assertTrue(guard.verify_models(self.originals, self.models, self.hashes))
        self.assertTrue(guard.verify_plan(self.plan))

    def bad_model(self, change):
        models = copy.deepcopy(self.models)
        change(models)
        with self.assertRaises(AssertionError):
            guard.verify_models(self.originals, models, self.hashes)

    def test_source_bytes_changed(self):
        self.bad_model(lambda rows: rows[0].update(sha256='0' * 64))

    def test_native_pose_changed(self):
        self.bad_model(lambda rows: rows[0].update(rootTranslation=[-834500, 1, 816500]))

    def test_support_removed(self):
        self.bad_model(lambda rows: rows[0].update(supportDependencies=[]))

    def test_partial_activation_group(self):
        self.bad_model(lambda rows: rows[0].update(activationGroup=rows[0]['activationGroup'][:-1]))

    def test_procedural_windows_added(self):
        self.bad_model(lambda rows: rows[0].update(proceduralWindows=True))

    def test_approval_missing(self):
        self.bad_model(lambda rows: rows[0].update(placementReviewed=False))

    def test_conflicting_recorded_height_not_rewritten(self):
        self.bad_model(lambda rows: next(m for m in rows if m['uid'] == 'landsd/271344:0').update(recordedTopHeight=36.84))

    def bad_plan(self, change):
        plan = copy.deepcopy(self.plan)
        change(plan)
        with self.assertRaises(AssertionError):
            guard.verify_plan(plan)

    def test_missing_terrain_member(self):
        self.bad_plan(lambda p: p['topLevelTerrainPatches'].pop())

    def test_unrelated_replacement(self):
        self.bad_plan(lambda p: p['topLevelTerrainPatches'][0].update(replaces={'url':'city/data/unrelated.json','sha256':'0'*64}))

    def test_foundation_uid_changed(self):
        self.bad_plan(lambda p: p['nativeBasicFallbackGrounds'][0].update(uid='landsd/224123:0'))

    def test_unscoped_catalogue_replacement(self):
        self.bad_plan(lambda p: p.update(catalogueReplacements=[{}]))


if __name__ == '__main__':
    unittest.main()
