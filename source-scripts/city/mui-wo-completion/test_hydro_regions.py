import copy,json,pathlib,sys,unittest
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(HERE.parent))
from hydro_regions import combine,regions_of,compose_terrain
class HydroRegionsTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.base=json.loads((ROOT/'3d-viewer/city/data/terrain.json').read_text());cls.tai=next(r for r in regions_of(cls.base['hydro']) if r['region']=='tai-o');cls.mui=json.loads((HERE/'hydro-mui-wo-terrain.json').read_text());cls.tsing={'schemaVersion':1,'region':'third-fixture','bounds':[20000,20000,20020,20020],'illustrativeBed':-4,'source':{'reference':'synthetic third-region fixture'},'water':[],'terrainCuts':[],'bedTriangles':[],'bankTriangles':[]}
 def test_legacy_single_region_is_unchanged(self):self.assertIs(combine([self.tai]),self.tai)
 def test_three_regions_reconstruct_exact_sources_without_geometry_duplication(self):
  values=[self.tai,self.mui,self.tsing];out=combine(values);self.assertEqual(regions_of(out),values);self.assertEqual(len(out['water']),sum(len(v['water']) for v in values));self.assertTrue(all('water' not in r and 'terrainCuts' not in r for r in out['regions']));self.assertEqual(out['regions'][0]['source'],self.tai['source'])
 def test_update_is_idempotent_and_preserves_other_regions(self):
  out=combine([self.tai,self.mui,self.tsing]);self.assertEqual(combine([out,self.mui]),out);new=compose_terrain(self.base,[self.mui,self.tsing]);self.assertEqual({k:v for k,v in new.items() if k!='hydro'},{k:v for k,v in self.base.items() if k!='hydro'})
 def test_overlapping_scopes_fail_without_silent_last_cut_wins(self):
  overlap=copy.deepcopy(self.tai);overlap['region']='overlap'
  with self.assertRaisesRegex(ValueError,'Overlapping hydro study bounds'):combine([self.tai,overlap])
 def test_overlapping_cut_cells_fail_even_with_disjoint_scopes(self):
  other=copy.deepcopy(self.mui);other['terrainCuts'][0]['cells']=[copy.deepcopy(self.tai['terrainCuts'][0]['cells'][0])]
  with self.assertRaisesRegex(ValueError,'Overlapping terrain cut ownership'):combine([self.tai,other])
if __name__=='__main__':unittest.main()
