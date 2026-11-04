"""Launcher lease serialization and failure cleanup without database access."""
import datetime
import json
from pathlib import Path
import runpy
import tempfile
import types
import unittest
from unittest.mock import Mock, patch
import uuid

SCRIPT = Path(__file__).with_name('nam_cheong_after_island_current_worker_v1_20261023.py')


class WorkerLeaseTests(unittest.TestCase):
    def execute(self, failure=False):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            lease = dict(token=uuid.uuid4(), owner='test', lease_until=datetime.datetime.now(datetime.timezone.utc))
            reservations = Mock()
            reservations.claim.return_value = dict(ok=True, reservation=lease)
            reservations.owns.return_value = True
            reservations.release.return_value = dict(ok=True)
            def save(path, value):
                raw = json.dumps(value)
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(raw)
            stub = types.ModuleType('run')
            stub.ROOT = stub.HERE = root
            stub.save, stub.reservations = save, reservations
            with patch.dict('sys.modules', {'run': stub}):
                g = runpy.run_path(str(SCRIPT))
            command = Mock(return_value=types.SimpleNamespace(returncode=0))
            if failure:
                command.side_effect = OSError('test spawn failure')
            with patch.object(g['subprocess'], 'run', command):
                with self.assertRaises(OSError if failure else SystemExit):
                    g['main']()
            saved = json.loads((root / 'local' / g['BATCH'] / 'reservation.json').read_text())
            self.assertEqual(saved['token'], str(lease['token']))
            self.assertIsInstance(saved['lease_until'], str)
            reservations.release.assert_called_once_with(lease)
            reservations.claim.assert_called_once()
            command.assert_called_once()

    def test_uuid_and_datetime_lease_is_saved_and_released(self):
        self.execute()

    def test_spawn_failure_releases_lease(self):
        self.execute(failure=True)


if __name__ == '__main__':
    unittest.main()
