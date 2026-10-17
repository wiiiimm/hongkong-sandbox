"""Reuse exact-source model tests and add bounded Pui O preservation guards."""
import gzip,json,sys,unittest
from run import HERE,ROOT,DOC,module
sys.path.insert(0,str(HERE.parent/'mui-wo-models'))
shared=module('shared_model_tests',HERE.parent/'mui-wo-models/test_models.py');shared.HERE=HERE
class PuiOModels(shared.ModelExtensionTests):
 minimum_new_models=680
 def test_scoped_counts_and_original_source_fields(self):
  selection=json.loads(gzip.decompress((HERE/'building-selection.json.gz').read_bytes()))['buildings'];models=json.loads(gzip.decompress((HERE/'model-geometries.json.gz').read_bytes()))['byBuildingUid'];original={b['uid']:b for b in selection}
  self.assertEqual(len(original),919);self.assertEqual(len(models),681)
  for uid,m in models.items():
   b=original[uid];match=m['officialMatches'][0]
   self.assertEqual(b['objectId'],match['objectId']);self.assertEqual(b['buildingCSUID'],m['buildingCSUID']);self.assertEqual(b['baseHeightHKPD'],match['sourceBaseHeight']);self.assertEqual(b['topHeightHKPD'],match['sourceTopHeight'])
   self.assertNotIn('modelGeometry',b)
  report=json.loads((DOC/'terrain-audit.json').read_text());self.assertEqual(report['counts']['baseEstimatesChanged'],140)
  for r in report['rows']:
   if r['baseEstimateChanged']:self.assertIsNone(r['sourceBaseHeight']);self.assertIsNone(r['sourceTopHeight'])
 def test_source_terrain_coverage_and_residual_conflicts_are_explicit(self):
  source=json.loads((DOC/'source-audit.json').read_text());self.assertEqual(source['counts']['noOwnTINAtCentre'],0);self.assertEqual(source['counts']['roofBelowOwnSourceTIN'],0)
  self.assertEqual(sum(r['paired'] for r in source['seams']),540);self.assertLess(max(r['maxMetres'] for r in source['seams']),.07)
  audit=json.loads((DOC/'terrain-audit.json').read_text());self.assertEqual((audit['counts']['whollyBelow'],audit['counts']['partlyBelow']),(1,2));self.assertEqual(len(audit['unmatched']),4)
 def test_staged_route_uses_continuous_navigation_with_safe_existing_arrivals(self):
  report=json.loads((DOC/'route-navigation.json').read_text());self.assertTrue(report['passed']);self.assertFalse(report['negativeHighWater']['passed'])
  for direction in ['forward','reverse']:
   self.assertTrue(report[direction]['passed']);self.assertGreater(report[direction]['distanceMetres'],550);self.assertEqual(report[direction]['positionResetsAlongRoute'],0);self.assertEqual(report[direction]['initialisations'],1)
  for r in report['arrivals'].values():self.assertTrue(r['accepted']);self.assertEqual(r['relocatedMetres'],0)
if __name__=='__main__':unittest.main()
