import io,struct,unittest,zipfile
from discover import models,ac,cache_key
class DiscoveryTests(unittest.TestCase):
 def test_complete_directory_lists_models_without_extracting_payloads(self):
  stream=io.BytesIO();model='B345321814801063C0';prefix='BUILDING/'+model+'/'
  with zipfile.ZipFile(stream,'w',zipfile.ZIP_DEFLATED) as z:
   z.writestr(prefix+model+'.gltf','{}');z.writestr(prefix+'geometry.bin',b'1234567');z.writestr('TERRAIN/other.gltf','{}');z.writestr('../BUILDING/invalid.gltf','{}')
  raw=stream.getvalue();end=raw.rfind(b'PK\x05\x06');offset=struct.unpack('<4s4H2LH',raw[end:end+22])[6];infos,_=ac.parse_directory(raw[offset:]);found=models(infos)
  self.assertEqual(len(found),1);self.assertEqual(found[0]['geoRefNo'],'3453218148');self.assertEqual(found[0]['decodedBytes'],9);self.assertEqual(len(found[0]['members']),2)
  with self.assertRaises(AssertionError):ac.parse_directory(raw[offset:-1])
 def test_changed_source_or_pipeline_does_not_reuse_negative_lookup(self):
  r={'sheet':'11-NW-24C','etag':'one','directorySHA256':'old'};key=cache_key('index','code',r)
  self.assertEqual(key,cache_key('new-index-same-source','code',r));self.assertNotEqual(key,cache_key('index','new-code',r));self.assertNotEqual(key,cache_key('index','code',{**r,'etag':'two'}));self.assertNotEqual(key,cache_key('index','code',{**r,'directorySHA256':'new'}))
if __name__=='__main__':unittest.main()
