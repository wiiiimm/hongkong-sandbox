import copy,unittest
from original_independent_atomic_contract_v1_20261027 import verify_metadata,verify_existing_atomic_group,triple_layout,manifest_triple_transition
class IndependentAtomic(unittest.TestCase):
    def setUp(self):
        self.sources={'landsd/a:0':'a'*64,'landsd/b:0':'b'*64}
        self.original={u:dict(uid=u,sha256=s,rootTranslation=[-834500,0,816500],asset='old/'+s+'.gz',modelId=u)for u,s in self.sources.items()}
        self.models=[dict(e,asset='assets/'+e['sha256']+'.glb.gz',priority='landmark',proceduralWindows=False,activationGroup=sorted(self.sources))for e in self.original.values()]
    def verify(self):return verify_metadata(self.models,self.sources,self.original,list(self.sources))
    def test_both_independent_roots_pass(self):self.assertTrue(self.verify())
    def test_missing_atomic_peer_fails(self):
        self.models[0]['activationGroup']=self.models[0]['activationGroup'][:1]
        with self.assertRaises(AssertionError):self.verify()
    def test_invented_support_fails(self):
        self.models[0]['supportDependencies']=[dict(uid='landsd/b:0',state='installed')]
        with self.assertRaises(AssertionError):self.verify()
    def test_source_pose_edit_fails(self):
        self.models[0]['verticalPlacementOffsetHKPD']=.1
        with self.assertRaises(AssertionError):self.verify()
    def test_original_basic_suppression_fails(self):
        self.models[0]['suppressesBuildingUids']=['landsd/x:0']
        with self.assertRaises(AssertionError):self.verify()
    def test_source_byte_change_fails(self):
        self.models[0]['sha256']='c'*64
        with self.assertRaises(AssertionError):self.verify()
    def test_ground_owner_cannot_be_omitted(self):
        with self.assertRaises(AssertionError):verify_metadata(self.models,self.sources,self.original,['landsd/a:0'])
class ExistingAtomic(IndependentAtomic):
    def setUp(self):
        super().setUp()
        self.old={'landsd/existing:0':dict(uid='landsd/existing:0',sha256='e'*64,asset='original.glb.gz',placementReviewed=False,publicationApproved=False,supportDependencies=[])}
        self.after=copy.deepcopy(self.old);self.group=sorted(set(self.sources)|set(self.old))
        self.after['landsd/existing:0']['activationGroup']=self.group
        for model in self.models:model['activationGroup']=self.group
    def verify(self):return verify_existing_atomic_group(self.models,self.sources,self.original,list(self.sources),self.old,self.after)
    def test_existing_negative_flags_stay_unchanged(self):self.assertTrue(self.verify())
    def test_existing_review_flag_change_is_rejected(self):
        self.after['landsd/existing:0']['publicationApproved']=True
        with self.assertRaises(AssertionError):self.verify()
    def test_existing_asset_change_is_rejected(self):
        self.after['landsd/existing:0']['asset']='moved.glb.gz'
        with self.assertRaises(AssertionError):self.verify()
    def test_existing_group_cannot_be_broken(self):
        self.old['landsd/existing:0']['activationGroup']=['landsd/existing:0','landsd/other:0']
        with self.assertRaises(AssertionError):self.verify()
    def test_existing_member_annotation_is_required(self):
        self.after['landsd/existing:0'].pop('activationGroup')
        with self.assertRaises(AssertionError):self.verify()

class TripleTransition(unittest.TestCase):
    def setUp(self):
        self.review=[dict(url='old'+str(i),sha256=str(i))for i in range(3)]
        self.tested=[dict(replaces=r,sha256=str(i+3),resolution=5)for i,r in enumerate(self.review)]
        self.planned=[dict(r,destination='new'+str(i))for i,r in enumerate(self.tested)]
        self.before=dict(terrainPatches=[dict(url=r['url'])for r in self.review]+[dict(url='retained')],counts=dict(a=1),tiles=['tile'])
        self.after=dict(self.before,terrainPatches=[dict(url='retained')]+[dict(url=r['destination'])for r in self.planned])
    def test_complete_layout_and_transition_pass(self):
        triple_layout(self.tested,self.planned,self.review);manifest_triple_transition(self.before,self.after,self.planned)
    def test_missing_terrain_mate_fails(self):
        with self.assertRaises(AssertionError):triple_layout(self.tested[:2],self.planned[:2],self.review[:2])
    def test_retained_manifest_entry_change_fails(self):
        self.after['terrainPatches'][0]['url']='changed'
        with self.assertRaises(AssertionError):manifest_triple_transition(self.before,self.after,self.planned)
    def test_model_counts_change_fails(self):
        self.after['counts']=dict(a=2)
        with self.assertRaises(AssertionError):manifest_triple_transition(self.before,self.after,self.planned)
if __name__=='__main__':unittest.main()
