"""A changed archive never permits changed or approximately equivalent assets."""
import gzip,hashlib,unittest
from revised_sheet_exact_asset_recovery_v1_20261028 import shape_prepare

def digest(raw):return hashlib.sha256(raw).hexdigest()

class ExactAssetBytes(unittest.TestCase):
 def test_identical_asset_is_recovered_verbatim(self):
  raw=gzip.compress(b'glTF pinned original payload',mtime=0)
  self.assertEqual(shape_prepare.canonical_bytes(raw,digest(raw)),raw)
 def test_changed_geometry_payload_cannot_reuse_original_hash(self):
  old=gzip.compress(b'glTF original geometry',mtime=0);new=gzip.compress(b'glTF changed geometry',mtime=0)
  with self.assertRaises(ValueError):shape_prepare.canonical_bytes(new,digest(old))
 def test_same_payload_with_other_changed_header_is_not_silently_approved(self):
  old=gzip.compress(b'glTF unchanged geometry',mtime=0);new=gzip.compress(b'glTF unchanged geometry',mtime=1)
  self.assertEqual(gzip.decompress(old),gzip.decompress(new))
  with self.assertRaises(ValueError):shape_prepare.canonical_bytes(new,digest(old))
 def test_only_exact_pinned_platform_header_is_reconstructed(self):
  raw=gzip.compress(b'glTF unchanged geometry',mtime=0);pinned=raw[:9]+bytes([255 if raw[9]==3 else 3])+raw[10:]
  recovered=shape_prepare.canonical_bytes(raw,digest(pinned));self.assertEqual(recovered,pinned);self.assertEqual(gzip.decompress(recovered),gzip.decompress(raw))

if __name__=='__main__':unittest.main()
