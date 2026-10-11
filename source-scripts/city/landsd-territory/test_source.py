"""Offline regressions for byte-preserving source reuse and streaming reads."""
import gzip,json,pathlib,tempfile,unittest
from retain import iter_features
from source import HERE,read_json,digest

class RetainedSourceTests(unittest.TestCase):
 def test_stream_handles_chunk_boundary_unicode_and_nulls(self):
  features=[{'type':'Feature','geometry':{'type':'Polygon','coordinates':[[[114,22],[114.01,22],[114,22.01],[114,22]]]},'properties':{'OBJECTID':i,'BuildingBlockType':'Open-sided Structure','TopHeight':None,'label':'八爪魚天橋 { \\"'+('x'*1100000 if i==2 else '')}} for i in range(1,4)]
  with tempfile.TemporaryDirectory() as folder:
   for suffix in ['.json','.json.gz']:
    p=pathlib.Path(folder)/('source'+suffix);raw=json.dumps({'type':'FeatureCollection','features':features},ensure_ascii=False).encode();p.write_bytes(gzip.compress(raw) if suffix.endswith('gz') else raw)
    self.assertEqual(list(iter_features(p)),features)
 def test_truncated_collection_is_rejected(self):
  with tempfile.TemporaryDirectory() as folder:
   p=pathlib.Path(folder)/'truncated.json';p.write_text('{"type":"FeatureCollection","features":[{"type":"Feature","properties":{}}]')
   with self.assertRaises(ValueError):list(iter_features(p))
 def test_source_manifest_matches_advertised_membership(self):
  m=read_json(HERE/'manifest.json');ids=read_json(HERE/'query-object-ids.json')['objectIds'];count=read_json(HERE/'query-count.json')['count'];v=m['validation']
  self.assertEqual(count,342223);self.assertEqual(len(ids),len(set(ids)));self.assertEqual(v['featureCount'],count);self.assertEqual(v['components'],342224)
  self.assertEqual(m['completeness']['objectIdSHA256'],digest(json.dumps(sorted(ids),separators=(',',':')).encode()))
  self.assertEqual(sum(v['buildingTypes'].values()),count);self.assertEqual(v['nullBaseHeight'],106319);self.assertEqual(v['nullTopHeight'],104917)
  self.assertEqual(v['missingGeometries'],[]);self.assertEqual(v['nonFiniteCoordinates'],[]);self.assertEqual(v['unclosedRings'],[])
 def test_compressed_source_keeps_original_bytes(self):
  m=read_json(HERE/'manifest.json');p=HERE/'landsd-hong-kong-source.geojson.gz';self.assertEqual(p.stat().st_size,m['snapshot']['compressedBytes']);self.assertEqual(digest(p.read_bytes()),m['snapshot']['compressedSHA256'])
  import hashlib
  checksum=hashlib.sha256();size=0
  with gzip.open(p,'rb') as f:
   while block:=f.read(1024*1024):checksum.update(block);size+=len(block)
  self.assertEqual(size,m['snapshot']['originalBytes']);self.assertEqual(checksum.hexdigest(),m['snapshot']['uncompressedSHA256'])

if __name__=='__main__':unittest.main()
