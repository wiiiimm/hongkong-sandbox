"""Meaningful geometric and publication-boundary checks for model integration."""
import hashlib, unittest
import numpy as np
from shapely.geometry import box
from run import HERE,DOC,load
from placement import upper_envelope,surface_contacts

def square(y):
 return np.array([[[0,y,0],[2,y,0],[0,y,2]],[[2,y,0],[2,y,2],[0,y,2]]],dtype=float)
class PlacementTests(unittest.TestCase):
 def test_lower_floor_is_not_a_roof(self):
  surfaces=upper_envelope(np.concatenate([square(0),square(10)]));self.assertAlmostEqual(sum(p.area for _,p in surfaces),4);self.assertTrue(all(np.all(t[:,1]==10) for t,p in surfaces))
 def test_coplanar_duplicates_are_not_double_counted(self):
  surfaces=upper_envelope(np.concatenate([square(10),square(10)]));self.assertAlmostEqual(sum(p.area for _,p in surfaces),4)
 def test_sloped_terrain_intersection_is_exact(self):
  ground=square(0);ground[:,:,1]=ground[:,:,0];contacts=surface_contacts(upper_envelope(square(1)),ground)
  self.assertAlmostEqual(contacts['maximumTerrainMinusRoof'],1);self.assertAlmostEqual(contacts['terrainAboveRoofArea'],1.8);self.assertAlmostEqual(contacts['coveredArea'],4)
 def test_publication_accounting_and_geometry_unchanged(self):
  s=load(DOC/'publication-screen.json');c=load(HERE/'publication/catalogue.json');original={r['uid']:r for r in load(HERE/'compact/catalogue.json')['models']}
  self.assertEqual(s['acceptedModels'],291);self.assertEqual(s['heldModels'],21);self.assertEqual(set(s['acceptedUids'])|set(s['heldUids']),set(original));self.assertFalse(set(s['acceptedUids'])&set(s['heldUids']))
  self.assertEqual({r['uid'] for r in c['models']},set(s['acceptedUids']))
  for r in c['models']:
   for k,v in original[r['uid']].items():self.assertEqual(r[k],v)
   self.assertEqual(hashlib.sha256((HERE/'publication'/r['asset']).read_bytes()).hexdigest(),r['sha256'])
 def test_patch_guards_and_source_preservation(self):
  bundle=load(HERE/'terrain-refinements.json');estimates=load(HERE/'building-estimate-updates.json');diagnostics=load(HERE/'diagnostic-updates.json');digest=hashlib.sha256((HERE/'terrain-refinements.json').read_bytes()).hexdigest()
  self.assertEqual(len(bundle['patches']),3);self.assertEqual(estimates['parentSha256'],bundle['parentSha256']);self.assertEqual(estimates['refinementSha256'],digest);self.assertEqual(diagnostics['refinementSha256'],digest)
  self.assertEqual({b['uid'] for b in estimates['buildings']},{'landsd/173217:0','landsd/173237:0'});self.assertTrue(all(b['sourceBaseHeightHKPD'] is None and b['sourceTopHeightHKPD'] is None for b in estimates['buildings']))
  rects=[]
  for p in bundle['patches']:
   g=p['meta']['georef'];rects.append(box(g['bE'],g['bN']-p['h']+1,g['bE']+p['w']-1,g['bN']))
  for i,a in enumerate(rects):
   for b in rects[i+1:]:self.assertEqual(a.intersection(b).area,0)
 def test_neighbours_and_seams(self):
  s=load(DOC/'publication-screen.json');self.assertGreaterEqual(s['seamChecks'],1000);self.assertLess(s['maximumBoundaryError'],1e-5);self.assertEqual(s['newWholeNeighbourConflicts'],[]);self.assertEqual(s['newPartialNeighbourConflicts'],[]);self.assertEqual(s['newFloatingNeighbourFlags'],[])
 def test_repaired_representatives_and_podium_support(self):
  s=load(DOC/'publication-screen.json');rows={r['uid']:r for r in s['rows']}
  for uid in ['landsd/202951:0','landsd/206970:0','landsd/208041:0']:self.assertTrue(rows[uid]['accepted'])
  self.assertGreater(rows['landsd/206970:0']['previousRoof']['maximumTerrainMinusRoof'],5);self.assertLess(rows['landsd/206970:0']['roof']['maximumTerrainMinusRoof'],0)
  for uid in ['landsd/76963:0','landsd/95569:0','landsd/257187:0','landsd/261085:0']:
   r=rows[uid];self.assertTrue(r['accepted']);self.assertTrue(r['mappedPodiumSupports']);self.assertTrue(all(p['sourceRoofSupportCoverage']>=.95 and abs(p['fallbackVerticalDifference'])<=.5 and p['uid'] in s['acceptedUids'] for p in r['mappedPodiumSupports']))
if __name__=='__main__':unittest.main()
