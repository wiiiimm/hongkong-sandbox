import io,tarfile,tempfile,unittest
from pathlib import Path
from checkpoint import digest,unpack
class CheckpointTests(unittest.TestCase):
 def make(self,path,name,link=False):
  with tarfile.open(path,'w:gz') as tar:
   row=tarfile.TarInfo(name)
   if link:row.type=tarfile.SYMTYPE;row.linkname='/tmp/outside'
   else:row.size=4
   tar.addfile(row,None if link else io.BytesIO(b'data'))
 def test_verified_archive_extracts_and_refuses_existing_destination(self):
  with tempfile.TemporaryDirectory() as temp:
   p=Path(temp);a=p/'cache.tar.gz';name='source-scripts/city/citywide-source/cache/test.bin';self.make(a,name)
   unpack(a,digest(a),p/'restored');self.assertEqual((p/'restored'/name).read_bytes(),b'data')
   with self.assertRaises(ValueError):unpack(a,digest(a),p/'restored')
   with self.assertRaises(ValueError):unpack(a,'0'*64,p/'bad')
   self.assertFalse((p/'bad').exists())
 def test_unsafe_member_never_creates_destination(self):
  with tempfile.TemporaryDirectory() as temp:
   p=Path(temp);a=p/'cache.tar.gz'
   for name,link in [('../outside',False),('source-scripts/city/citywide-source/cache/link',True),('.env.modelling',False)]:
    self.make(a,name,link)
    with self.assertRaises(ValueError):unpack(a,digest(a),p/'bad')
    self.assertFalse((p/'bad').exists())
if __name__=='__main__':unittest.main()
