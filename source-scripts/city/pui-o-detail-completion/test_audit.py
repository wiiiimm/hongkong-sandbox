"""Data-completeness and safety checks for the bounded staged Pui O package."""
import gzip,hashlib,json,pathlib,unittest,zipfile,io
from audit import directory_entries
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2];BASE=HERE.parent/'pui-o-completion';DOC=ROOT/'docs/astra-city/pui-o-detail-completion'
def read(p):return json.loads(p.read_text())
class AuditTests(unittest.TestCase):
 def test_every_fallback_accounted_once(self):
  selection=json.loads(gzip.decompress((BASE/'building-selection.json.gz').read_bytes()))['buildings'];known={m['uid'] for m in read(BASE/'compact/catalogue.json')['models']};rows=read(DOC/'completion.json')['ledger'];self.assertEqual(len(rows),238);self.assertEqual(len({r['uid'] for r in rows}),238);self.assertEqual({r['uid'] for r in rows},{b['uid'] for b in selection}-known)
 def test_index_completeness(self):
  for name in ['index','individual-index']:
   data=read(HERE/(name+'.json'));provenance=read(HERE/(name+'-provenance.json'));self.assertFalse(data.get('exceededTransferLimit'));self.assertEqual({f['attributes']['OBJECTID'] for f in data['features']},set(provenance['ids']['objectIds']));self.assertEqual(hashlib.sha256((HERE/(name+'.json')).read_bytes()).hexdigest(),provenance['sha256'])
 def test_complete_original_zip_directories(self):
  for dirname in ['directories','individual-directories']:
   files=list((HERE/dirname).glob('*.json'));self.assertEqual(len(files),15)
   for path in files:
    record=read(path);raw=path.with_suffix('.bin').read_bytes();self.assertEqual(hashlib.sha256(raw).hexdigest(),record['directorySha256'])
    infos=directory_entries(raw);self.assertEqual(len(infos),record['entries']);self.assertEqual({i['filename'] for i in infos if i['filename'].endswith('.gltf')},{e['path'] for e in record['models']})
 def test_only_exact_unambiguous_candidates(self):
  report=read(DOC/'prepared.json');self.assertEqual(len(report['screens']),4)
  for r in report['screens']:
   self.assertTrue(r['safeIdentityMatch']);self.assertEqual(len(r['checks']),1);self.assertGreaterEqual(r['checks'][0]['overlap'],.5);self.assertLessEqual(r['checks'][0]['centroidDistanceMetres'],10)
 def test_source_and_packed_bytes_unchanged(self):
  cat=read(HERE/'compact/catalogue.json');self.assertEqual(cat['counts']['packedModels'],4)
  for r in cat['models']:
   asset=HERE/'compact'/r['asset'];self.assertEqual(asset.stat().st_size,r['bytes']);self.assertEqual(hashlib.sha256(asset.read_bytes()).hexdigest(),r['sha256'])
  for r in read(DOC/'prepared.json')['assets']:
   entry=ROOT/r['sourceEntry'];root=entry.parents[2]
   for rel,digest in r['sourceHashes'].items():self.assertEqual(hashlib.sha256((root/rel).read_bytes()).hexdigest(),digest)
 def test_terrain_conflicts_excluded_from_integration_candidate(self):
  rt=read(DOC/'runtime-verification.json');safe={r['uid'] for r in rt['results'] if not r['roofBelowSomeCurrentTerrain']};cat=read(HERE/'compact/catalogue-integration-candidate.json');self.assertEqual({m['uid'] for m in cat['models']},safe);self.assertEqual(len(safe),2);self.assertTrue(all(m['placementReviewed'] is False for m in cat['models']))
if __name__=='__main__':unittest.main()
