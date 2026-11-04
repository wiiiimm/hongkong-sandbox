"""Bounded ZIP64 compatibility without allocating or fetching giant archives."""
import io,struct,unittest,zipfile
from bounded_zip_directory_v1_20261103 import metadata,parse_window,TailFile,MAX_DIRECTORY_BYTES


class Directories(unittest.TestCase):
    def ordinary(self):
        data=io.BytesIO()
        with zipfile.ZipFile(data,'w',zipfile.ZIP_DEFLATED) as z:z.writestr('BUILDING/example.gltf',b'{}')
        return data.getvalue()
    def zip64(self):
        normal=self.ordinary();end=normal.rfind(b'PK\x05\x06');fields=struct.unpack('<4s4H2LH',normal[end:end+22]);central=normal[fields[6]:end]
        offset=(1<<32)+1024;position=offset+len(central)
        end64=struct.pack('<4sQ2H2L4Q',b'PK\x06\x06',44,45,45,0,0,1,1,len(central),offset)
        locator=struct.pack('<4sLQL',b'PK\x06\x07',0,position,1)
        end32=struct.pack('<4s4H2LH',b'PK\x05\x06',0,0,1,1,len(central),0xffffffff,0)
        raw=central+end64+locator+end32;size=offset+len(raw);padding=65536-len(raw)
        return b'\0'*padding+raw,offset-padding,size
    def test_ordinary_directory(self):
        raw=self.ordinary();m=metadata(raw,0,len(raw));entries=parse_window(raw,0,len(raw),m)
        self.assertFalse(m['zip64']);self.assertEqual(entries[0].filename,'BUILDING/example.gltf')
    def test_zip64_absolute_offsets_without_archive_allocation(self):
        raw,start,size=self.zip64();m=metadata(raw,start,size);entries=parse_window(raw,start,size,m)
        self.assertTrue(m['zip64']);self.assertGreater(size,1<<32);self.assertEqual(len(raw),65536)
        self.assertEqual(entries[0].filename,'BUILDING/example.gltf')
    def test_split_archive_rejected(self):
        raw,start,size=self.zip64();at=raw.rfind(b'PK\x06\x07');bad=bytearray(raw);struct.pack_into('<L',bad,at+4,1)
        with self.assertRaises(AssertionError):metadata(bytes(bad),start,size)
    def test_missing_zip64_locator_rejected(self):
        raw,start,size=self.zip64();bad=raw.replace(b'PK\x06\x07',b'BAD!')
        with self.assertRaises(AssertionError):metadata(bad,start,size)
    def test_oversized_directory_rejected_before_fetch(self):
        raw,start,size=self.zip64();at=raw.rfind(b'PK\x06\x06');bad=bytearray(raw);struct.pack_into('<Q',bad,at+40,MAX_DIRECTORY_BYTES+1)
        with self.assertRaises(AssertionError):metadata(bytes(bad),start,size)
    def test_wrong_zip64_position_rejected(self):
        raw,start,size=self.zip64();at=raw.rfind(b'PK\x06\x07');bad=bytearray(raw);struct.pack_into('<Q',bad,at+8,123)
        with self.assertRaises(AssertionError):metadata(bytes(bad),start,size)
    def test_payload_seek_rejected(self):
        raw,start,size=self.zip64();view=TailFile(raw,start,size)
        with self.assertRaises(AssertionError):view.seek(0)


if __name__=='__main__':unittest.main()
