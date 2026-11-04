import hashlib,tempfile,unittest
from pathlib import Path
from retained_original_terrain_route_schema_v1_20261026 import normalize_route

class RouteTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name);(self.root/'terrain.json').write_bytes(b'original exact bytes');self.route=dict(source='terrain.json',sourceSHA256=hashlib.sha256(b'original exact bytes').hexdigest(),replaces=dict(url='old',sha256='old',retainedUids=['retained']))
 def test_alias_only_and_no_input_mutation(self):
  r=normalize_route(self.root,self.route);self.assertEqual(r['sha256'],self.route['sourceSHA256']);self.assertNotIn('sha256',self.route);self.assertEqual(r['replaces'],self.route['replaces'])
 def test_conflicting_alias(self):
  with self.assertRaises(AssertionError):normalize_route(self.root,{**self.route,'sha256':'0'*64})
 def test_changed_bytes(self):
  (self.root/'terrain.json').write_bytes(b'changed')
  with self.assertRaises(AssertionError):normalize_route(self.root,self.route)
 def test_missing_actual_alias(self):
  r=dict(self.route);r.pop('sourceSHA256')
  with self.assertRaises(AssertionError):normalize_route(self.root,r)
 def test_outside_root(self):
  with self.assertRaises(AssertionError):normalize_route(self.root,{**self.route,'source':'../terrain.json'})

if __name__=='__main__':unittest.main()
