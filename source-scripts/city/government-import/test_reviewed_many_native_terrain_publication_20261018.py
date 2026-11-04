"""Exercise actual publisher guards across all seven replaced parents."""
import json
import unittest
import test_reviewed_multi_native_terrain_publication_20261009 as prior
from reviewed_many_native_terrain_publication_20261018 import stage_top_level

class ManyNativePublicationTests(prior.PluralNativePublicationTests):
    def setUp(self):
        super().setUp()
        old = prior.stage_top_level
        prior.stage_top_level = stage_top_level
        self.addCleanup(setattr, prior, 'stage_top_level', old)

    def seven(self):
        for i in range(2, 7):
            old = dict(nativeMesh=True, coarseCells=[1+4*i,1,3+4*i,3], hydro={'water':[]}, meta={'targetUids':[f'old-{i}']})
            self.old.append(old)
            url = f'city/data/old-{i}.json'
            sha = self.put('3d-viewer/'+url, old)
            self.replacements.append(dict(url=url, sha256=sha, retainedUids=old['meta']['targetUids']))
            self.original['terrainPatches'].append(dict(url=url, sha256=sha))
        self.new['coarseCells'] = [1,1,27,3]
        self.new['meta']['targetUids'] = [uid for old in self.old for uid in old['meta']['targetUids']] + ['new']
        newsha = self.put('staged/new.json', self.new)
        self.plan['topLevelTerrainPatches'][0]['sha256'] = newsha
        full = dict(aiCalls=0, modelGeometryChanges=0, rows=[dict(uid=uid, passed=True, terrain=dict(newlyWhollyBuried=0,newlyUpwardWhollyBuried=0)) for uid in self.new['meta']['targetUids']])
        fullsha = self.put('proof/full.json', full)
        for i, row in enumerate(self.replacements):
            decision = dict(status='approved-for-integration', supersededURL=row['url'],supersededSHA256=row['sha256'], replacementSHA256=newsha, sourceGeometryChanged=False, aiCalls=0,modelGeometryChanges=0, retainedUids=row['retainedUids'], replacementTargetUids=self.new['meta']['targetUids'], fullMeshCheck=dict(path='proof/full.json',sha256=fullsha))
            path = f'proof/review-{i}.json'
            row['nativeReview'] = dict(path=path,sha256=self.put(path,decision))

    def test_seven_parents_replaced_with_one_asset(self):
        self.seven()
        manifest, edits, report = self.run_adapter()
        self.assertEqual([row['url'] for row in manifest['terrainPatches']], ['city/data/new.json'])
        self.assertEqual(len(edits), 1)
        self.assertEqual(len(report['replacedTerrainPatches']), 7)
        self.assertTrue(all((self.root/'3d-viewer'/row['url']).exists() for row in self.replacements))

    def test_seventh_source_mutation_rejected(self):
        self.seven()
        self.put('3d-viewer/'+self.replacements[6]['url'], {'changed':True})
        with self.assertRaises(AssertionError): self.run_adapter()

    def test_seventh_review_mutation_rejected(self):
        self.seven()
        (self.root/'proof/review-6.json').write_text('{}')
        with self.assertRaisesRegex(AssertionError,'review changed'): self.run_adapter()

if __name__ == '__main__':
    unittest.main()
