"""Source preservation, marine cut, model anchoring and approximation boundaries."""
import hashlib,json,pathlib,sys,unittest
import numpy as np
from shapely.geometry import Polygon,Point,LineString
from shapely.ops import unary_union
ROOT=pathlib.Path(__file__).resolve().parents[3];HERE=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'docs/astra-city/mui-wo-buildings/review'));from bake_model_geometry import bake
sys.path.insert(0,str(HERE.parent/'tai-o-completion'));from hydro_terrain import height
class TsingMaTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.models=json.loads((HERE/'bridges-tsing-ma.json').read_text());cls.cables=json.loads((HERE/'cables-tsing-ma.json').read_text());cls.hydro=json.loads((HERE/'hydro-tsing-ma.json').read_text());cls.patch=json.loads((HERE/'terrain-tsing-ma.json').read_text());cls.water=unary_union([Polygon(p['rings'][0],p['rings'][1:]) for p in cls.hydro['water']]);cls.base=json.loads((ROOT/'3d-viewer/city/data/terrain.json').read_text())
 def test_six_original_components_and_hashes(self):
  self.assertEqual(len(self.models['models']),6);self.assertEqual(sum(m['modelGeometry']['triangles'] for m in self.models['models']),37970)
  for m in self.models['models']:
   g=m['modelGeometry'];assets=HERE/'assets';source=g['source'];spec={'id':g['modelId'],'url':m['sheet']+'/'+source,'sourceEntry':source,'sourceHashes':g['sourceHashes'],'worldBounds':g['worldBounds'],'officialMatches':g['officialMatches']}
   for name,sha in g['sourceHashes'].items():self.assertEqual(hashlib.sha256((assets/m['sheet']/name).read_bytes()).hexdigest(),sha)
   rebaked=bake(spec,assets)
   for key in ['position','normal','colour']:self.assertEqual(g[key],rebaked[key])
   self.assertFalse(m['walkable']);self.assertEqual(m['walkTriangleIndices'],[])
 def test_tower_source_identity_and_original_heights(self):
  matches=[r for m in self.models['models'] for r in m['buildingMatches']];self.assertEqual({r['uid'] for r in matches},{'landsd/193003:0','landsd/205933:0','landsd/194907:0','landsd/194906:0'})
  live={b['uid']:b for b in json.loads((ROOT/'3d-viewer/city/data/tiles/-5_-4.json').read_text())['buildings']}
  for m in matches:
   b=live[m['uid']];self.assertEqual(m['buildingCSUID'],b['buildingCSUID']);self.assertEqual(m['sourceBaseHeightHKPD'],b['baseHeightHKPD']);self.assertEqual(m['sourceTopHeightHKPD'],b['topHeightHKPD'])
 def test_marine_channel_and_real_island(self):
  for p in [(-9250,-6940),(-9000,-7010),(-8750,-7090),(-8500,-7160),(-8250,-7240)]:self.assertTrue(self.water.covers(Point(p)))
  for p in [(-9800,-6770),(-9500,-6860)]:self.assertFalse(self.water.covers(Point(p)))
  self.assertGreater(self.water.area,1_900_000)
 def test_cut_triangles_preserve_mapped_land_and_bed(self):
  for grid in self.hydro['terrainCuts']:
   for cell in grid['cells']:
    for t in np.array(cell['land']).reshape(-1,3,3):self.assertLess(Polygon(t[:,[0,2]]).intersection(self.water).area,.002)
  triangles=np.array(self.hydro['bedTriangles']).reshape(-1,3,3);self.assertTrue(np.all(triangles[:,:,1]==-4));area=sum(Polygon(t[:,[0,2]]).area for t in triangles);self.assertAlmostEqual(area,self.water.area,places=3)
 def test_source_ground_replaces_only_staged_ridge(self):
  self.assertGreater(height(self.base,-9500,-6860),30);self.assertAlmostEqual(height(self.patch,-9500,-6860),6.785,places=3);self.assertLess(height(self.patch,-9800,-6770),5)
  report=json.loads((ROOT/'docs/astra-city/tsing-ma/terrain-source-audit.json').read_text());self.assertEqual(len(report['samples']),7)
  for s in report['samples']:self.assertEqual(s['originalExpectedRoundedMean'],s['coarseOriginalRaw'])
 def test_illustrative_cables_are_separate_and_outward(self):
  c=self.cables;self.assertTrue(c['estimatedGeometry']);self.assertEqual(c['counts']['originalSourceModels'],0);self.assertEqual(c['counts']['mainCables'],2);self.assertEqual(c['counts']['illustrativeHangers'],152)
  for s in c['spans']:self.assertLess(abs(s['horizontalSpanMetres']-1377),.5)
  t=np.array(c['modelGeometry']['position']).reshape(-1,3,3);n=np.array(c['modelGeometry']['normal']).reshape(-1,3,3);cross=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);self.assertTrue(np.all(np.sum(cross*n.mean(axis=1),axis=1)>0))
  for p in c['parts']:
   if p['role']=='hanger':self.assertLess(p['path'][0][1],p['path'][1][1])
 def test_partial_approach_geometry_is_not_dropped(self):
  clips=self.models['proxyClips'];self.assertEqual(len(clips),2);bs={b['id']:b for b in json.loads((ROOT/'3d-viewer/city/data/bridges.json').read_text())['bridges']}
  for c in clips:
   self.assertGreater(c['retainedLengthMetres'],89);self.assertLess(c['retainedLengthMetres'],91);line=LineString(bs[c['id']]['path']);length=0
   for path in c['keepPaths']:
    length+=LineString(path).length
    for p in path:self.assertLess(line.distance(Point(p)),1e-6)
   self.assertAlmostEqual(length,c['retainedLengthMetres'],places=6)
 def test_patch_boundary_uses_existing_rendered_heights(self):
  d=self.patch;g=d['meta']['georef'];w,h=d['w'],d['h']
  for c,r in [(i,0) for i in range(w)]+[(i,h-1) for i in range(w)]+[(0,j) for j in range(h)]+[(w-1,j) for j in range(h)]:
   x=g['bE']+c*5-834500;z=816500-g['bN']+r*5;self.assertAlmostEqual(height(d,x,z),height(self.base,x,z),delta=1e-5)
if __name__=='__main__':unittest.main()
