"""Source preservation, foundation protection and explicitly separate cable estimates."""
import hashlib,json,pathlib,sys,unittest,numpy as np
from shapely.geometry import Polygon,Point,LineString,MultiPoint
from shapely.ops import unary_union
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'docs/astra-city/mui-wo-buildings/review'));from bake_model_geometry import bake
sys.path.insert(0,str(HERE.parent/'tai-o-completion'));from hydro_terrain import height
class TingKauTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.data=json.loads((HERE/'bridges-ting-kau.json').read_text());cls.model=cls.data['models'][0];cls.cables=json.loads((HERE/'cables-ting-kau.json').read_text());cls.hydro=json.loads((HERE/'hydro-ting-kau.json').read_text());cls.patch=json.loads((HERE/'terrain-ting-kau.json').read_text());cls.base=json.loads((ROOT/'3d-viewer/city/data/terrain.json').read_text());cls.water=unary_union([Polygon(x['rings'][0],x['rings'][1:]) for x in cls.hydro['water']])
 def test_original_source_mesh_bytes_and_bake_unchanged(self):
  g=self.model['modelGeometry'];spec={'id':g['modelId'],'url':self.model['sheet']+'/'+g['source'],'sourceEntry':g['source'],'sourceHashes':g['sourceHashes'],'worldBounds':g['worldBounds'],'officialMatches':g['officialMatches']}
  for name,sha in g['sourceHashes'].items():self.assertEqual(hashlib.sha256((HERE/'assets'/self.model['sheet']/name).read_bytes()).hexdigest(),sha)
  rebaked=bake(spec,HERE/'assets')
  for key in ['position','normal','colour']:self.assertEqual(g[key],rebaked[key])
  self.assertEqual(g['triangles'],16995);self.assertEqual(len(self.data['models']),1)
 def test_three_towers_are_not_rendered_twice_or_moved(self):
  self.assertEqual(set(self.model['suppressesBuildingUids']),{'landsd/219323:0','landsd/219830:0','landsd/221079:0'})
  self.assertEqual(len(self.model['buildingMatches']),3)
  for row in self.model['buildingMatches']:
   self.assertEqual(row['buildingCSUID'][:10],row['identityModel'][1:11]);self.assertGreater(row['overlapOfSmallerFootprint'],.8);self.assertGreater(row['mainInfrastructureTowerTopHKPD'],150)
  self.assertFalse(self.model['walkable']);self.assertEqual(self.model['walkTriangleIndices'],[])
 def test_proxy_replacement_covers_only_confirmed_source_bridge(self):
  original={b['id']:b for b in json.loads((ROOT/'3d-viewer/city/data/bridges.json').read_text())['bridges']};p=np.array(self.model['modelGeometry']['position']).reshape(-1,3);hull=MultiPoint(p[:,[0,2]]).convex_hull.buffer(1.5)
  self.assertEqual(len(self.model['suppresses']),13);self.assertEqual(self.data['proxyClips'],[])
  for key in self.model['suppresses']:
   self.assertEqual(original[key]['name'],'Ting Kau Bridge');self.assertLess(LineString(original[key]['path']).difference(hull).length,.001)
 def test_marine_cut_keeps_all_tower_foundations(self):
  for point in [(-8340,-8710),(-8290,-8610),(-8180,-8380),(-8140,-8300)]:self.assertTrue(self.water.covers(Point(point)))
  for point in [(-8427.765,-8887.478),(-8229.83,-8485.528),(-8019.633,-8059.256)]:self.assertFalse(self.water.covers(Point(point)))
  self.assertGreater(self.water.area,950000);self.assertLess(self.water.area,960000)
 def test_replacement_triangles_do_not_reintroduce_false_land(self):
  for grid in self.hydro['terrainCuts']:
   for cell in grid['cells']:
    for t in np.array(cell['land']).reshape(-1,3,3):self.assertLess(Polygon(t[:,[0,2]]).intersection(self.water).area,.002)
  bed=np.array(self.hydro['bedTriangles']).reshape(-1,3,3);self.assertTrue(np.all(bed[:,:,1]==-4));self.assertAlmostEqual(sum(Polygon(t[:,[0,2]]).area for t in bed),self.water.area,places=3)
 def test_original_dtm_averages_explain_inherited_ridge(self):
  report=json.loads((ROOT/'docs/astra-city/ting-kau/terrain-source-audit.json').read_text());self.assertEqual(len(report['samples']),7)
  for s in report['samples']:self.assertEqual(round(s['native14x14Mean']),s['coarseCityRaw']);self.assertEqual(s['coarseOriginalRaw'],s['coarseCityRaw'])
  marine=[s for s in report['samples'] if s['mappedWater']];self.assertTrue(any(s['coarseRenderedAtPoint']>15 for s in marine));self.assertTrue(all(s['sourceRawRange'][1]>50 for s in marine))
 def test_cable_estimates_have_distinct_fan_structure_and_outward_geometry(self):
  c=self.cables;self.assertTrue(c['estimatedGeometry']);self.assertEqual(c['counts']['originalSourceModels'],0);self.assertEqual(c['counts']['illustrativeFanStays'],334);self.assertEqual(c['counts']['illustrativeLongitudinalStays'],8)
  self.assertEqual({p['role'] for p in c['parts']},{'fan-stay','longitudinal-stay'})
  for p in c['parts']:self.assertEqual(len(p['path']),2);self.assertGreater(p['path'][0][1],p['path'][1][1]);self.assertTrue(p['estimatedGeometry'])
  t=np.array(c['modelGeometry']['position']).reshape(-1,3,3);n=np.array(c['modelGeometry']['normal']).reshape(-1,3,3);cross=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);self.assertTrue(np.all(np.sum(cross*n.mean(axis=1),axis=1)>0))
 def test_patch_boundary_matches_existing_rendered_heights(self):
  p=self.patch;g=p['meta']['georef'];w,h=p['w'],p['h']
  for c,r in [(i,0) for i in range(w)]+[(i,h-1) for i in range(w)]+[(0,j) for j in range(h)]+[(w-1,j) for j in range(h)]:
   x=g['bE']+c*5-834500;z=816500-g['bN']+r*5;self.assertAlmostEqual(height(p,x,z),height(self.base,x,z),delta=1e-5)
if __name__=='__main__':unittest.main(verbosity=2)
