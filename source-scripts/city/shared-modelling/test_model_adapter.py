from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch
import model_adapter
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'landmark-resume'))
import r2_snapshot

class AdapterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.store = r2_snapshot.LocalStore(self.root / 'store')
        self.codepatch = patch.object(model_adapter, 'code_hashes', return_value={'fixture': 'hash'}); self.codepatch.start(); self.addCleanup(self.codepatch.stop)
        self.output_paths = []
        paths = self.output_paths
        class Processor:
            def __init__(self, root, out, **kwargs): self.out = out; paths.append(out)
            def __call__(self, payload):
                if payload.get('held'): return {'outcome': 'current-footprint-match-failed', 'uid': 'fixture'}
                dest = self.out / 'fixture.glb.gz'; dest.write_bytes(b'compressed-fixture')
                return {'outcome': 'staged-needs-placement-review', 'record': {'asset': dest.name, 'sha256': r2_snapshot.digest(dest), 'bytes': dest.stat().st_size}, 'reusedCompact': True}
        cached = types.SimpleNamespace(Processor=Processor, tool_hash=lambda root: 'verified-tool')
        self.patch = patch.object(model_adapter, 'modules', return_value=(cached, r2_snapshot)); self.patch.start(); self.addCleanup(self.patch.stop)
    def wrapper(self, inner):
        return {'snapshot': 'snapshot', 'sourceJobId': 'source', 'sourceSelection': 'selection', 'adapterCode': {'fixture': 'hash'}, 'adapterPayload': inner}
    def test_verifies_object_and_removes_temporary_path(self):
        payload = self.wrapper({'toolSHA256': 'verified-tool'})
        result = model_adapter.process(payload, self.root, self.store)
        self.assertEqual(payload['adapterPayload'], {'toolSHA256': 'verified-tool'})
        self.assertNotIn('asset', result['record'])
        self.assertFalse(result['publicationApproved'])
        self.assertEqual((self.store.root / result['object']['key']).read_bytes(), b'compressed-fixture')
        self.assertFalse(self.output_paths[0].exists())
        model_adapter.process(payload, self.root, self.store)
        self.assertNotEqual(self.output_paths[0], self.output_paths[1])
    def test_stale_tools_refuse_before_processing(self):
        with self.assertRaisesRegex(ValueError, 'fingerprint'): model_adapter.process(self.wrapper({'toolSHA256': 'old'}), self.root, self.store)
        self.assertFalse(self.output_paths)
    def test_adapter_code_mismatch_refuses(self):
        payload = self.wrapper({'toolSHA256': 'verified-tool'}); payload['adapterCode'] = {}
        with self.assertRaisesRegex(ValueError, 'adapter code'): model_adapter.process(payload, self.root, self.store)
        self.assertFalse(self.output_paths)
    def test_holds_do_not_upload(self):
        result = model_adapter.process(self.wrapper({'toolSHA256': 'verified-tool', 'held': True}), self.root, self.store)
        self.assertEqual(result['outcome'], 'current-footprint-match-failed')
        self.assertNotIn('object', result); self.assertFalse(self.store.root.exists())
    def test_failed_readback_does_not_return_success(self):
        with patch.object(self.store, 'get', side_effect=ValueError('corrupt remote object')):
            with self.assertRaisesRegex(ValueError, 'corrupt'): model_adapter.process(self.wrapper({'toolSHA256': 'verified-tool'}), self.root, self.store)
        self.assertFalse(self.output_paths[0].exists())

if __name__ == '__main__': unittest.main()
