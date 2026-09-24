"""Focused source/projection, preservation and bounded refinement regressions."""
import hashlib,unittest,zipfile
import numpy as np
from shapely import STRtree
from shapely.geometry import Polygon
from audit import ROOT,HERE,DOC,OUT,load,sha,source_piece_audit
class RefinementChecks(unittest.TestCase):
 def test_native_plane_clipping_preserves_holes(self):
  tri=np.array([[0,0,0],[10,10,0],[0,0,10]],dtype=float);footprint=Polygon([(0,0),(10,0),(0,10)],[[(6,1),(7,1),(7,2),(6,2)]])
  metrics,_,_=source_piece_audit(footprint,5,(np.array([tri]),STRtree([Polygon(tri[:,[0,2]])])))
  self.assertAlmostEqual(metrics['coverageArea'],49);self.assertAlmostEqual(metrics['areaAboveHighestRoofPlusTolerance'],.5*4.9**2-1)
 def test_exact_case_set_and_six_derived_flags_clear(self):
  original=load(DOC/'exact-source-audit.json');staged=load(DOC/'refinement-staging.json');self.assertEqual(original['counts'],{'cases':13,'currentPartial':13,'nativeHighestRoofPartial':7})
  targets={r['uid'] for p in staged['patches'] for r in p['cases']};self.assertEqual(targets,{'landsd/174150:0','landsd/195964:0','landsd/201705:0','landsd/206484:0','landsd/206970:0','landsd/336510:0'})
  self.assertEqual(staged['resolvedHighestRoofFlags'],6);self.assertTrue(all(not r['stillPartial'] for p in staged['patches'] for r in p['cases']))
 def test_parent_and_downloaded_source_members_unchanged(self):
  data=load(HERE/'terrain-refinements.json');self.assertEqual(sha(OUT/'terrain-mui-wo.json'),data['parentSha256']);download=load(HERE/'sources/10-SW-8C/download.json')
  self.assertEqual(download['memberPrefixes'],['TERRAIN']);self.assertEqual(len(download['entries']),2)
  with zipfile.ZipFile(HERE/'sources/10-SW-8C/10-SW-8C.zip') as z:
   for entry in download['entries']:
    self.assertTrue(entry['name'].startswith('TERRAIN'));self.assertEqual(hashlib.sha256(z.read(entry['name'])).hexdigest(),entry['sha256'])
  self.assertEqual(load(HERE/'staged/10-SW-8C/manifest.json')['models'],[])
 def test_disjoint_parent_edges_and_neighbours(self):
  r=load(DOC/'neighbour-seam-checks.json');self.assertEqual(r['seamChecks'],2180);self.assertLess(r['maximumBoundaryErrorMetres'],1e-6);self.assertEqual(r['neighbourForms'],25);self.assertEqual(r['newWholeConflicts'],[]);self.assertEqual(r['newPartialConflicts'],[])
 def test_only_two_null_height_estimates_need_refreshed_bases(self):
  updates=load(HERE/'building-estimate-updates.json');self.assertEqual(updates['refinementSha256'],sha(HERE/'terrain-refinements.json'));self.assertEqual({b['uid'] for b in updates['buildings']},{'landsd/173217:0','landsd/173237:0'})
  for b in updates['buildings']:
   current=next(r for r in load(OUT/'tiles'/(b['tile']+'.json'))['buildings'] if r['uid']==b['uid'])
   self.assertEqual(current['base'],b['previousBase']);self.assertEqual(current['buildingCSUID'],b['buildingCSUID']);self.assertIsNone(current['baseHeightHKPD']);self.assertIsNone(current['topHeightHKPD']);self.assertNotIn('modelGeometry',current);self.assertEqual(b['height'],current['height']);self.assertEqual(b['height'],3.5);self.assertEqual(b['baseSource'],'terrain-estimated')
  report=load(DOC/'neighbour-seam-checks.json');self.assertEqual(report['newFloatingBasesAfterEstimateUpdates'],[]);self.assertEqual(report['diagnosticUpdates'],6)
 def test_actual_mesh_sampler_water_and_continuous_route(self):
  r=load(DOC/'runtime-checks.json');self.assertEqual(r['refinementSha256'],sha(HERE/'terrain-refinements.json'));self.assertEqual(r['checks']['vertices'],17445);self.assertEqual(r['checks']['mappedWaterNodes'],0);self.assertLess(r['checks']['maxVertexError'],.001)
  for name in ['forward','reverse']:
   route=r['route'][name];self.assertTrue(route['passed']);self.assertEqual(route['initialisations'],1);self.assertEqual(route['positionResetsAlongRoute'],0);self.assertGreater(route['distanceMetres'],4130)
if __name__=='__main__':unittest.main()
