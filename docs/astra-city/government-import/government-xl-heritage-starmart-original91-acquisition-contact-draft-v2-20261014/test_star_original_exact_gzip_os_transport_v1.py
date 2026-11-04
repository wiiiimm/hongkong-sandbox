"""ROOT-only exact package representation and bounded adverse cases."""
from pathlib import Path
import json,hashlib,unittest
from star_original_exact_gzip_os_transport_v1 import restore,NATIVE
D=Path(__file__).resolve().parent;ROOT=D.parents[3]
def raw():
 c=json.loads((D/'input-contract.json').read_text());return(ROOT/c['preservedV1PackedPackagePath']).read_bytes()
class PackageTests(unittest.TestCase):
 def reject(self,change):
  b=bytearray(raw());change(b)
  with self.assertRaises(AssertionError):restore(bytes(b))
 def test_actual_exact_native_container(self):
  b=raw();n,a=restore(b);self.assertEqual(hashlib.sha256(n).hexdigest(),NATIVE);self.assertEqual(n[:9],b[:9]);self.assertEqual(n[10:],b[10:]);self.assertEqual(a['changedByteOffsets'],[9])
 def test_already_changed_OS_not_original_transport(self):self.reject(lambda b:b.__setitem__(9,255))
 def test_deflate_payload_change(self):self.reject(lambda b:b.__setitem__(20,b[20]^1))
 def test_trailer_change(self):self.reject(lambda b:b.__setitem__(-1,b[-1]^1))
 def test_mtime_change(self):self.reject(lambda b:b.__setitem__(4,1))
 def test_missing_byte(self):self.reject(lambda b:b.pop())
if __name__=='__main__':unittest.main()
