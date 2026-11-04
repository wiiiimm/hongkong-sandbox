"""Regression contracts for source-preserving Mui Wo regional staging."""
import gzip,hashlib,json,pathlib,unittest
from shapely.geometry import Point
import numpy as np
from shapely.geometry import Polygon,box
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2];DOC=ROOT/'docs/astra-city/mui-wo-completion'
def read(p):return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
class PayloadTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.patch=read(HERE/'staged-terrain-mui-wo.json');cls.audit=read(DOC/'terrain-audit.json');cls.infra=read(HERE/'bridges-mui-wo.json')
 def test_terrain_source_coverage_and_hashes(self):
  self.assertEqual(len(self.patch['meta']['detailSources']),27)
  for s in self.patch['meta']['detailSources']:
   p=ROOT/s['file'];self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),s['sha256']);g=read(p)
   self.assertEqual(len(g['elev']),g['w']*g['h']);self.assertEqual(g['valid'],[v is not None for v in g['elev']])
  self.assertEqual(self.audit['terrainSha256'],hashlib.sha256((HERE/'staged-terrain-mui-wo.json').read_bytes()).hexdigest())
 def test_original_patch_extent_water_mask_and_outer_edge_preserved(self):
  old=read(HERE/'baseline-terrain-mui-wo.json.gz');new=self.patch
  self.assertEqual((old['w'],old['h'],old['meta']['georef']),(new['w'],new['h'],new['meta']['georef']))
  self.assertTrue(all(b<=0 for a,b in zip(old['elev'],new['elev']) if a<=0))
  changes=[i for i,(a,b) in enumerate(zip(old['elev'],new['elev'])) if (a<=0)!=(b<=0)];self.assertEqual(changes,[511567])
  import hydro
  point=Point(-15812.5,2972.5);land=[g for r,g in hydro.coast.ib5000() if r['layer']=='ContourPoly']
  self.assertTrue(all(not g.covers(point) for g in land));self.assertGreater(min(g.distance(point) for g in land),3.6)
  w,h=new['w'],new['h'];edge=[*range(w),*range((h-1)*w,h*w),*[r*w for r in range(h)],*[r*w+w-1 for r in range(h)]]
  self.assertEqual([old['elev'][i] for i in edge],[new['elev'][i] for i in edge])
 def test_roof_conflicts_and_missing_height_policy(self):
  c=self.audit['counts'];self.assertEqual((c['forms'],c['models'],c['whollyBelow'],c['partlyBelow']),(2408,1327,0,13))
  changed=[r for r in self.audit['rows'] if r['missingBaseReestimated']];self.assertEqual(len(changed),164)
  self.assertTrue(all(r['sourceBase'] is None and r['sourceTop'] is None for r in changed))
  self.assertEqual(len({r['uid'] for r in self.audit['rows']}),2408)
 def test_hydro_preserves_explicit_lower_estuary_scope(self):
  h=read(HERE/'hydro-mui-wo.json');self.assertEqual(h['illustrativeBed'],-4);self.assertFalse(h['source']['riverScope']['scopeIsTidalLimit']);self.assertEqual(h['source']['riverScope']['upstreamDisplayZ'],2024)
  self.assertEqual({r['id'] for r in h['source']['riverFeatures']},{'HydroPolygon/1104404556','HydroPolygon/1104401625'})
  self.assertTrue(all(Polygon(w['rings'][0],w['rings'][1:]).is_valid for w in h['water']))
  derived=read(HERE/'hydro-mui-wo-terrain.json');self.assertEqual(derived['water'],h['water']);self.assertEqual(derived['bounds'],h['bounds'])
 def test_infrastructure_preserves_exact_source_and_bounded_replacements(self):
  original=read(HERE/'infrastructure-models.json.gz');self.assertEqual(len(self.infra['models']),10);self.assertEqual(sum(m['modelGeometry']['triangles'] for m in self.infra['models']),8450)
  self.assertEqual([m['modelGeometry'] for m in original['models']],[m['modelGeometry'] for m in self.infra['models']]);self.assertEqual(sum(m['walkable'] for m in self.infra['models']),6)
  self.assertEqual(len(self.infra['approaches']),4);self.assertTrue(all(r['estimatedElevation'] and r['estimatedPublicApproach'] for r in self.infra['approaches']))
  full={i for m in self.infra['models'] for i in m['suppresses']};partial={r['id'] for r in self.infra['proxyClips']};self.assertEqual((len(full),len(partial),len(full&partial)),(9,16,0))
  for r in self.infra['proxyClips']:
   self.assertGreater(r['withinExactSourceProjectionMetres'],.01);self.assertAlmostEqual(r['originalLengthMetres'],r['retainedLengthMetres']+r['replacedLengthMetres']);self.assertGreater(r['retainedLengthMetres'],0)
 def test_continuous_route_and_arrivals_include_failure_controls(self):
  r=read(DOC/'route-navigation.json');self.assertTrue(r['passed']);self.assertGreater(r['forward']['distanceMetres'],4100);self.assertEqual(r['forward']['positionResetsAlongRoute'],0);self.assertEqual(r['reverse']['positionResetsAlongRoute'],0);self.assertTrue(all(not p['passed'] for p in r['negativeCases'].values()))
  a=read(DOC/'arrivals-staged.json');self.assertTrue(a['passed']);self.assertEqual(a['existingAfter'],{'walking':190,'passed':190});self.assertEqual([r['id'] for r in a['repairs']],['muiwo']);self.assertEqual(len(a['new']),5)
  self.assertTrue(read(DOC/'arrival-connection.json')['passed'])
if __name__=='__main__':unittest.main()
