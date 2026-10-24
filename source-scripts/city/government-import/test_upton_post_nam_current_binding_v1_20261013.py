"""Pure named manifest/census/evidence-routing adversity, no database or mesh."""
import unittest,tempfile,copy,hashlib
from pathlib import Path
from upton_post_nam_current_binding_v1_20261013 import manifest_delta,census,historical_ref,OLD
ROOT=Path(__file__).resolve().parents[3]
OLD_BYTES=(ROOT/'docs/astra-city/government-import/government-xl-complete-current-native-actual-position-matrix-bounds-v4-20261012/captured-manifest.json').read_bytes()
assert hashlib.sha256(OLD_BYTES).hexdigest()==OLD
class Tests(unittest.TestCase):
 def setUp(self):
  self.old=dict(officialModelCatalogues=['a','b'],tiles=[dict(url='tile')],terrainPatches=[dict(url='terrain')],baseTerrain='base')
  self.current=copy.deepcopy(self.old);self.current['officialModelCatalogues'].append('Nam')
 def test_named_sole_append(self):self.assertTrue(manifest_delta(self.old,self.current,'Nam'))
 def test_changed_tile_rejected(self):
  self.current['tiles'][0]['url']='other'
  with self.assertRaises(AssertionError):manifest_delta(self.old,self.current,'Nam')
 def test_changed_terrain_rejected(self):
  self.current['terrainPatches'][0]['url']='other'
  with self.assertRaises(AssertionError):manifest_delta(self.old,self.current,'Nam')
 def test_changed_other_field_rejected(self):
  self.current['newFlag']=True
  with self.assertRaises(AssertionError):manifest_delta(self.old,self.current,'Nam')
 def test_changed_old_catalogue_rejected(self):
  self.current['officialModelCatalogues'][0]='other'
  with self.assertRaises(AssertionError):manifest_delta(self.old,self.current,'Nam')
 def test_catalogue_order_change_rejected(self):
  self.current['officialModelCatalogues']=['b','a','Nam']
  with self.assertRaises(AssertionError):manifest_delta(self.old,self.current,'Nam')
 def test_unrelated_second_append_rejected(self):
  self.current['officialModelCatalogues'].append('other')
  with self.assertRaises(AssertionError):manifest_delta(self.old,self.current,'Nam')
 def test_exact_uid_delta(self):
  old=[f'landsd/{i}:0'for i in range(6649)];self.assertTrue(census(old,old+['landsd/79099:0']))
 def test_wrong_uid_delta_rejected(self):
  old=[f'landsd/{i}:0'for i in range(6649)]
  with self.assertRaises(AssertionError):census(old,old+['landsd/79098:0'])
 def test_missing_old_actor_rejected(self):
  old=[f'landsd/{i}:0'for i in range(6649)]
  with self.assertRaises(AssertionError):census(old,old[1:]+['landsd/79099:0','landsd/90000:0'])
 def test_duplicate_current_actor_rejected(self):
  old=[f'landsd/{i}:0'for i in range(6649)]
  with self.assertRaises(AssertionError):census(old,old+[old[0]])
 def test_duplicate_old_actor_rejected(self):
  old=[f'landsd/{i}:0'for i in range(6649)];old[-1]=old[0]
  with self.assertRaises(AssertionError):census(old,old+['landsd/79099:0'])
 def paths(self,root):
  archive=root/'saved.json';archive.write_bytes(OLD_BYTES);return archive
 def test_only_named_old_manifest_resolves(self):
  with tempfile.TemporaryDirectory()as t:
   root=Path(t);a=self.paths(root);self.assertEqual(historical_ref(dict(path='3d-viewer/city/data/manifest.json',sha256=OLD),root,a),a)
 def test_missing_other_path_never_resolves(self):
  with tempfile.TemporaryDirectory()as t:
   root=Path(t);a=self.paths(root)
   with self.assertRaises(FileNotFoundError):historical_ref(dict(path='other.json',sha256=OLD),root,a)
 def test_changed_other_input_never_resolves(self):
  with tempfile.TemporaryDirectory()as t:
   root=Path(t);a=self.paths(root);(root/'other.json').write_bytes(b'changed')
   with self.assertRaises(AssertionError):historical_ref(dict(path='other.json',sha256=OLD),root,a)
 def test_changed_named_archive_rejected(self):
  with tempfile.TemporaryDirectory()as t:
   root=Path(t);a=self.paths(root);a.write_bytes(b'changed')
   with self.assertRaises(AssertionError):historical_ref(dict(path='3d-viewer/city/data/manifest.json',sha256=OLD),root,a)
 def test_unnamed_old_manifest_hash_not_aliased(self):
  with tempfile.TemporaryDirectory()as t:
   root=Path(t);a=self.paths(root)
   with self.assertRaises(FileNotFoundError):historical_ref(dict(path='3d-viewer/city/data/manifest.json',sha256='0'*64),root,a)
 def test_current_version_checks_actual_path(self):
  with tempfile.TemporaryDirectory()as t:
   root=Path(t);a=self.paths(root);f=root/'3d-viewer/city/data/manifest.json';f.parent.mkdir(parents=True);f.write_bytes(b'current');q=dict(path='3d-viewer/city/data/manifest.json',sha256=hashlib.sha256(b'current').hexdigest());self.assertEqual(historical_ref(q,root,a),f)
if __name__=='__main__':unittest.main()
