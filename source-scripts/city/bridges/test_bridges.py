"""Verify real geometry and graph evidence, not just serializer structure."""
import json,math,unittest
from shapely.geometry import LineString,Point,Polygon
import build

class BridgeTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.data=json.loads(build.OUT.read_text());cls.records,*_=build.read_sources();cls.boundary=build.geometry(cls.records['relation/913110']);cls.boundary_line_buffer=cls.boundary.buffer(.02);cls.boundary_deck_buffer=cls.boundary.buffer(.1);cls.byid={r['id']:r for r in cls.data['bridges']}
 def test_explicit_numeric_evidence(self):
  self.assertEqual(build.metres('5.5 m'),5.5);self.assertEqual(build.metres(' 14 '),14);self.assertEqual(build.metres('3 metres'),3)
  for value in ['3-5','3;4','15 ft','unknown','~4','4,5']:self.assertIsNone(build.metres(value))
  self.assertEqual(build.levels('0;1'),[0,1]);self.assertEqual(build.levels('0,1'),[0,1]);self.assertEqual(build.levels('-1;0'),[-1,0]);self.assertEqual(build.levels('1-3'),[])
  self.assertIsNone(build.scalar('1;2'));self.assertEqual(build.scalar('2'),2)
 def test_role_selection_keeps_floor_paths_distinct(self):
  self.assertEqual(build.classify({'highway':'footway','bridge':'yes'}),'bridge')
  self.assertEqual(build.classify({'highway':'footway','level':'2','indoor':'yes'}),'elevated-link')
  self.assertIsNone(build.classify({'highway':'footway','level':'0','indoor':'yes'}))
  self.assertIsNone(build.classify({'highway':'path','height':'0.5','informal':'yes'}))
  self.assertIsNone(build.classify({'highway':'construction','bridge':'yes'}))
 def test_geometry_and_source_node_alignment(self):
  self.assertEqual(len(self.byid),len(self.data['bridges']))
  for r in self.data['bridges']:
   self.assertEqual(len(r['nodes']),len(r['path']),r['id']);self.assertGreaterEqual(len(r['path']),2)
   e=self.records[r['source'].removeprefix('https://www.openstreetmap.org/')];original=build.coords(e['geometry']);line=LineString(original);actual=LineString(r['path'])
   self.assertTrue(line.buffer(.02).covers(actual),r['id']);self.assertTrue(self.boundary_line_buffer.covers(actual),r['id'])
   source_nodes={node:point for node,point in zip(e.get('nodes',[]),original)}
   for node,point in zip(r['nodes'],r['path']):
    self.assertTrue(all(math.isfinite(v) for v in point));self.assertEqual(len(point),2)
    if node is not None:self.assertIn(node,source_nodes);self.assertLess(Point(point).distance(Point(source_nodes[node])),.02)
    else:self.assertLess(Point(point).distance(self.boundary.boundary),.02,r['id'])
 def test_access_connections_are_actual_shared_endpoint_nodes(self):
  for r in self.data['bridges']:
   if r['role']!='access':continue
   self.assertTrue(r['connections']);self.assertTrue(r['connectsTo'])
   for c in r['connections']:
    self.assertIn(c['pathIndex'],[0,len(r['path'])-1]);self.assertEqual(c['nodeId'],r['nodes'][c['pathIndex']]);self.assertEqual(c['position'],r['path'][c['pathIndex']])
    for id in c['bridgeIds']:
     other=self.byid[id];self.assertNotEqual(other['role'],'access');self.assertIn(c['nodeId'],other['nodes'])
     self.assertEqual(c['position'],other['path'][other['nodes'].index(c['nodeId'])])
 def test_deck_outlines_are_source_geometry(self):
  for deck in self.data['decks']:
   polygon=Polygon(deck['rings'][0],deck['rings'][1:]);source=build.geometry(self.records[deck['source'].removeprefix('https://www.openstreetmap.org/')])
   self.assertTrue(polygon.is_valid,deck['id']);self.assertTrue(source.buffer(.1).covers(polygon),deck['id']);self.assertTrue(self.boundary_deck_buffer.covers(polygon),deck['id'])
   for id in deck['bridgeIds']:self.assertIn(id,self.byid);self.assertNotEqual(self.byid[id]['role'],'access');self.assertEqual(self.byid[id]['layer'],build.scalar(deck['tags']['layer']))
 def test_shared_source_nodes_have_one_retained_coordinate(self):
  positions={}
  for r in self.data['bridges']:
   for node,point in zip(r['nodes'],r['path']):
    if node is None:continue
    if node in positions:self.assertEqual(positions[node],point,str(node))
    else:positions[node]=point
 def test_all_eighteen_districts_have_coverage(self):
  names={name for name in self.data['counts']['districts'] if name.endswith('District')};self.assertEqual(len(names),18)
  self.assertGreater(self.data['counts']['roles']['bridge'],10000);self.assertGreater(self.data['counts']['roles']['access'],1000)
  self.assertGreater(self.data['counts']['interior'],0)

if __name__=='__main__':unittest.main()
