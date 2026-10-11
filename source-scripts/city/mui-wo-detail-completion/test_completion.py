"""Check exhaustive source accounting and original-geometry packet integrity."""
import gzip, hashlib, json, pathlib, struct, unittest
from run import HERE, ROOT, DOC, baseline, load

class CompletionTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.buildings,cls.original=baseline();cls.ledger=load(DOC/'ledger.json');cls.catalogue=load(HERE/'compact/catalogue.json');cls.evidence=load(DOC/'compact-assets.json')
 def test_every_uid_once_and_originals_preserved(self):
  rows=self.ledger['rows'];uids=[r['uid'] for r in rows]
  self.assertEqual(len(uids),2408);self.assertEqual(len(uids),len(set(uids)));self.assertEqual(set(uids),{b['uid'] for b in self.buildings})
  self.assertEqual({r['uid'] for r in rows if r['reason']=='already-detailed'},set(self.original))
  new={r['uid'] for r in self.catalogue['models']};self.assertFalse(new & set(self.original));self.assertEqual(new,{r['uid'] for r in rows if r['reason']=='new-exact-match-packed-awaiting-placement-review'})
 def test_source_identity_and_match_screen(self):
  by_uid={b['uid']:b for b in self.buildings};evidence={r['uid']:r for r in self.evidence['assets']}
  for model in self.catalogue['models']:
   b=by_uid[model['uid']];e=evidence[model['uid']]
   self.assertEqual(model['buildingCSUID'],b['buildingCSUID']);self.assertEqual(model['modelId'][1:11],b['sourceAttributes']['GeoRefNo'])
   self.assertEqual({m['buildingCSUID'] for m in e['sourceMatches']},{b['buildingCSUID']})
   self.assertTrue(all(m['overlapOfSmallerFootprint']>=.5 and m['footprintCentroidDistanceMetres']<=10 for m in e['sourceMatches']))
   for rel,digest in e['sourceHashes'].items():
    folder=ROOT/e['sourceEntry'];folder=folder.parents[2]
    self.assertEqual(hashlib.sha256((folder/rel).read_bytes()).hexdigest(),digest)
 def test_native_nodes_materials_and_glb_lengths(self):
  evidence={r['uid']:r for r in self.evidence['assets']}
  for model in self.catalogue['models']:
   compressed=(HERE/'compact'/model['asset']).read_bytes();raw=gzip.decompress(compressed)
   self.assertEqual(len(compressed),model['bytes']);self.assertEqual(hashlib.sha256(compressed).hexdigest(),model['sha256'])
   magic,version,length=struct.unpack('<4sII',raw[:12]);self.assertEqual((magic,version,length),(b'glTF',2,len(raw)))
   json_size,json_kind=struct.unpack('<I4s',raw[12:20]);self.assertEqual(json_kind,b'JSON');packed=json.loads(raw[20:20+json_size]);source=load(ROOT/evidence[model['uid']]['sourceEntry'])
   for key in ('nodes','scenes','scene','materials'):self.assertEqual(packed.get(key),source.get(key))
   self.assertEqual(sum(s['triangles'] for s in evidence[model['uid']]['primitives']),model['triangles'])
 def test_summary_reconciles_and_no_claim_of_publication(self):
  counts=self.ledger['counts'];self.assertEqual(sum(counts['reasons'].values()),counts['forms']);self.assertEqual(counts['baselineDetailed']+counts['newExactModels'],counts['potentialDetailed']);self.assertEqual(counts['potentialDetailed']+counts['remainingFallback'],counts['forms'])
  self.assertTrue(all(not m['placementReviewed'] for m in self.catalogue['models']));self.assertEqual(counts['compressedBytes'],sum(m['bytes'] for m in self.catalogue['models']))
 def test_all_intersecting_sheets_inspected(self):
  scope=load(HERE/'scope.json');sheets=set(scope['sheets']);self.assertEqual(sheets,set(scope['additionalSheets'])|set(scope['existingSheets']))
  for sheet in scope['additionalSheets']:
   d=load(HERE/'sources'/sheet/'download.json');self.assertEqual(hashlib.sha256((HERE/'sources'/sheet/(sheet+'.zip')).read_bytes()).hexdigest(),d['sha256']);self.assertTrue((HERE/'staged'/sheet/'manifest.json').exists())
if __name__=='__main__':unittest.main()
