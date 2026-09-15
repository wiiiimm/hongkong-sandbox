"""CRC/ETag/range and narrow NUL-only classification tests, without network calls."""
import importlib.util
import io
from pathlib import Path
import struct
import unittest
from unittest.mock import patch
import zipfile
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('native_defect_test',HERE/'verify_source_defects.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)


def archive(payload):
    buffer=io.BytesIO();model='B123456789001063C0'
    with zipfile.ZipFile(buffer,'w',zipfile.ZIP_DEFLATED)as z:z.writestr(f'BUILDING/{model}/{model}.gltf',payload)
    raw=buffer.getvalue();end=raw.rfind(b'PK\x05\x06');offset=struct.unpack('<4s4H2LH',raw[end:end+22])[6]
    return raw,raw[offset:],model


class Response:
    def __init__(self,raw,start,end,etag='"fixture"'):
        self.status=206;self.headers={'ETag':etag,'Content-Range':f'bytes {start}-{end}/{len(raw)}'};self.body=raw[start:end+1]
    def read(self,n):return self.body[:n]
    def __enter__(self):return self
    def __exit__(self,*args):pass


class DefectTests(unittest.TestCase):
    def verify(self,payload,etag='"fixture"'):
        raw,directory,model=archive(payload)
        def opener(request,timeout):
            start,end=map(int,request.headers['Range'].removeprefix('bytes=').split('-'));return Response(raw,start,end,etag)
        with patch.object(v.urllib.request,'urlopen',opener):return v.verify_member({'sourceURL':'https://example.invalid/archive.zip','etag':'"fixture"'},directory,model)

    def test_only_zero_plus_crlf_is_confirmed(self):
        row=self.verify(b'\x00'*2094+b'\r\n');self.assertEqual(row['classification'],'confirmed-source-corrupt');self.assertEqual(row['bytes'],2096);self.assertEqual(row['nulBytes'],2094);self.assertTrue(row['verification']['contentRangeVerified'])

    def test_valid_or_other_malformed_json_is_not_auto_repaired(self):
        for raw in [b'{"asset":{"version":"2.0"}}',b'\x00{}\r\n',b'\x00\x00\n']:
            self.assertEqual(self.verify(raw)['classification'],'unclassified-source-json-failure')

    def test_source_revision_is_pinned(self):
        with self.assertRaisesRegex(ValueError,'revision mismatch'):self.verify(b'\x00'*10+b'\r\n','"different"')

if __name__=='__main__':unittest.main()
