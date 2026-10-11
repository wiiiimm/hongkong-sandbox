"""Checks the exported data against independent retained geometry and terrain."""
import json,math,pathlib,unittest
from shapely.geometry import Point,Polygon,LineString
import build

class NTDataTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.data=json.loads((build.OUT/'regional/nt.json').read_text());cls.records,_,_=build.read_sources();cls.arrivals=build.Arrivals(cls.records)
 def test_all_assigned_sections_and_regions(self):
  expected={f'{district}.{section}' for district,count in [(11,5),(12,6),(13,7),(14,7),(15,9),(16,7),(17,8),(18,8)] for section in range(1,count+1)}
  self.assertEqual({s['id'] for s in self.data['sections']},expected);self.assertEqual({p['sectionId'] for p in self.data['places']},expected)
  self.assertEqual({p['region'] for p in self.data['places']},{'ntwest','nteast','ntnorth'})
  self.assertEqual(len({p['id'] for p in self.data['places']}),len(self.data['places']))
 def test_source_coordinates_and_verified_arrivals(self):
  for p in self.data['places']:
   feature=p['source'].removeprefix('https://www.openstreetmap.org/');centre=build.centre_of(self.records[feature]);actual=Point(build.xy(p['lon'],p['lat']))
   self.assertLess(centre.distance(actual),.03,p['id'])
   if p.get('aerialOnly'):
    self.assertNotIn('spawn',p);self.assertNotIn('arrivalVerified',p);continue
   self.assertTrue(p['arrivalVerified']);point=Point(p['spawn']);self.assertTrue(self.arrivals.valid(point),p['id'])
   pathid=p['arrivalSource'].removeprefix('https://www.openstreetmap.org/');path=self.records[pathid];tags=path['tags']
   self.assertNotIn(tags.get('access'),build.RESTRICTED);self.assertNotIn(tags.get('foot'),build.RESTRICTED)
   self.assertLessEqual(LineString(build.coords(path['geometry'])).distance(point),.08,p['id']);self.assertLessEqual(point.distance(centre),1000)
   self.assertAlmostEqual(p['terrainY'],self.arrivals.ground(point.x,point.y),delta=.006)
 def test_restricted_sites_are_not_walkable_arrivals(self):
  byid={p['id']:p for p in self.data['places']}
  for id in ['nt-kwai-tsing-port','nt-lung-kwu-chau','nt-sha-tau-kok','nt-lin-ma-hang-border']:self.assertTrue(byid[id]['aerialOnly'])
 def test_surface_footprints_remain_source_polygons(self):
  ids=set();boundary=build.geometry(self.records['relation/913110'])
  for s in self.data['surfaces']:
   self.assertNotIn(s['id'],ids);ids.add(s['id']);p=Polygon(s['rings'][0],s['rings'][1:]);self.assertTrue(p.is_valid,s['id']);self.assertGreater(p.area,11);self.assertTrue(boundary.buffer(.1).covers(p),s['id'])
   source=build.geometry(self.records[s['source'].removeprefix('https://www.openstreetmap.org/')]);self.assertTrue(source.buffer(.7).covers(p),s['id'])
   self.assertLessEqual(sum(len(r) for r in s['rings']),600)
   for ring in s['rings']:self.assertEqual(ring[0],ring[-1]);self.assertTrue(all(math.isfinite(v) for point in ring for v in point))
 def test_surface_counts_and_height_honesty(self):
  kinds={s['kind'] for s in self.data['surfaces']};self.assertEqual(kinds,{'pier','beach','plaza','pitch'})
  self.assertGreater(len(self.data['surfaces']),100);self.assertEqual(self.data['buildingOverrides'],[])

if __name__=='__main__':unittest.main()
