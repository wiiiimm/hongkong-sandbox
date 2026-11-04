"""Focused regression checks for narrow source-TIN correction integration."""
import hashlib,json,pathlib,unittest
from terrain import HERE,ROOT,DOC,load,sha
class TerrainChecks(unittest.TestCase):
 def test_parent_unchanged_and_nested_cells(self):
  bundle=load(HERE/'terrain-refinements.json');parent=load(ROOT/'3d-viewer'/bundle['parentTerrainURL']);self.assertEqual(bundle['parentSha256'],sha(ROOT/'3d-viewer'/bundle['parentTerrainURL']));g=parent['meta']['georef']
  for p in bundle['patches']:
   c0,r0,c1,r1=p['coarseCells'];self.assertGreaterEqual(c0,0);self.assertGreaterEqual(r0,0);self.assertLess(c1,parent['w']);self.assertLess(r1,parent['h']);self.assertEqual(p['w'],(c1-c0)*5+1);self.assertEqual(p['h'],(r1-r0)*5+1);self.assertEqual(p['meta']['georef']['bE'],g['bE']+c0*5);self.assertEqual(p['meta']['georef']['bN'],g['bN']-r0*5)
 def test_full_native_coverage_and_roofs_clear(self):
  r=load(DOC/'terrain-preparation.json');self.assertEqual(len(r['rows']),2)
  for row in r['rows']:self.assertTrue(row['resolved']);self.assertEqual(row['sourceCovered'],row['gridVertices']);self.assertEqual(row['waterMaskNodesChanged'],0);self.assertLess(row['after']['max'],row['sourceRoof'])
 def test_neighbours_and_all_four_models(self):
  r=load(DOC/'terrain-verification.json');self.assertEqual(r['auditedForms'],6);self.assertEqual(sum(b['newModel'] for b in r['rows']),4);self.assertTrue(r['allFourNewModelsClear']);self.assertEqual(r['newRegressions'],[]);self.assertGreaterEqual(r['seamSamples'],700);self.assertLess(r['maxSeamErrorMetres'],1e-6)
 def test_only_missing_base_estimate_changes(self):
  updates=load(HERE/'building-estimate-updates.json');self.assertEqual(len(updates['buildings']),1);u=updates['buildings'][0];self.assertEqual(u['uid'],'landsd/182182:0');self.assertEqual(u['previousBase'],78);self.assertEqual(u['base'],75.849);self.assertEqual(u['height'],3);self.assertIsNone(u['sourceBaseHeightHKPD']);self.assertIsNone(u['sourceTopHeightHKPD']);self.assertEqual(u['heightSource'],'estimated');self.assertEqual(updates['refinementSha256'],sha(HERE/'terrain-refinements.json'))
 def test_original_terrain_source_hashes(self):
  folders=list((HERE/'terrain/staged').iterdir());self.assertEqual(len(folders),3)
  for folder in folders:
   manifest=load(folder/'manifest.json');self.assertEqual(manifest['models'],[])
   for rel,digest in manifest['terrain']['sourceHashes'].items():
    path=folder/rel
    if not path.exists():
     # stage retains original glTF in its source ZIP, while its derived untextured copy is separate.
     import zipfile
     with zipfile.ZipFile(HERE/'terrain/sources'/folder.name/(folder.name+'.zip')) as z:raw=z.read(rel)
    else:raw=path.read_bytes()
    self.assertEqual(hashlib.sha256(raw).hexdigest(),digest)
 def test_actual_runtime_and_route(self):
  r=load(DOC/'terrain-runtime.json');self.assertEqual(r['checks']['checkedVertices'],4002);self.assertEqual(r['checks']['waterChanges'],0);self.assertEqual(r['checks']['sourceModelsLoaded'],4);self.assertLess(r['checks']['maxRayError'],.002)
  for side in ['forward','reverse']:self.assertTrue(r['route'][side]['passed']);self.assertEqual(r['route'][side]['positionResetsAlongRoute'],0);self.assertGreater(r['route'][side]['distanceMetres'],555)
if __name__=='__main__':unittest.main()
