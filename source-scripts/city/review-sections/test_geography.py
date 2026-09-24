"""Independent checks on the published polygons and retained geography sources."""
import hashlib,json,math,pathlib,sys,unittest
import shapely
from shapely.geometry import Polygon,Point,MultiPolygon
from shapely.ops import unary_union
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent));import build
class ReviewGeographyTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.data=json.loads(build.OUT.read_text());cls.sections=cls.data['sections'];cls.shapes={s['id']:unary_union([Polygon(p['rings'][0],p['rings'][1:]) for p in s['polygons']]) for s in cls.sections};cls.districts=build.load_districts();cls.places=build.anchors()
 def test_all_132_checklist_ids_once(self):
  names,_=build.checklist();self.assertEqual(set(self.shapes),set(names));self.assertEqual(len(self.sections),132)
  for s in self.sections:self.assertEqual(s['name'],names[s['id']]);self.assertNotIn('status',s)
 def test_all_source_response_ids_and_hashes(self):
  manifest=json.loads((build.HERE/'source-manifest.json').read_text())
  for f in manifest['files']:self.assertEqual(hashlib.sha256((build.HERE/f['path']).read_bytes()).hexdigest(),f['sha256'])
  ids=json.loads((build.HERE/'sources/ids.json').read_text())['objectIds'];features=json.loads((build.HERE/'sources/districts.json').read_text())['features']
  self.assertEqual(set(ids),{f['attributes']['OBJECTID'] for f in features});self.assertEqual(len(ids),18)
 def test_valid_finite_closed_geometry_labels_and_bounds(self):
  for s in self.sections:
   g=self.shapes[s['id']];self.assertTrue(g.is_valid,(s['id'],shapely.is_valid_reason(g)));self.assertGreater(g.area,1);self.assertTrue(g.covers(Point(s['label'])),s['id']);self.assertEqual(list(g.bounds),s['bounds'])
   for p in s['polygons']:
    for r in p['rings']:
     self.assertEqual(r[0],r[-1]);self.assertGreaterEqual(len(r),4);self.assertTrue(all(len(p)==2 and all(math.isfinite(x) for x in p) for p in r))
 def test_every_district_complete_to_one_square_millimetre(self):
  for district,source in self.districts.items():
   parts=[g for key,g in self.shapes.items() if key.startswith(district+'.')];merged=unary_union(parts)
   self.assertLess(merged.symmetric_difference(source['geometry']).area,1e-6,district)
   self.assertLess(abs(sum(p.area for p in parts)-merged.area),1e-6,district)
 def test_all_sections_pairwise_non_overlapping(self):
  items=list(self.shapes.items())
  for i,(key,g) in enumerate(items):
   for other,h in items[i+1:]:self.assertLess(g.intersection(h).area,1e-6,(key,other))
 def test_149_source_anchors_contained_four_explicit_exceptions(self):
  exceptions={e['placeId']:e for e in self.data['provenance']['anchorExceptions']};outside=[]
  for p in self.places:
   g=self.shapes[p['sectionId']];pt=Point(p['point'])
   if not g.covers(pt):
    outside.append(p['id']);self.assertIn(p['id'],exceptions);e=exceptions[p['id']]
    self.assertEqual(list(p['point']),e['sourcePoint']);self.assertTrue(g.covers(Point(e['partitionSeed'])));self.assertGreater(e['outsideRequestedDistrictMetres'],50)
    self.assertTrue(all(self.districts[d]['geometry'].covers(pt) for d in e['actualDistricts']))
  self.assertEqual(len(self.places)-len(outside),149);self.assertEqual(set(outside),set(exceptions));self.assertEqual(len(outside),4)
 def test_explicit_island_ownership_including_soko_and_po_toi(self):
  rules,_,_=build.load_islands()
  for rule in rules:
   for d in {s.split('.')[0] for s in rule['sections']}:
    wanted=unary_union([self.shapes[s] for s in rule['sections'] if s.startswith(d+'.')]);clipped=rule['geometry'].intersection(self.districts[d]['geometry'])
    self.assertLess(clipped.difference(wanted).area,1e-6,(rule['source'],d))
  for key in ('relation/14384590','relation/12922891','relation/12927100','way/9561875'):
   rule=next(r for r in rules if r['source']==key);self.assertLess(rule['geometry'].intersection(self.shapes['10.10']).area,1e-6)
 def test_holes_and_multipart_survive_partition(self):
  a=Polygon([(0,0),(100,0),(100,100),(0,100)],holes=[[(40,40),(60,40),(60,60),(40,60)]]);b=Polygon([(200,0),(210,0),(210,10),(200,10)]);shape=MultiPolygon([a,b]);cells=build.partition(shape,[{'sectionId':'01.1','point':(10,10)},{'sectionId':'01.2','point':(90,90)}])
  self.assertLess(unary_union(list(cells.values())).symmetric_difference(shape).area,1e-9);self.assertFalse(any(g.covers(Point(50,50)) for g in cells.values()));self.assertTrue(any(g.covers(Point(205,5)) for g in cells.values()))
 def test_payload_mobile_budget_and_place_inventory(self):
  self.assertLess(build.OUT.stat().st_size,2_000_000);self.assertLess(sum(len(r) for s in self.sections for p in s['polygons'] for r in p['rings']),50000)
  self.assertEqual(sorted(p['id'] for p in self.places),sorted(p for s in self.sections for p in s['placeIds']))
if __name__=='__main__':unittest.main(verbosity=2)
