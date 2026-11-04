"""Protect default extraction and prevent filtered caches being mistaken for full source caches."""
import contextlib,importlib.util,io,json,pathlib,tempfile,unittest,zipfile
from unittest.mock import patch
FETCH=pathlib.Path(__file__).resolve().parents[1]/'mui-wo-models/fetch.py'
spec=importlib.util.spec_from_file_location('shared_fetch',FETCH);fetch=importlib.util.module_from_spec(spec);spec.loader.exec_module(fetch)
class Response:
 def __init__(self,data,start,size):self.data=data;self.status=206;self.headers={'Content-Range':f'bytes {start}-{start+len(data)-1}/{size}','Content-Length':str(len(data)),'ETag':'fixture-source-v1'}
 def __enter__(self):return self
 def __exit__(self,*args):pass
 def read(self):return self.data
class SourceFilterTest(unittest.TestCase):
 def setUp(self):
  b=io.BytesIO()
  with zipfile.ZipFile(b,'w') as z:
   for n in ['BUILDING/B1.gltf','BUILDING/B1.bin','TERRAIN(TB)/T1.gltf','TERRAIN(TB)/T1.bin','INFRASTRUCTURE/I1.gltf','INFRASTRUCTURE/I1.bin','PHOTO/photo.jpg']:z.writestr(n,b'original-'+n.encode())
  self.archive=b.getvalue();self.tmp=tempfile.TemporaryDirectory();self.here=pathlib.Path(self.tmp.name)
  (self.here/'index.json').write_text(json.dumps({'features':[{'attributes':{'SHEETNO':'fixture','Format_glTF':'https://example.invalid/source.zip','REVISIONDATE':0}}]}))
 def tearDown(self):self.tmp.cleanup()
 def request(self,request,timeout):
  span=request.get_header('Range').removeprefix('bytes=');a,b=span.split('-');size=len(self.archive)
  start=max(0,size-int(b)) if not a else int(a);stop=size-1 if not a else int(b)
  return Response(self.archive[start:stop+1],start,size)
 def run_fetch(self,prefixes=None):
  with patch.object(fetch.urllib.request,'urlopen',self.request),contextlib.redirect_stdout(io.StringIO()):fetch.fetch_tiles(self.here,['fixture'],member_prefixes=prefixes)
  folder=self.here/'sources/fixture';return json.loads((folder/'download.json').read_text()),zipfile.ZipFile(folder/'fixture.zip').namelist()
 def test_original_default_retains_all_geometry_without_photo(self):
  record,names=self.run_fetch();self.assertEqual(len(names),6);self.assertTrue(all(n.endswith(('.gltf','.bin')) for n in names));self.assertNotIn('memberPrefixes',record)
 def test_terrain_prefix_retains_original_named_folder_and_hashes(self):
  record,names=self.run_fetch(['TERRAIN']);self.assertEqual(names,['TERRAIN(TB)/T1.gltf','TERRAIN(TB)/T1.bin']);self.assertEqual(record['memberPrefixes'],['TERRAIN']);self.assertEqual(len(record['entries']),2)
  with self.assertRaisesRegex(ValueError,'cannot satisfy'):self.run_fetch()
 def test_full_cache_can_supply_narrower_request(self):
  before,names=self.run_fetch();after,other=self.run_fetch(['INFRASTRUCTURE/']);self.assertEqual(before,after);self.assertEqual(names,other)
if __name__=='__main__':unittest.main()
