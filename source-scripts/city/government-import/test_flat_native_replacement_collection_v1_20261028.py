"""Adversarial scope losses cannot silently pass multi-member replacement."""
import copy
import unittest
from flat_native_replacement_collection_v1_20261028 import verify


class ScopeTests(unittest.TestCase):
    def fixture(self):
        old={url:dict(nativeMesh={'source':{}},coarseCells=cells,
            meta=dict(parentTerrain='city/data/terrain.json',parentSha256='root',targetUids=[uid]))
            for url,cells,uid in [('left',[0,0,1,1],'old-a'),('right',[1,0,2,1],'old-b')]}
        records=[dict(url=url,sha256=url,coarseCells=row['coarseCells'],targetUids=row['meta']['targetUids']) for url,row in old.items()]
        candidate=dict(nativeMesh={'source':{}},coarseCells=[0,0,2,1],
            meta=dict(parentTerrain='city/data/terrain.json',parentSha256='root',targetUids=['new','old-a','old-b']))
        scope=dict(positiveAreaTerrainOverlaps=2,terrainContacts=[dict(url=url,coarseOverlapAreaM2=1,packedContacts=[]) for url in old],uids=['new','old-a','old-b'],regionalCoarseCells=[0,0,2,1])
        return scope,dict(uids=['new'],replacedNativeTerrain=records),old,candidate

    def test_complete_collection(self):
        self.assertEqual(len(verify(*self.fixture())),2)

    def test_scope_mutations_fail(self):
        def missing_record(s,r,o,c):r['replacedNativeTerrain'].pop()
        def missing_old_target(s,r,o,c):c['meta']['targetUids'].remove('old-b')
        def unrelated_target(s,r,o,c):c['meta']['targetUids'].append('unrelated')
        def extra_overlap(s,r,o,c):s['terrainContacts'].append(dict(url='third',coarseOverlapAreaM2=1,packedContacts=[]));s['positiveAreaTerrainOverlaps']=3
        def duplicate_record(s,r,o,c):r['replacedNativeTerrain'].append(copy.deepcopy(r['replacedNativeTerrain'][0]))
        def truncated_domain(s,r,o,c):c['coarseCells']=[0,0,1,1];s['regionalCoarseCells']=[0,0,1,1]
        def different_root(s,r,o,c):o['right']['meta']['parentSha256']='other-root'
        def rewritten_old_targets(s,r,o,c):o['right']['meta']['targetUids']=['replacement-uid']
        def hidden_coordinated_group(s,r,o,c):o['right']['nativeMesh']['source']['coordinatedBoundary']={'member':1}
        for mutate in [missing_record,missing_old_target,unrelated_target,extra_overlap,duplicate_record,truncated_domain,different_root,rewritten_old_targets,hidden_coordinated_group]:
            with self.subTest(mutation=mutate.__name__):
                values=self.fixture();mutate(*values)
                with self.assertRaises(AssertionError):verify(*values)


if __name__=='__main__':unittest.main()
