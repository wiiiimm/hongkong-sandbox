import io,json,pathlib,struct,tempfile,unittest,zipfile
from unittest.mock import patch
import download as d
class DownloadTests(unittest.TestCase):
 def fixture(self):
  stream=io.BytesIO();model='B345321814801063C0';base='BUILDING/'+model+'/'
  with zipfile.ZipFile(stream,'w',zipfile.ZIP_DEFLATED) as z:
   z.writestr(base+model+'.gltf',json.dumps({'buffers':[{'uri':'geometry.bin'}]}));z.writestr(base+'geometry.bin',b'geometry');z.writestr('TERRAIN/unused.bin',b'not requested'*5000)
  raw=stream.getvalue();end=raw.rfind(b'PK\x05\x06');offset=struct.unpack('<4s4H2LH',raw[end:end+22])[6];directory=raw[offset:];infos,check=d.ac.parse_directory(directory)
  entries=[e for e in infos if e.filename.startswith('BUILDING/')]
  row={'sheet':'test','sourceURL':'https://download.map.gov.hk/test.zip','revision':0,'etag':'original','archiveBytes':len(raw),'directorySHA256':d.ac.sha(directory),'models':[{'members':[{'name':e.filename,'crc32':e.CRC,'headerOffset':e.header_offset,'compressedBytes':e.compress_size,'decodedBytes':e.file_size} for e in entries]}]}
  return raw,directory,row
 def test_grouped_range_and_restart_reuse(self):
  raw,directory,row=self.fixture();calls=[]
  class Net:
   def __init__(self,*a,**k):self.initial=0;self.data={'receivedBytes':0}
   def get(self,url,n,span,etag):
    calls.append(span);self.data['receivedBytes']+=n;start,end=map(int,span.split('-'));return raw[start:end+1],{}
  with tempfile.TemporaryDirectory() as temp,patch.object(d.ac,'Network',Net):
   p=pathlib.Path(temp);(p/'directory').write_bytes(directory)
   record=d.acquire(row,p/'directory',p/'out');self.assertEqual(len(calls),1);self.assertEqual(len(record['entries']),2)
   again=d.acquire(row,p/'directory',p/'out');self.assertEqual(record['sha256'],again['sha256']);self.assertEqual(len(calls),1)
 def test_cold_rebuild_is_identical_across_local_clocks(self):
  raw,directory,row=self.fixture()
  class Net:
   def __init__(self,*a,**k):self.initial=0;self.data={'receivedBytes':0};self.cap=k.get('cap',0)
   def get(self,url,n,span,etag):
    self.data['receivedBytes']+=n;start,end=map(int,span.split('-'));return raw[start:end+1],{}
  with tempfile.TemporaryDirectory() as temp,patch.object(d.ac,'Network',Net):
   p=pathlib.Path(temp);(p/'directory').write_bytes(directory)
   records=[]
   for index,year in enumerate((2001,2031)):
    with patch('zipfile.time.localtime',return_value=(year,2,3,4,5,6,0,0,0)):
     records.append(d.acquire(row,p/'directory',p/str(index)))
   self.assertEqual(records[0]['sha256'],records[1]['sha256'])
   with zipfile.ZipFile(p/'0/test.zip') as z:
    self.assertTrue(all(e.date_time==(1980,1,1,0,0,0)for e in z.infolist()))
 def test_legacy_compact_cache_rediscovers_missing_dependencies(self):
  raw,directory,row=self.fixture();row['models'][0]['members']=[m for m in row['models'][0]['members']if m['name'].endswith('.gltf')];calls=[]
  class Net:
   def __init__(self,*a,**k):self.initial=0;self.data={'receivedBytes':0};self.cap=k.get('cap',0)
   def get(self,url,n,span,etag):
    calls.append(span);self.data['receivedBytes']+=n;start,end=map(int,span.split('-'));return raw[start:end+1],{}
  with tempfile.TemporaryDirectory()as temp,patch.object(d.ac,'Network',Net):
   p=pathlib.Path(temp);(p/'directory').write_bytes(directory);out=p/'out';out.mkdir();archive=out/'test.zip'
   name=row['models'][0]['members'][0]['name']
   with zipfile.ZipFile(io.BytesIO(raw))as source,zipfile.ZipFile(archive,'w')as compact:compact.writestr(name,source.read(name))
   d.ac.write(out/'download.json',{'source':row['sourceURL'],'sourceETag':row['etag'],'directorySHA256':row['directorySHA256'],'sha256':d.ac.sha(archive.read_bytes())})
   record=d.acquire(row,p/'directory',out)
   self.assertEqual(record['dependencyScanVersion'],1);self.assertEqual(len(calls),1)
   self.assertEqual(next(e['origin']for e in record['entries']if e['name']==name),'retained-verified-cache')
   with zipfile.ZipFile(archive)as z:self.assertEqual(z.read(name.rsplit('/',1)[0]+'/geometry.bin'),b'geometry')
 def test_expanded_selection_reuses_partial_compact_cache(self):
  raw,directory,row=self.fixture();calls=[]
  first=json.loads(json.dumps(row));first['models'][0]['members']=[m for m in first['models'][0]['members'] if m['name'].endswith('.bin')]
  class Net:
   def __init__(self,*a,**k):self.initial=0;self.data={'receivedBytes':0};self.cap=k.get('cap',0)
   def get(self,url,n,span,etag):
    calls.append(span);self.data['receivedBytes']+=n;start,end=map(int,span.split('-'));return raw[start:end+1],{}
  with tempfile.TemporaryDirectory() as temp,patch.object(d.ac,'Network',Net):
   p=pathlib.Path(temp);(p/'directory').write_bytes(directory)
   initial=d.acquire(first,p/'directory',p/'out');self.assertEqual(len(initial['entries']),1)
   expanded=d.acquire(row,p/'directory',p/'out');self.assertEqual(len(expanded['entries']),2)
   self.assertEqual(len(calls),2)
   self.assertEqual(next(e['origin'] for e in expanded['entries'] if e['name'].endswith('.bin')),'retained-verified-cache')
   again=d.acquire(row,p/'directory',p/'out');self.assertEqual(expanded['sha256'],again['sha256']);self.assertEqual(len(calls),2)
   with zipfile.ZipFile(p/'out/test.zip') as cached,zipfile.ZipFile(io.BytesIO(raw)) as source:
    for name in cached.namelist():self.assertEqual(cached.read(name),source.read(name))
 def test_crc_corruption_and_unsafe_paths_rejected(self):
  raw,directory,row=self.fixture();infos,_=d.ac.parse_directory(directory);entry=infos[0];bad=bytearray(raw[entry.header_offset:]);bad[35]^=1
  with self.assertRaises(Exception):d.ac.unpack_member(bytes(bad),entry)
  for name in ['../secret','/secret','folder\\secret']:
   with self.assertRaises(ValueError):d.safe(name)
if __name__=='__main__':unittest.main()
