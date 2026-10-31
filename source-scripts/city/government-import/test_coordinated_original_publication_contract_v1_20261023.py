import copy,unittest
from coordinated_original_publication_contract_v1_20261023 import pair_layout,manifest_pair_transition

class AtomicPairTests(unittest.TestCase):
    def setUp(self):
        self.reviewed=[dict(url=u,sha256=u+'-old',retainedUids=[u])for u in ['south','north']]
        self.tested=[dict(replaces=r,sha256=r['url']+'-new',resolution=5)for r in self.reviewed]
        self.planned=[dict(t,destination='new-'+t['replaces']['url'])for t in self.tested]
        self.before=dict(terrainPatches=[dict(url='elsewhere'),dict(url='south'),dict(url='north')],counts={'models':10},tiles=['tile'])
        self.after=dict(terrainPatches=[dict(url='elsewhere'),dict(url='new-south'),dict(url='new-north')],counts={'models':10},tiles=['tile'])
    def test_complete_pair(self):
        self.assertEqual(pair_layout(self.tested,self.planned,self.reviewed),({'south','north'},{'new-south','new-north'}));manifest_pair_transition(self.before,self.after,self.planned)
    def test_half_plan_rejected(self):
        with self.assertRaises(AssertionError):pair_layout(self.tested,self.planned[:1],self.reviewed)
    def test_changed_tested_bytes_rejected(self):
        p=copy.deepcopy(self.planned);p[1]['sha256']='untested'
        with self.assertRaises(AssertionError):pair_layout(self.tested,p,self.reviewed)
    def test_lost_retained_targets_rejected(self):
        p=copy.deepcopy(self.planned);p[1]['replaces']['retainedUids']=[]
        with self.assertRaises(AssertionError):pair_layout(self.tested,p,self.reviewed)
    def test_same_destination_rejected(self):
        p=copy.deepcopy(self.planned);p[1]['destination']=p[0]['destination']
        with self.assertRaises(AssertionError):pair_layout(self.tested,p,self.reviewed)
    def test_half_publication_rejected(self):
        a=copy.deepcopy(self.after);a['terrainPatches'][2]={'url':'north'}
        with self.assertRaises(AssertionError):manifest_pair_transition(self.before,a,self.planned)
    def test_unrelated_terrain_loss_rejected(self):
        a=copy.deepcopy(self.after);a['terrainPatches'][0]={'url':'unreviewed'}
        with self.assertRaises(AssertionError):manifest_pair_transition(self.before,a,self.planned)
    def test_base_map_mutation_rejected(self):
        for field,value in [('counts',{'models':11}),('tiles',['other'])]:
            a=copy.deepcopy(self.after);a[field]=value
            with self.assertRaises(AssertionError):manifest_pair_transition(self.before,a,self.planned)

if __name__=='__main__':unittest.main()
