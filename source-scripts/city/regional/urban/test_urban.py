"""Audit the generated artefact against retained source geometry and city meshes."""
import json,math,re,unittest
from functools import lru_cache
from shapely.geometry import Point,Polygon
from build import ROOT,HERE,OUT,DOC,DISTRICTS,load_sources,shape,Arrivals
from build_city import geometry,polys

class UrbanArtefactTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.output=json.loads(OUT.read_text());cls.records,cls.sources=load_sources();cls.arrivals=Arrivals(cls.records)
  cls.districts={DISTRICTS[e.get('tags',{}).get('name:en')]:geometry(e) for e in cls.records.values() if e.get('tags',{}).get('name:en') in DISTRICTS and e.get('tags',{}).get('boundary')=='administrative'}
 @lru_cache(maxsize=None)
 def source_polygons(self,oid):return polys(geometry(self.records[oid]))
 def test_all_56_checklist_sections_have_partial_visits(self):
  expected={f'{district:02}.{i}' for district,n in enumerate([7,5,6,8,6,6,6,6,6],start=1) for i in range(1,n+1)}
  self.assertEqual({p['sectionId'] for p in self.output['places']},expected)
  self.assertEqual({s['id'] for s in self.output['sections']},expected)
  self.assertEqual(len(self.output['places']),56)
  self.assertTrue(all(s['status']=='partial' for s in self.output['sections']))
  self.assertEqual(len(self.districts),9)
 def test_every_arrival_is_on_a_mapped_path_and_clear_dry_terrain(self):
  for place in self.output['places']:
   with self.subTest(section=place['sectionId']):
    self.assertIs(place.get('arrivalVerified'),True)
    point=Point(place['spawn']);oid=place['arrivalSource'].removeprefix('https://www.openstreetmap.org/')
    self.assertLessEqual(shape(self.records[oid]).distance(point),.08)
    self.assertTrue(self.arrivals.valid(point))
    self.assertAlmostEqual(self.arrivals.ground(point.x,point.y),place['terrainY'],delta=.001)
    self.assertLessEqual(point.distance(Point(place['target'][0],place['target'][2])),1000)
 def test_arrivals_remain_in_the_assigned_district(self):
  for place in self.output['places']:
   with self.subTest(section=place['sectionId']):
    self.assertTrue(self.districts[place['sectionId'][:2]].buffer(1).covers(Point(place['spawn'])))
 def test_surface_rings_and_sources_preserve_polygon_geography(self):
  seen=set()
  for surface in self.output['surfaces']:
   with self.subTest(surface=surface['id']):
    self.assertNotIn(surface['id'],seen);seen.add(surface['id'])
    for ring in surface['rings']:
     self.assertGreaterEqual(len(ring),4);self.assertEqual(ring[0],ring[-1]);self.assertTrue(all(math.isfinite(c) for p in ring for c in p))
    polygon=Polygon(surface['rings'][0],surface['rings'][1:]);self.assertTrue(polygon.is_valid);self.assertGreater(polygon.area,0)
    oid=surface['source'].removeprefix('https://www.openstreetmap.org/')
    self.assertLessEqual(min(polygon.hausdorff_distance(p) for p in self.source_polygons(oid)),.34)
    self.assertTrue(self.districts[surface['sectionId'][:2]].buffer(1).covers(polygon.representative_point()))
 def test_render_budget_and_counts_match_report(self):
  report=json.loads((DOC/'verification.json').read_text());surfaces=self.output['surfaces']
  self.assertEqual(report['surfaceCount'],len(surfaces));self.assertEqual(report['verifiedArrivals'],56)
  self.assertLess(report['byteCount'],1000000);self.assertLess(report['surfaceVertices'],20000)
  self.assertEqual({s['kind'] for s in surfaces},{'plaza','pitch','pier','beach'})
  self.assertEqual(self.output['buildingOverrides'],[])
if __name__=='__main__':unittest.main()
