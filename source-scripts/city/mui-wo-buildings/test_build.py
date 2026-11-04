"""Source-completeness, geometric fidelity and honest elevation tests for HKS-164."""
import importlib.util,math,unittest,urllib.parse
from collections import Counter
from pathlib import Path
from shapely.geometry import Polygon,Point
from shapely.strtree import STRtree
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('muiwo',HERE/'build.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class OfficialBuildings(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.source=m.read(HERE/'landsd-mui-wo.json.gz');cls.result=m.read(m.OUT);cls.raw={f['attributes']['OBJECTID']:f for f in cls.source['features']};cls.output=cls.result['buildings']
  baseline=m.read(HERE/'osm-baseline.json.gz')['buildings'];cls.osm=[Polygon(b['rings'][0],b['rings'][1:]) for b in baseline];cls.tree=STRtree(cls.osm)
 def test_complete_ids_count_and_exact_query_envelope(self):
  ids=m.read(HERE/'query-object-ids.json')['objectIds'];count=m.read(HERE/'query-count.json')['count']
  self.assertEqual(count,2408);self.assertEqual(len(set(ids)),count);self.assertEqual(set(ids),set(self.raw));self.assertEqual(set(ids),{b['objectId'] for b in self.output});self.assertEqual(len(self.output),count)
  self.assertEqual(len({b['uid'] for b in self.output}),count)
  query=next(q for q in m.read(HERE/'requests.json') if q.get('file')=='query-object-ids.json')['url'];args=urllib.parse.parse_qs(urllib.parse.urlparse(query).query)
  self.assertEqual(list(map(float,args['geometry'][0].split(','))),[113.97922444961371,22.249711576500182,114.0180525556901,22.28564402349982]);self.assertEqual(args['inSR'],['4326'])
 def test_all_types_names_and_null_fields_preserved(self):
  self.assertEqual(Counter(b['structureType'] for b in self.output),Counter(f['attributes']['BuildingBlockType'] for f in self.raw.values()))
  for b in self.output:self.assertEqual(b['sourceAttributes'],self.raw[b['objectId']]['attributes'])
  self.assertEqual(sum(not b['name'] and not b['zh'] for b in self.output),2185)
 def test_native_geometry_holes_and_world_projection(self):
  for b in self.output:
   actual=Polygon(b['rings'][0],b['rings'][1:]);expected,_=m.official_geometry(self.raw[b['objectId']])
   self.assertTrue(actual.is_valid);self.assertLess(actual.hausdorff_distance(expected),.000708);self.assertLess(actual.symmetric_difference(expected).area,expected.length*.000708+.00001)
   self.assertEqual(len(b['rings']),1+len(expected.interiors));self.assertGreater(b['sourceArea'],0)
 def test_recorded_absolute_heights_never_raised(self):
  for b in self.output:
   a=self.raw[b['objectId']]['attributes'];self.assertEqual(b['baseHeightHKPD'],a['BaseHeight']);self.assertEqual(b['topHeightHKPD'],a['TopHeight']);self.assertEqual(b['minimum'],0)
   if a['BaseHeight'] is not None and a['TopHeight'] is not None and a['TopHeight']>a['BaseHeight']:
    self.assertEqual(b['base'],a['BaseHeight']);self.assertAlmostEqual(b['base']+b['height'],a['TopHeight']);self.assertEqual(b['heightSource'],'landsd')
   else:self.assertEqual(b['heightSource'],'estimated');self.assertTrue(b['heightRule']);self.assertTrue(b['baseSource'])
   self.assertTrue(math.isfinite(b['base']));self.assertGreater(b['height'],0)
 def test_missing_records_have_no_hidden_osm_intersections(self):
  for b in self.output:
   p=Polygon(b['rings'][0],b['rings'][1:]);hits=[p.intersection(self.osm[i]).area for i in self.tree.query(p)];hits=[a for a in hits if a>.01]
   if b['coverage']['classification']=='missing':self.assertEqual(hits,[])
   else:self.assertEqual(len(hits),len(b['coverage']['osmMatches']))
  self.assertEqual(set(self.result['missingBuildingUids']),{b['uid'] for b in self.output if b['coverage']['classification']=='missing'})
 def test_terrain_conflict_flags_and_dense_crosscheck(self):
  # Independent dense sampling at vertices/interior points verifies analytical extrema bound the surface.
  sample=self.output[::41];bounds=Polygon([(x,z) for b in sample for x,z in b['rings'][0]]).bounds;terrain=m.Terrain(bounds)
  for b in sample:
   p=Polygon(b['rings'][0],b['rings'][1:]);t=b['terrain'];values=[terrain.ground(x,z) for x,z in p.exterior.coords];values.append(terrain.ground(p.centroid.x,p.centroid.y))
   for value in values:self.assertGreaterEqual(value,t['min']-.002);self.assertLessEqual(value,t['max']+.002)
   self.assertEqual(t['roofWhollyBelowTerrain'],b['renderTopHeight']<t['min']-.1);self.assertEqual(t['roofPartlyBelowTerrain'],b['renderTopHeight']<t['max']-.1)
 def test_estimate_policy_partial_invalid_and_negative_datum(self):
  def check(base,top,levels=None,kind='Tower'):
   return m.render_elevations(dict(BaseHeight=base,TopHeight=top,Storeys=levels,BuildingBlockType=kind),dict(min=7,max=8,centre=7.5))
  self.assertEqual(check(-2,8)['base'],-2);self.assertEqual(check(4,None,2)['height'],6.4)
  self.assertEqual(check(None,20)['renderTopHeight'],20);self.assertEqual(check(None,None,kind='Open-sided Structure')['height'],3)
  self.assertEqual(check(10,5)['base'],10);self.assertEqual(check(10,5)['heightSource'],'estimated')
 def test_streamable_api_matches_saved_source_records(self):
  for b in self.output[::71]:
   result=list(m.stage_feature(self.raw[b['objectId']],lambda p:b['terrain']))[0]
   for key in ['uid','rings','sourceAttributes','base','height','heightSource','terrain']:self.assertEqual(result[key],b[key])
 def test_projected_4795_rounding_preserves_valid_source_topology(self):
  fixture=m.read(HERE.parent/'landsd-territory/fixtures/packing-4795-native.json')
  original,_=m.official_geometry(fixture);self.assertTrue(original.is_valid)
  record=list(m.stage_feature(fixture,lambda p:dict(min=0,max=0,centre=0,method='test terrain')))[0]
  packed=Polygon(record['rings'][0],record['rings'][1:]);self.assertTrue(packed.is_valid);self.assertLess(packed.hausdorff_distance(original),.000001)
  self.assertEqual(record['sourceAttributes'],fixture['attributes'])
 def test_ring_winding_and_nested_holes(self):
  rings=[[[834500,816500],[834510,816500],[834510,816510],[834500,816510],[834500,816500]],[[834502,816502],[834508,816502],[834508,816508],[834502,816508],[834502,816502]],[[834503,816503],[834504,816503],[834504,816504],[834503,816504],[834503,816503]]]
  p,_=m.official_geometry(dict(geometry=dict(rings=[list(reversed(r)) for r in rings])));self.assertAlmostEqual(p.area,65);self.assertEqual(len(m.polys(p)),2)
if __name__=='__main__':unittest.main()
