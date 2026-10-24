import copy,gzip,hashlib,json,tempfile,unittest
from pathlib import Path
from exact_frozen_finite_chunk_hydration_draft_v1_20261012 import hydrate
class Tests(unittest.TestCase):
 def setUp(self):self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
 def tearDown(self):self.temp.cleanup()
 def write(self,start=0,stop=2):
  c=dict(uid='u',sourceSHA256='s',worldSHA256='w',groundSHA256='g',completeGroundFaces=3,firstFace=start,exclusiveLastFace=stop,codeRefs=[{'path':'historical-producer','sha256':'old-code'}],ordinaryThresholdM='-1/2');rows=[dict(face=i,originalBody=0,selection=dict(completeGroundSHA256='g',completeGroundFacetCount=3,everyNoncandidateStrictlyDisjoint=True,touchingAndCollapsedProjectionsRetained=True,selectedOriginalGroundFaces=[2]),originalGroundFaceBySelectedKernelFace=[2],exactLowerM='-3/2',ordinaryFiniteProved=False,allRefinedFiniteColumnPairs=[{'proof':'unchanged nested proof'}])for i in range(start,stop)];path=self.root/f'{start}.json.gz';raw=gzip.compress(json.dumps(dict(contract=c,rows=rows)).encode(),mtime=0);path.write_bytes(raw);return dict(actualRef=dict(path=path.name,sha256=hashlib.sha256(raw).hexdigest()),originalContract=copy.deepcopy(c)),rows
 def test_exact_rows_and_historical_contract_preserved(self):
  a,r=self.write();b,s=self.write(2,4);out,refs=hydrate(self.root,[b,a],{i:0 for i in range(4)});self.assertEqual(out[('w','g')],r+s);self.assertEqual(a['originalContract']['codeRefs'][0]['sha256'],'old-code')
 def test_changed_proof_bytes_rejected(self):
  a,_=self.write();p=self.root/a['actualRef']['path'];q=json.loads(gzip.decompress(p.read_bytes()));q['rows'][0]['exactLowerM']='0';p.write_bytes(gzip.compress(json.dumps(q).encode()))
  with self.assertRaises(AssertionError):hydrate(self.root,[a],{0:0,1:0})
 def test_wrong_source_contract(self):
  a,_=self.write();a['originalContract']['sourceSHA256']='changed'
  with self.assertRaises(AssertionError):hydrate(self.root,[a],{0:0,1:0})
 def test_wrong_world_ground_or_code_contract(self):
  for key in ['worldSHA256','groundSHA256','codeRefs']:
   a,_=self.write();a['originalContract'][key]='wrong'
   with self.assertRaises(AssertionError):hydrate(self.root,[a],{0:0,1:0})
 def test_gap_rejected(self):
  a,_=self.write();b,_=self.write(3,5)
  with self.assertRaises(AssertionError):hydrate(self.root,[a,b],{i:0 for i in range(5)})
 def test_duplicate_chunk_rejected(self):
  a,_=self.write()
  with self.assertRaises(AssertionError):hydrate(self.root,[a,a],{0:0,1:0})
 def test_source_body_mapping_rejected(self):
  a,_=self.write()
  with self.assertRaises(AssertionError):hydrate(self.root,[a],{0:1,1:0})
 def test_missing_or_reordered_row_rejected(self):
  a,_=self.write();p=self.root/a['actualRef']['path'];q=json.loads(gzip.decompress(p.read_bytes()));q['rows'].reverse();raw=gzip.compress(json.dumps(q).encode());p.write_bytes(raw);a['actualRef']['sha256']=hashlib.sha256(raw).hexdigest()
  with self.assertRaises(AssertionError):hydrate(self.root,[a],{0:0,1:0})
 def test_path_escape_rejected(self):
  a,_=self.write();a['actualRef']['path']='../'+a['actualRef']['path']
  with self.assertRaises(AssertionError):hydrate(self.root,[a],{0:0,1:0})
if __name__=='__main__':unittest.main()
