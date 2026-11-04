import copy,unittest
from original_disjoint_routing_metadata_scope_20261010 import boundaries,verify_boundaries

class RoutingScope(unittest.TestCase):
 def fixture(self):
  e={'url':'city/data/remote-terrain.json','source':{'files':[{'path':'old.bin','sha256':'a'*64}]}}
  return {'immutableTerrainProposal':{'bounds':[0,0,2,2]},'completeCurrentTerrainRouting':[{'entry':e,'asset':{'path':'3d-viewer/city/data/remote-terrain.json','sha256':'b'*64},'testedBounds':[[10,10,12,12]]}]},{'terrainPatches':[copy.deepcopy(e)]}
 def test_only_archived_source(self):
  p,m=self.fixture();r=boundaries(p,m);self.assertEqual(verify_boundaries(p,m,r),{'/completeCurrentTerrainRouting/0/entry/source'})
 def test_no_source_no_boundary(self):
  p,m=self.fixture();del p['completeCurrentTerrainRouting'][0]['entry']['source'];del m['terrainPatches'][0]['source'];self.assertEqual(boundaries(p,m),[])
 def test_tampered_acquisition(self):
  p,m=self.fixture();r=boundaries(p,m);p['completeCurrentTerrainRouting'][0]['entry']['source']['files'][0]['sha256']='c'*64
  with self.assertRaises(AssertionError):verify_boundaries(p,m,r)
 def test_omitted_entry(self):
  p,m=self.fixture();p['completeCurrentTerrainRouting']=[]
  with self.assertRaises(AssertionError):boundaries(p,m)
 def test_touches_is_not_disjoint(self):
  p,m=self.fixture();p['completeCurrentTerrainRouting'][0]['testedBounds']=[[2,0,3,1]]
  with self.assertRaises(AssertionError):boundaries(p,m)
 def test_missing_measured_bounds(self):
  p,m=self.fixture();p['completeCurrentTerrainRouting'][0]['testedBounds']=[]
  with self.assertRaises(AssertionError):boundaries(p,m)
 def test_cannot_leaf_numeric_asset(self):
  p,m=self.fixture();r=boundaries(p,m);r[0]['pointer']='/completeCurrentTerrainRouting/0/asset'
  with self.assertRaises(AssertionError):verify_boundaries(p,m,r)
 def test_nan_bounds_rejected(self):
  p,m=self.fixture();p['completeCurrentTerrainRouting'][0]['testedBounds'][0][0]=float('nan')
  with self.assertRaises(AssertionError):boundaries(p,m)
 def test_wrong_numeric_asset_path(self):
  p,m=self.fixture();p['completeCurrentTerrainRouting'][0]['asset']['path']='source-scripts/city/provider.gltf'
  with self.assertRaises(AssertionError):boundaries(p,m)
 def test_asset_omission(self):
  p,m=self.fixture();del p['completeCurrentTerrainRouting'][0]['asset']
  with self.assertRaises(KeyError):boundaries(p,m)
if __name__=='__main__':unittest.main()
