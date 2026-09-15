import copy
import gzip
import json
import os
import pathlib
import struct
import tempfile
import unittest
from cached_models import Processor, check_source, safe
from inventory import digest


class CachedModelsTest(unittest.TestCase):
    def setUp(self):
        t = tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.root = pathlib.Path(t.name)
        production = pathlib.Path(os.environ.get('ASTRA_TEST_ROOT', pathlib.Path(__file__).resolve().parents[3]))
        for relative in ['docs/astra-city/mui-wo-buildings/review', 'source-scripts/city/central-completion']:
            p = self.root/relative
            p.parent.mkdir(parents=True, exist_ok=True)
            p.symlink_to(production/relative, target_is_directory=True)
        folder = self.root/'fixture'
        folder.mkdir()
        # Native source coordinates transform to a two-square-metre local triangle.
        data = dict(asset={'version': '2.0'}, scenes=[{'nodes': [0]}], scene=0,
                    nodes=[{'mesh': 0, 'matrix': [1,0,0,0,0,1,0,0,0,0,1,0,834500,0,-816500,1]}],
                    meshes=[{'primitives': [{'attributes': {'POSITION': 0}}]}],
                    buffers=[{'uri': 'm.bin', 'byteLength': 36}],
                    bufferViews=[{'buffer': 0, 'byteOffset': 0, 'byteLength': 36}],
                    accessors=[{'bufferView': 0, 'componentType': 5126, 'count': 3, 'type': 'VEC3'}])
        (folder/'m.gltf').write_text(json.dumps(data))
        (folder/'m.bin').write_bytes(struct.pack('<9f', 0,0,0, 2,0,0, 0,5,2))
        hashes = {p.name: digest(p.read_bytes()) for p in folder.iterdir()}
        spec = dict(id='model1', sourceEntry='m.gltf', vertices=3, triangles=1,
                    sourceHashes=hashes, worldBounds=[[0,0,0],[2,5,2]],
                    officialBuildingCSUIDs=['cs1'], officialMatches=[{'objectId': 1}])
        self.payload = dict(disposition='match-and-pack', priorCompact=[], jobKey='job1',
                            building=dict(uid='landsd/1:0',csuid='cs1',object_id=1, name='Fixture',
                                          rings_json=json.dumps([[[0,0],[2,0],[0,2]]]), source_base=0,source_top=5,structure_type='Tower'),
                            candidate=dict(manifest='fixture/manifest.json',spec=spec,tile='sheet1',revision='2026-01-01',sourceArchiveSHA256='retained'))
        self.processor = Processor(self.root, self.root/'out')

    def test_real_shared_pack_and_idempotent_asset(self):
        r = self.processor(self.payload)
        self.assertEqual(r['outcome'], 'staged-needs-placement-review')
        self.assertEqual(r['proof']['overlapOfSmallerFootprint'], 1)
        raw = (self.root/'out'/r['record']['asset']).read_bytes()
        self.assertEqual(gzip.decompress(raw)[:4], b'glTF')
        before = self.processor.output_bytes
        self.assertEqual(self.processor(self.payload)['record']['sha256'], r['record']['sha256'])
        self.assertEqual(before, self.processor.output_bytes)

    def test_corrupt_derivative_rebuilt_without_touching_source(self):
        r = self.processor(self.payload)
        target = self.root/'out'/r['record']['asset']
        target.write_bytes(b'corrupt')
        rebuilt = self.processor(self.payload)
        self.assertEqual(digest(target.read_bytes()), rebuilt['record']['sha256'])
        check_source(self.root, self.payload['candidate'])

    def test_mismatch_never_writes_model(self):
        p = copy.deepcopy(self.payload)
        p['building']['rings_json'] = json.dumps([[[100,100],[102,100],[100,102]]])
        self.assertEqual(self.processor(p)['outcome'], 'current-footprint-match-failed')
        self.assertFalse(list((self.root/'out').glob('*.glb.gz')))
        p = copy.deepcopy(self.payload)
        p['building']['csuid'] = 'wrong'
        with self.assertRaisesRegex(ValueError, 'identity'):
            self.processor(p)

    def test_hash_path_and_resource_guards(self):
        with self.assertRaisesRegex(ValueError, 'escapes'):
            safe(self.root, '../secret')
        self.processor.max_input_bytes = 1
        self.assertEqual(self.processor(self.payload)['outcome'], 'per-model-resource-limit')
        self.processor.max_input_bytes = 1024**2
        self.processor.max_output_bytes = 1
        self.assertEqual(self.processor(self.payload)['outcome'], 'output-resource-limit')
        (self.root/'fixture/m.bin').write_bytes(b'corrupt')
        with self.assertRaisesRegex(ValueError, 'checksum'):
            check_source(self.root, self.payload['candidate'])

    def test_prior_compact_reused_with_identity_and_hash(self):
        original = self.processor(self.payload)
        self.payload['priorCompact'] = [dict(file='out/'+original['record']['asset'], record=original['record'])]
        self.processor.pack = lambda p: self.fail('Must reuse the verified existing compact asset')
        result = self.processor(self.payload)
        self.assertTrue(result['reusedCompact'])
        self.assertFalse(result['record']['placementReviewed'])


if __name__ == '__main__':
    unittest.main()
