"""Focused checks for sourced transforms, matching, cache provenance and mosaic joins."""
import gzip,importlib.util,json,pathlib,sys,unittest
import numpy as np
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2];REVIEW=ROOT/'docs/astra-city/mui-wo-buildings/review'
sys.path.insert(0,str(REVIEW));from prepare_model_sample import model_geometry
from terrain_mosaic import blend_sources
import tempfile
class ModelExtensionTests(unittest.TestCase):
 minimum_new_models=900
 def test_verified_models_preserve_actual_source_transform_bounds(self):
  data=json.loads(gzip.decompress((HERE/'model-geometries.json.gz').read_bytes()));self.assertGreater(data['counts']['newDetailedModels'],self.minimum_new_models);self.assertEqual(len(data['byBuildingUid']),data['counts']['matchedBuildingGeometries'])
  for uid,record in data['byBuildingUid'].items():
   folder=REVIEW/'model-sample' if record['sourceTile']=='10-SW-12C' else HERE/'staged'/record['sourceTile'];path=folder/record['source'];gltf=json.loads(path.read_text())
   source,triangles=model_geometry(gltf,lambda uri:(path.parent/uri).read_bytes());position=np.array(record['position']).reshape(-1,3);normal=np.array(record['normal']).reshape(-1,3)
   np.testing.assert_allclose(position.min(axis=0),source.min(axis=0),atol=1e-9);np.testing.assert_allclose(position.max(axis=0),source.max(axis=0),atol=1e-9);self.assertEqual(len(position)//3,triangles)
   self.assertTrue(np.isfinite(position).all() and np.isfinite(normal).all());self.assertEqual(record['buildingCSUID'],record['officialMatches'][0]['buildingCSUID'])
   self.assertEqual(uid,'landsd/'+str(record['officialMatches'][0]['objectId'])+':0')
 def test_adjacent_terrain_sources_do_not_blend_back_to_dtm_internally(self):
  with tempfile.TemporaryDirectory() as temp:
   root=pathlib.Path(temp);paths=[]
   for n in range(2):
    data={'w':10,'h':10,'elev':[20]*100,'meta':{'georef':{'aE':5,'aN':-5,'bE':n*50,'bN':0}},'source':{'tile':str(n)}};path=root/(str(n)+'.json');path.write_text(json.dumps(data));paths.append(path)
   fine=np.full((10,20),2.);_,audit=blend_sources(fine,0,0,paths,root)
   self.assertEqual(fine[5,0],2);self.assertAlmostEqual(fine[5,1],8);self.assertEqual(fine[5,9],20);self.assertEqual(fine[5,10],20);self.assertEqual(fine[5,-1],2)
   self.assertEqual(audit['seams'][0]['maxAdjacent5mDifference'],0)
   fine=np.full((10,20),2.);fine[5,10]=0;_,water=blend_sources(fine,0,0,paths,root)
   self.assertEqual(fine[5,10],0);self.assertEqual(water['sourceNodesExcludedByExistingWaterMask'],1)
 def test_compact_cache_is_not_described_as_complete_source_archive(self):
  for path in (HERE/'sources').glob('*/download.json'):
   data=json.loads(path.read_text())
   if data.get('cacheKind'):
    self.assertIsNone(data['archiveSha256']);self.assertLess(data['transferredBytes'],data['sourceArchiveBytes']);self.assertTrue(all(e['name'].endswith(('.gltf','.bin')) for e in data['entries']))
if __name__=='__main__':unittest.main()
