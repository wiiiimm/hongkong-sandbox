from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import uuid
import north_pair_nonwall_topology_v1_20261027 as worker


class StartupCleanup(unittest.TestCase):
    def setUp(self):
        self.lease = dict(owner='own-test-lease', token=uuid.uuid4(), lease_until=datetime.now(timezone.utc))

    def test_database_types_serialized_and_normal_child_release_respected(self):
        with patch.object(worker, 'save') as save, patch.object(worker.subprocess, 'run', return_value=SimpleNamespace(returncode=0)), patch.object(worker.reservations, 'owns', return_value=False), patch.object(worker.reservations, 'release') as release:
            worker.execute_reserved(self.lease, Path('/tmp/test-unused.json'), ['diagnostic'])
            written = save.call_args.args[1]
            self.assertEqual(written['token'], str(self.lease['token']))
            self.assertIsInstance(written['lease_until'], str)
            release.assert_not_called()

    def test_failed_receipt_write_releases_own_unused_lease(self):
        with patch.object(worker, 'save', side_effect=OSError('write failed')), patch.object(worker.subprocess, 'run') as run, patch.object(worker.reservations, 'owns', return_value=True), patch.object(worker.reservations, 'release', return_value={'ok': True}) as release:
            with self.assertRaises(OSError): worker.execute_reserved(self.lease, Path('/tmp/test-unused.json'), ['diagnostic'])
            run.assert_not_called()
            release.assert_called_once_with(self.lease)

    def test_failed_child_releases_own_remaining_lease(self):
        with patch.object(worker, 'save'), patch.object(worker.subprocess, 'run', return_value=SimpleNamespace(returncode=1)), patch.object(worker.reservations, 'owns', return_value=True), patch.object(worker.reservations, 'release', return_value={'ok': True}) as release:
            with self.assertRaises(AssertionError): worker.execute_reserved(self.lease, Path('/tmp/test-unused.json'), ['diagnostic'])
            release.assert_called_once_with(self.lease)


if __name__ == '__main__': unittest.main()
