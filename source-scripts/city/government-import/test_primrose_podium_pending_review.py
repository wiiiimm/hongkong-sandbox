import unittest
from primrose_podium_pending_review import verify


class Connection:
    def __init__(self, current, archived=None):
        self.current, self.archived = current, archived

    def execute(self, sql, params):
        self.value = self.archived if 'snapshot_id=%s' in sql else self.current
        return self

    def fetchone(self):
        return self.value


class PendingReviewTests(unittest.TestCase):
    uid = 'landsd/74573:0'
    sha = 'a' * 64

    def test_exact_empty_pending_preserved(self):
        r = verify(Connection(('s1', 'pending', self.sha, None)), self.uid, self.sha)
        self.assertEqual(r, {'snapshotId': 's1', 'state': 'pending',
                             'sourceSHA256': self.sha, 'result': None})

    def test_review_inherited_into_new_snapshot_keeps_pinned_history(self):
        old = {'snapshotId': 's1', 'state': 'pending',
               'sourceSHA256': self.sha, 'result': None}
        r = verify(Connection(('s2', 'pending', self.sha, None),
                              ('pending', self.sha, None)), self.uid, self.sha, old)
        self.assertEqual(r['snapshotId'], 's2')

    def test_decided_or_held_reviews_rejected(self):
        for state in ['held', 'approved-for-integration', 'installed-verified']:
            with self.subTest(state=state), self.assertRaises(AssertionError):
                verify(Connection(('s1', state, self.sha, None)), self.uid, self.sha)

    def test_pending_with_decision_rejected(self):
        with self.assertRaises(AssertionError):
            verify(Connection(('s1', 'pending', self.sha, {'evidence': 'decision'})),
                   self.uid, self.sha)

    def test_changed_source_rejected(self):
        with self.assertRaises(AssertionError):
            verify(Connection(('s1', 'pending', 'b' * 64, None)), self.uid, self.sha)

    def test_missing_review_rejected(self):
        with self.assertRaises(AssertionError):
            verify(Connection(None), self.uid, self.sha)

    def test_changed_archived_review_rejected(self):
        old = {'snapshotId': 's1', 'state': 'pending',
               'sourceSHA256': self.sha, 'result': None}
        with self.assertRaises(AssertionError):
            verify(Connection(('s2', 'pending', self.sha, None),
                              ('held', self.sha, None)), self.uid, self.sha, old)

    def test_unscoped_source_rejected(self):
        with self.assertRaises(AssertionError):
            verify(Connection(('s1', 'pending', self.sha, None)),
                   'landsd/51764:0', self.sha)


if __name__ == '__main__':
    unittest.main()
