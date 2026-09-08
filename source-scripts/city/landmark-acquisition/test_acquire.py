import importlib.util,io,json,pathlib,struct,tempfile,unittest,zipfile
from unittest.mock import patch
HERE=pathlib.Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('landmark_acquire',HERE/'acquire.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)

def fixture():
 data=io.BytesIO()
 with zipfile.ZipFile(data,'w',zipfile.ZIP_DEFLATED)as archive:
  archive.writestr('BUILDING/B1234567890.gltf',b'{"asset":{"version":"2.0"}}')
  archive.writestr('BUILDING/B1234567890.bin',bytes(range(256))*4)
 raw=data.getvalue();end=raw.rfind(b'PK\x05\x06');fields=struct.unpack('<4s4H2LH',raw[end:end+22]);return raw,raw[fields[6]:]

class AcquisitionTests(unittest.TestCase):
 def test_complete_directory_preserves_native_offsets_and_detects_partial_directory(self):
  raw,directory=fixture();infos,check=a.parse_directory(directory)
  self.assertEqual(check['completeEntries'],2)
  for entry in infos:self.assertEqual(raw[entry.header_offset:entry.header_offset+4],b'PK\x03\x04')
  with self.assertRaises(AssertionError):a.parse_directory(directory[2:])
  with self.assertRaises(AssertionError):a.parse_directory(directory[:-1])
 def test_member_range_decodes_exact_original_bytes_and_checks_crc(self):
  raw,directory=fixture();infos,check=a.parse_directory(directory)
  with zipfile.ZipFile(io.BytesIO(raw))as archive:
   for i,entry in enumerate(infos):
    end=infos[i+1].header_offset if i+1<len(infos)else check['centralDirectoryOffset']
    self.assertEqual(a.unpack_member(raw[entry.header_offset:end],entry),archive.read(entry.filename))
   entry=infos[0];original_crc=entry.CRC;entry.CRC=original_crc^1
   with self.assertRaises(AssertionError):a.unpack_member(raw[entry.header_offset:infos[1].header_offset],entry)
 def test_identity_summary_top_level_parts_override_rows_without_parts(self):
  target={'uid':'landsd/123:0','csuid':'1234567890T20050101','state':'not-in-retained-staged-models','identityProposalGroups':['tower']}
  data={'rows':[{'id':'tower','members':[target]}],'parts':[target,{'uid':'landsd/456:0','state':'candidate-staged'}]}
  self.assertEqual(a.target_entries(data),[(target,['tower'])])
  self.assertEqual(a.target_entries({'targets':['landsd/789:0']}),[({'uid':'landsd/789:0'},[])])
 def test_parallel_reservations_cannot_exceed_one_durable_cap(self):
  with tempfile.TemporaryDirectory()as folder:
   path=pathlib.Path(folder)/'ledger.json';network=a.Network(path,cap=100)
   def request(_):
    try:network.get('https://example.test/model.zip',30,'0-29')
    except (TimeoutError,a.BudgetExceeded):pass
   with patch.object(a.urllib.request,'urlopen',side_effect=TimeoutError('interrupted')):
    with a.concurrent.futures.ThreadPoolExecutor(max_workers=8)as pool:list(pool.map(request,range(20)))
   retained=json.loads(path.read_text());self.assertEqual(retained['chargedBytes'],90);self.assertEqual(len(retained['requests']),3)
 def test_atomic_json_reports_remain_complete_during_parallel_writes(self):
  with tempfile.TemporaryDirectory()as folder:
   path=pathlib.Path(folder)/'state.json';a.write(path,{'value':'initial'})
   def writer(number):
    for _ in range(20):a.write(path,{'value':str(number)*10000})
   with a.concurrent.futures.ThreadPoolExecutor(max_workers=4)as pool:
    futures=[pool.submit(writer,number)for number in range(4)]
    while not all(future.done()for future in futures):self.assertIsInstance(a.read(path)['value'],str)
    for future in futures:future.result()
   self.assertEqual(list(path.parent.glob('*.part')),[])
 def test_cap_is_reserved_before_io_and_survives_an_interrupted_request(self):
  with tempfile.TemporaryDirectory()as folder:
   path=pathlib.Path(folder)/'ledger.json';network=a.Network(path,cap=100)
   with patch.object(a.urllib.request,'urlopen',side_effect=TimeoutError('interrupted'))as fetch:
    with self.assertRaises(TimeoutError):network.get('https://example.test/model.zip',75,'0-74')
    self.assertEqual(fetch.call_count,1)
   resumed=a.Network(path,cap=100)
   with patch.object(a.urllib.request,'urlopen')as fetch:
    with self.assertRaises(a.BudgetExceeded):resumed.get('https://example.test/model.zip',26,'75-100')
    fetch.assert_not_called()
   self.assertEqual(resumed.data['chargedBytes'],75)
 def test_ignored_ranges_are_rejected_without_reading_archive_body(self):
  class Response:
   status=200;headers={'Content-Length':'999999999'}
   def __enter__(self):return self
   def __exit__(self,*args):pass
   def read(self,*args):raise AssertionError('must not read a whole archive')
  with tempfile.TemporaryDirectory()as folder,patch.object(a.urllib.request,'urlopen',return_value=Response()):
   network=a.Network(pathlib.Path(folder)/'ledger.json',cap=100)
   with self.assertRaisesRegex(ValueError,'refused bounded'):network.get('https://example.test/model.zip',50,'0-49')
   self.assertEqual(network.data['receivedBytes'],0)
 def test_only_provenance_response_headers_are_retained(self):
  headers=a.provenance_headers({'ETag':'"source"','content-range':'bytes 1-3/40','Set-Cookie':'transient','X-Request-Id':'temporary','Last-Modified':'source date'})
  self.assertEqual(headers,{'ETag':'"source"','Content-Range':'bytes 1-3/40','Last-Modified':'source date'})

if __name__=='__main__':unittest.main()
