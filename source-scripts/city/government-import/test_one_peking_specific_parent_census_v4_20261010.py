import copy,importlib.util,unittest
from run import ROOT,HERE,read
from one_peking_specific_parent_census_v4_20261010 import census,numeric_tree,reconstructed_numeric_equal

class ParentCensus(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parent=read(ROOT/'3d-viewer/city/data/terrain-government-xl-caine-road-original-pair-installed-v2-20261010.json')
        manifest=read(ROOT/'3d-viewer/city/data/manifest.json')
        cls.entries=[r for u in manifest['officialModelCatalogues'] for r in read(ROOT/'3d-viewer'/u)['models']]
        spec=importlib.util.spec_from_file_location('parent_census_actual_forms',HERE/'xl-final-script-pass.py')
        final=importlib.util.module_from_spec(spec);spec.loader.exec_module(final)
        g=cls.parent['meta']['georef'];p=cls.parent
        bounds=[g['bE']-834500,816500-g['bN'],g['bE']-834500+(p['w']-1)*g['aE'],816500-g['bN']-(p['h']-1)*g['aN']]
        cls.forms=[b for b,_,_ in final.load_forms(bounds)]
    def test_actual_complete_twelve(self):
        x=census(self.parent,self.entries,self.forms)
        self.assertEqual(len(x['allTargetUids']),12)
        self.assertEqual(x['currentBasicUids'],[])
        self.assertEqual(len(x['installedNativeUids']),12)
        self.assertFalse(x['physicalAccepted'])
    def test_missing_current_93890(self):
        with self.assertRaises(AssertionError):census(self.parent,self.entries,[b for b in self.forms if b['uid']!='landsd/93890:0'])
    def test_duplicate_current_target(self):
        b=next(b for b in self.forms if b['uid']=='landsd/73140:0')
        with self.assertRaises(AssertionError):census(self.parent,self.entries,self.forms+[b])
    def test_duplicate_native_entry(self):
        e=next(e for e in self.entries if e['uid']=='landsd/73140:0')
        with self.assertRaises(AssertionError):census(self.parent,self.entries+[e],self.forms)
    def test_missing_native_is_not_inferred_basic(self):
        with self.assertRaises(AssertionError):census(self.parent,[e for e in self.entries if e['uid']!='landsd/73140:0'],self.forms)
    def test_changed_child_identity(self):
        p=copy.deepcopy(self.parent);next(c for c in p['patches'] if c['id']=='government-native-central-hullett-house')['meta']['targetUids']=['landsd/93890:0']
        with self.assertRaises(AssertionError):census(p,self.entries,self.forms)
    def test_missing_child_target_metadata(self):
        p=copy.deepcopy(self.parent);del p['patches'][0]['meta']['targetUids']
        with self.assertRaises(KeyError):census(p,self.entries,self.forms)
    def test_duplicate_target_membership(self):
        p=copy.deepcopy(self.parent);p['patches'][0]['meta']['targetUids'].append('landsd/73140:0')
        with self.assertRaises(AssertionError):census(p,self.entries,self.forms)

class NumericReconstruction(unittest.TestCase):
    def fixture(self):
        return dict(elev=[1.,2.],patches=[dict(id='child',meta=dict(targetUids=['landsd/73140:0']),nativeMesh=dict(position=[0.,1.,2.],index=[0,0,0],source=dict(path='old',sha256='abc')))])
    def test_identical_complete_numbers(self):
        p=self.fixture();self.assertTrue(reconstructed_numeric_equal(p,copy.deepcopy(p))['completeNumericTerrainEqual'])
    def test_only_evidence_strings_are_not_surface_claim(self):
        p=self.fixture();q=copy.deepcopy(p);q['patches'][0]['nativeMesh']['source']['path']='new'
        result=reconstructed_numeric_equal(p,q,old_batch='old',new_batch='new');self.assertFalse(result['physicalAccepted'])
    def test_unqualified_source_hash(self):
        p=self.fixture();q=copy.deepcopy(p);q['patches'][0]['nativeMesh']['source']['sha256']='def'
        with self.assertRaises(AssertionError):reconstructed_numeric_equal(p,q,old_batch='old',new_batch='new')
    def test_unqualified_evidence_path(self):
        p=self.fixture();q=copy.deepcopy(p);q['patches'][0]['nativeMesh']['source']['path']='arbitrary'
        with self.assertRaises(AssertionError):reconstructed_numeric_equal(p,q,old_batch='old',new_batch='new')
    def test_tiny_numeric_change(self):
        p=self.fixture();q=copy.deepcopy(p);q['patches'][0]['nativeMesh']['position'][0]=2**-80
        with self.assertRaises(AssertionError):reconstructed_numeric_equal(p,q)
    def test_index_order_change(self):
        p=self.fixture();q=copy.deepcopy(p);q['patches'][0]['nativeMesh']['index'][0]=1
        with self.assertRaises(AssertionError):reconstructed_numeric_equal(p,q)
    def test_missing_grid(self):
        p=self.fixture();q=copy.deepcopy(p);del q['elev']
        with self.assertRaises(AssertionError):reconstructed_numeric_equal(p,q)
    def test_nonfinite_value(self):
        with self.assertRaises(AssertionError):numeric_tree({'a':[float('nan')]})
    def test_same_numeric_but_changed_target(self):
        p=self.fixture();q=copy.deepcopy(p);q['patches'][0]['meta']['targetUids']=['landsd/93890:0']
        with self.assertRaises(AssertionError):reconstructed_numeric_equal(p,q)

if __name__=='__main__':unittest.main()
