"""Coverage/identity/provenance guards for the bounded staged additions."""
import collections,gzip,json,unittest
from shapely.geometry import Polygon
from shapely.ops import unary_union
from audit import HERE,OLD,DOC,sha
class AuditTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.audit=json.loads((DOC/'audit.json').read_text());cls.rows=cls.audit['rows'];cls.buildings=json.loads(gzip.decompress((OLD/'building-selection.json.gz').read_bytes()))['buildings'];cls.catalogue=json.loads((HERE/'compact/catalogue.json').read_text());cls.old=json.loads(gzip.decompress((OLD/'model-geometries.json.gz').read_bytes()))['byBuildingUid']
 def test_every_selected_uid_has_one_terminal_reason(self):
  self.assertEqual({b['uid'] for b in self.buildings},{r['uid'] for r in self.rows});self.assertEqual(len(self.rows),len({r['uid'] for r in self.rows}));self.assertEqual(len(self.rows),1030)
  self.assertEqual(collections.Counter(r['reason'] for r in self.rows),{'already-imported':532,'safe-staged-addition':7,'exact-georef-candidate-fails-conservative-footprint-match':3,'no-exact-georef-model-in-inspected-building-directories':488})
 def test_complete_index_sheets_cover_whole_selected_footprints(self):
  index=json.loads((HERE/'index.json').read_text());self.assertFalse(index.get('exceededTransferLimit'));self.assertEqual(len(index['features']),11)
  cover=unary_union([Polygon(f['geometry']['rings'][0],f['geometry']['rings'][1:]) for f in index['features']])
  for b in self.buildings:
   rings=[[(x+834500,816500-z) for x,z in r] for r in b['rings']];self.assertLess(Polygon(rings[0],rings[1:]).difference(cover).area,.001,b['uid'])
 def test_directory_absence_is_exhaustive_for_inspected_model_entries(self):
  refs={}
  for p in (HERE/'directories').glob('*.json'):
   for e in json.loads(p.read_text())['entries']:
    if e['name'].startswith('BUILDING/') and e['name'].endswith('.gltf'):refs.setdefault(e['name'].split('/')[-1][1:11],[]).append(e['name'])
  for r in self.rows:
   if r['reason']=='no-exact-georef-model-in-inspected-building-directories':self.assertNotIn(r['geoRefNo'],refs)
 def test_staged_assets_are_new_and_exactly_identified(self):
  rows={b['uid']:b for b in self.buildings};self.assertEqual(len(self.catalogue['models']),7)
  for e in self.catalogue['models']:
   self.assertNotIn(e['uid'],self.old);b=rows[e['uid']]
   for k,v in [('buildingCSUID','buildingCSUID'),('objectId','objectId'),('recordedBaseHeight','baseHeightHKPD'),('recordedTopHeight','topHeightHKPD')]:self.assertEqual(e[k],b[v])
   raw=(HERE/'compact'/e['asset']).read_bytes();self.assertEqual(sha(raw),e['sha256']);self.assertEqual(len(raw),e['bytes']);self.assertFalse(e['placementReviewed'])
 def test_source_downloads_are_original_verified_entries(self):
  import zipfile
  for p in (HERE/'sources').glob('*/download.json'):
   d=json.loads(p.read_text());archive=p.parent/(p.parent.name+'.zip');self.assertEqual(sha(archive.read_bytes()),d['sha256']);self.assertIsNone(d['archiveSha256'])
   with zipfile.ZipFile(archive) as z:
    for e in d['entries']:self.assertEqual(sha(z.read(e['name'])),e['sha256']);self.assertEqual(z.getinfo(e['name']).CRC,e['sourceCRC32'])
 def test_terrain_conflicts_remain_explicit(self):
  proof=json.loads((DOC/'runtime-verification.json').read_text());self.assertTrue(proof['staged']);self.assertEqual({r['uid'] for r in proof['results'] if r['roofBelowCentreTerrain']},{'landsd/14899:0','landsd/211618:0'})
if __name__=='__main__':unittest.main()
