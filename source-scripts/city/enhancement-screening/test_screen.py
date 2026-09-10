import contextlib
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest
import uuid
from unittest.mock import patch
import screen


class ScreeningTests(unittest.TestCase):
    def setUp(self):
        self.uid = 'landsd/89275:0'
        self.row = {'uid': self.uid, 'inputHash': 'a'*64, 'state': 'unassessed'}
        self.plan = {'rows': [self.row]}
        path = Path(__file__).resolve()
        self.entry = {'uid': self.uid, 'inputHash': 'a'*64, 'decision': 'good-to-go',
                      'reason': 'Fixture only: current silhouette is sufficient',
                      'evidence': str(path.relative_to(screen.ROOT)),
                      'evidenceHash': hashlib.sha256(path.read_bytes()).hexdigest()}

    def test_skip_does_not_schedule_unassessed(self):
        rows = [{'uid': str(i), 'state': state} for i, state in enumerate(
            ['good-to-go','enhanced','enhancement-required','unassessed'])]
        groups = screen.partition(rows)
        self.assertEqual([len(groups[k]) for k in ['skip','enhance','assess']], [2,1,1])

    def test_changed_inputs_or_evidence_reject_acceptance(self):
        for change in [{'inputHash': 'b'*64}, {'evidenceHash': 'b'*64},
                       {'decision': 'pending'}, {'reason': ''}]:
            with self.assertRaises(ValueError):
                screen.prepare_entries([{**self.entry, **change}], self.plan)

    def test_atomic_validation_and_identity(self):
        self.assertEqual(len(screen.prepare_entries([self.entry], self.plan)), 1)
        with self.assertRaises(ValueError):
            screen.prepare_entries([self.entry, self.entry], self.plan)
        with self.assertRaises(ValueError):
            screen.prepare_entries([{**self.entry, 'uid': 'missing'}], self.plan)

    @unittest.skipUnless(os.getenv('SCREENING_LIVE_TEST') == '1', 'Opt-in rollback-only Neon test')
    def test_database_history_retries_and_fencing(self):
        connect, reservations = screen.database()
        key = 'screen-test-' + uuid.uuid4().hex
        with connect() as con:
            with con.transaction(force_rollback=True):
                @contextlib.contextmanager
                def shared():
                    yield con
                group = {'owner': key, 'token': uuid.uuid4(), 'resources': ['building:'+self.uid]}
                with tempfile.TemporaryDirectory() as tmp, patch.object(screen, 'database', return_value=(shared, reservations)), patch.object(reservations, '_current', return_value=group) as current:
                    receipt = Path(tmp)/'receipt.json'; receipt.write_text('{}')
                    self.assertEqual(screen.record([self.entry], receipt, key, self.plan), {'recorded': 1})
                    self.assertEqual(screen.record([self.entry], receipt, key, self.plan), {'reused': 1})
                    revised = {**self.entry, 'decision': 'enhancement-required', 'reason': 'Fixture rework'}
                    with self.assertRaises(ValueError):
                        screen.record([revised], receipt, key, self.plan)
                    screen.record([revised], receipt, key+'-2', self.plan)
                    self.assertEqual(con.execute('SELECT count(*) AS n FROM astra_modelling.enhancement_screening_events WHERE request_id LIKE %s', (key+'%',)).fetchone()['n'], 2)
                    current.return_value = None
                    with self.assertRaises(ValueError):
                        screen.record([self.entry], receipt, key+'-3', self.plan)
            self.assertEqual(con.execute('SELECT count(*) AS n FROM astra_modelling.enhancement_screening_events WHERE request_id LIKE %s', (key+'%',)).fetchone()['n'], 0)


if __name__ == '__main__':
    unittest.main()
