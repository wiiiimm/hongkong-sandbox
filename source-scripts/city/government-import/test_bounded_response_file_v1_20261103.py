import hashlib
import io
import tempfile
import unittest
from pathlib import Path
from bounded_response_file_v1_20261103 import receive


class BoundedResponseTests(unittest.TestCase):
    def test_complete_and_exact_limit(self):
        for data in [b'', b'abc', b'x' * (4 * 1024 * 1024 + 3)]:
            with tempfile.TemporaryDirectory() as root:
                path = Path(root) / 'data'
                result = receive(io.BytesIO(data), path, max(1, len(data)))
                self.assertEqual(path.read_bytes(), data)
                self.assertEqual(result, dict(receivedBytes=len(data), sha256=hashlib.sha256(data).hexdigest()))

    def test_overflow_preserves_only_bounded_prefix(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / 'data'
            source = io.BytesIO(b'abcdef')
            counts = []
            with self.assertRaisesRegex(ValueError, 'cap'):
                receive(source, path, 3, counts.append)
            self.assertEqual(path.read_bytes(), b'abcd')
            self.assertEqual(source.tell(), 4)
            self.assertEqual(counts, [4])

    def test_no_overwrite_or_budget_reset(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / 'data'
            path.write_bytes(b'old')
            with self.assertRaises(AssertionError):
                receive(io.BytesIO(b'new'), path, 3)
            self.assertEqual(path.read_bytes(), b'old')

    def test_interruption_keeps_actual_partial_bytes(self):
        class Interrupted:
            calls = 0
            def read(self, maximum):
                self.calls += 1
                if self.calls == 1:
                    return b'abc'
                raise TimeoutError('interrupted')
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / 'data'
            with self.assertRaises(TimeoutError):
                receive(Interrupted(), path, 8)
            self.assertEqual(path.read_bytes(), b'abc')


if __name__ == '__main__':
    unittest.main()
