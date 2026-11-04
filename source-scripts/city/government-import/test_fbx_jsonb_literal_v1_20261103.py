import json,unittest
from fbx_jsonb_literal_v1_20261103 import jsonb_literals
class LiteralBinding(unittest.TestCase):
    def test_exact_bytes_and_display_roundtrip(self):
        raw=b'Root\0\x01Model';before=dict(rawBytesHex=raw.hex(),decodedUTF8=raw.decode())
        after=jsonb_literals(before)
        self.assertEqual(bytes.fromhex(after['rawBytesHex']),raw)
        self.assertEqual(json.loads('"'+after['decodedUTF8Escaped']+'"'),raw.decode())
        self.assertNotIn('\0',after['decodedUTF8Escaped'])
    def test_nested_names_and_backslashes(self):
        raw=b'roof\\literal"\0';value=[dict(name=dict(rawBytesHex=raw.hex(),decodedUTF8=raw.decode()))]
        after=jsonb_literals(value)[0]['name']
        self.assertEqual(json.loads('"'+after['decodedUTF8Escaped']+'"'),raw.decode())
    def test_wrong_display_cannot_replace_original(self):
        with self.assertRaises(AssertionError):jsonb_literals(dict(rawBytesHex='00',decodedUTF8='different'))
    def test_unbound_nul_is_rejected(self):
        with self.assertRaises(AssertionError):jsonb_literals(dict(name='unknown\0'))
    def test_numeric_geometry_and_source_hash_unchanged(self):
        value=dict(controlPoints=[[1.25,2,3]],sourceSHA256='original',flags=[True,None])
        self.assertEqual(jsonb_literals(value),value)
if __name__=='__main__':unittest.main()
