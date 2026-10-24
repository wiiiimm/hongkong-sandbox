"""Source topology/permission/coordinate tests; runtime replay is a separate check."""
import gzip,json,math,pathlib,unittest
from route_build import build,permitted,SOURCE,WAY_IDS,ROOT
class RouteTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.route=build();cls.source={e['id']:e for e in json.loads(gzip.decompress(SOURCE.read_bytes()))['elements'] if e['type']=='way'}
 def test_every_connection_is_an_original_shared_node_edge(self):
  r=self.route
  self.assertEqual(len(r['nodeIds']),len(r['centreline']))
  self.assertGreater(r['lengthMetres'],600)
  self.assertEqual(len(r['stops']),6)
  self.assertEqual(r['centreline'][0],[-30779.0,3820.8])
  for segment in r['segments']:
   way=self.source[segment['sourceWayId']];pairs=set(zip(way['nodes'],way['nodes'][1:]))
   for i in range(segment['fromIndex'],segment['toIndex']):
    pair=tuple(r['nodeIds'][i:i+2])
    if i<2:
     self.assertEqual(segment['sourceWayId'],r['arrivalInterpolation']['sourceWayId']);self.assertLess(r['arrivalInterpolation']['roundingConnectorMetres'],.1)
    else:self.assertTrue(pair in pairs or pair[::-1] in pairs)
 def test_no_private_residential_deck_or_tidal_stair_is_included(self):
  for s in self.route['segments']:self.assertTrue(permitted(s['tags']));self.assertNotEqual(s['kind'],'steps');self.assertNotEqual(s['tags'].get('tidal'),'yes')
  for access in ('private','no','customers','permit','destination'):
   self.assertFalse(permitted({'highway':'footway','access':access}))
   self.assertFalse(permitted({'highway':'footway','foot':access}))
  self.assertNotIn(244106712,WAY_IDS) # Sun Ki conflicting access tags are not assumed public.
 def test_main_bridge_matches_existing_bridge_geometry(self):
  bridge=next(s for s in self.route['segments'] if s['kind']=='bridge')
  record=next(b for b in json.loads((ROOT/'3d-viewer/city/data/bridges.json').read_text())['bridges'] if b['id']==bridge['bridgeId'])
  points=self.route['centreline'][bridge['fromIndex']:bridge['toIndex']+1]
  self.assertEqual(self.route['nodeIds'][bridge['fromIndex']:bridge['toIndex']+1],record['nodes'][::-1])
  self.assertLess(max(math.dist(a,b) for a,b in zip(points,record['path'][::-1])),.008)
 def test_stops_follow_route_and_runtime_acceptance_is_not_claimed(self):
  self.assertEqual([s['index'] for s in self.route['stops']],sorted(s['index'] for s in self.route['stops']))
  self.assertFalse(self.route['continuousWalkVerified']);self.assertEqual(self.route['sourceOffsets'],[])
  self.assertEqual(build(),self.route)
if __name__=='__main__':unittest.main()
