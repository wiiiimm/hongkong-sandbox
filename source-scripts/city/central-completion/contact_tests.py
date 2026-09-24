"""Assert retained-source alternatives and explicit remaining access limitations."""
import gzip,hashlib,importlib.util,json,math,pathlib,unittest
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2];DOC=ROOT/'docs/astra-city/central-completion'
spec=importlib.util.spec_from_file_location('existing_candidate_tests',HERE/'route-candidates-test.py');original=importlib.util.module_from_spec(spec);spec.loader.exec_module(original)
class AlternativeSourceTests(original.CandidateTests):
 @classmethod
 def setUpClass(cls):
  super().setUpClass();cls.payload=json.loads((DOC/'route-alternatives.json').read_text());cls.audit=json.loads((DOC/'contact-edge-audit.json').read_text())
 def test_all_bridges_remain_explicit_unverified_gaps(self):
  for route in self.payload['routes']:
   self.assertEqual({s['id'] for s in route['segments'] if s['kind']=='footbridge'},{g['segment'] for g in route['gaps']});self.assertNotIn('walkCentreline',route)
   self.assertIn(route['status'],['source-connected-runtime-unverified','source-connected-partial-destination'])
 def test_original_routes_unchanged_and_blocked_segments_excluded(self):
  self.assertEqual(hashlib.sha256((DOC/'route-candidates.json').read_bytes()).hexdigest(),self.payload['originalRouteSha256'])
  self.assertEqual(hashlib.sha256((DOC/'contact-edge-audit.json').read_bytes()).hexdigest(),self.payload['edgeAuditSha256'])
  self.assertEqual(hashlib.sha256((HERE/'pedestrian-network.json.gz').read_bytes()).hexdigest(),self.audit['sourceSha256'])
  blocked=set(self.audit['blocked'])|set(self.audit['outsideIds'])
  for route in self.payload['routes']:self.assertFalse({s['id'] for s in route['segments']}&blocked)
 def test_tamar_interior_is_explicitly_unresolved(self):
  self.assertEqual([f['route'] for f in self.payload['failures']],['central-waterfront'])
  approach=next(r for r in self.payload['routes'] if r['id']=='central-waterfront-approach');self.assertEqual(approach['unresolvedDestination']['title'],'Tamar Park')
  self.assertGreater(math.dist(approach['anchors'][-1]['sourceWorldXYZ'],approach['unresolvedDestination']['hintWorldXYZ']),80)
 def test_actual_geometry_audit_clears_alternatives(self):
  report=json.loads((DOC/'contact-model-audit.json').read_text());self.assertEqual(len(report['models']),5)
  alternatives=[r for r in report['routes'] if r['version']=='alternative'];self.assertEqual(len(alternatives),3)
  for r in alternatives:self.assertEqual(r['existingBuildingContactSamples'],0);self.assertEqual(r['availableContactModelSurfaceHits'],[])
class CurvedPodiumMatchTests(unittest.TestCase):
 def test_source_identity_and_raw_heights_preserved(self):
  proof=json.loads((DOC/'west-wing-match.json').read_text());record=json.loads((HERE/'compact-followup/catalogue.json').read_text())['models'][0]
  rows=json.loads(gzip.decompress((HERE/'building-selection.json.gz').read_bytes()))['buildings'];b=next(b for b in rows if b['uid']==record['uid'])
  self.assertEqual(record['buildingCSUID'],b['buildingCSUID']);self.assertEqual(proof['sourceAttributes'],b['sourceAttributes'])
  self.assertEqual((record['recordedBaseHeight'],record['recordedTopHeight']),(4.8,16));self.assertGreater(record['worldBounds'][1][1],20)
  self.assertEqual(record['triangles'],46918);self.assertEqual(hashlib.sha256((HERE/'compact-followup'/record['asset']).read_bytes()).hexdigest(),record['sha256'])
 def test_actual_shape_passes_same_match_thresholds(self):
  proof=json.loads((DOC/'west-wing-match.json').read_text());self.assertTrue(proof['uniqueGeoRefMatch']);self.assertGreater(proof['originalConvexHullScreen']['centroidDistanceMetres'],10)
  self.assertLess(proof['actualSourceProjection']['centroidDistanceMetres'],10);self.assertGreater(proof['actualSourceProjection']['overlapOfSmallerFootprint'],.95)
if __name__=='__main__':unittest.main()
