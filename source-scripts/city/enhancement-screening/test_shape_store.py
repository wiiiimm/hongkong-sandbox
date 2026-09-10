import copy
import gzip
import json
from pathlib import Path
import tempfile
import unittest
from shape_store import package, verify, encode, sha
from shape_batch import batches


class ShapeStoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name)/'inputs.json.gz'
        self.e = {'sampleUids': ['a', 'b'], 'controlUids': ['c'], 'rows': {
            uid: {'inputHash': uid*64, 'state': 'enhanced' if uid == 'c' else 'unassessed'}
            for uid in ('a', 'b', 'c')}, 'sourceCommit': 'commit', 'manifestDigest': 'manifest',
            'nativeRun': 'native', 'contextHash': 'context', 'seed': 'seed', 'population': 9}
        self.results = [dict(uid=uid, **row, action='skip' if uid == 'c' else 'retain-pending',
            comparison=None, reasons=['unavailable'], metrics=None) for uid, row in self.e['rows'].items()]
        self.summary = dict(version='test', mode='bounded-validation-dry-run', sampleSize=2,
            controlCount=1, counts={'retain-pending': 2}, comparisons={'unavailable': 2},
            reasonCounts={'unavailable': 2}, aiCalls=0, modelReviewWrites=0, screeningAcceptanceWrites=0,
            publishedModels=0, sourceCommit='commit', manifestDigest='manifest', engineSHA256='e'*64,
            policy={}, routingSHA256='r'*64)
        self.freeze()

    def freeze(self):
        self.path.write_bytes(gzip.compress(encode(self.e), mtime=0))
        self.summary['evidenceSHA256'] = sha(self.path.read_bytes())

    def packed(self):
        return package(self.path, self.summary, self.results)

    @staticmethod
    def database_rows(rows):
        return [(r['uid'], r['role'], r['result']['action'], r['result']['inputHash'],
                 r['sha256'], copy.deepcopy(r['result'])) for r in rows]

    def test_complete_membership_includes_missing_geometry_and_control(self):
        _, manifest, rows = self.packed()
        self.assertEqual([r['role'] for r in rows], ['sample', 'sample', 'control'])
        self.assertEqual(len(rows), 3)
        self.assertFalse(manifest['authoritative'])
        verify(manifest, self.database_rows(rows), manifest, rows)

    def test_jsonb_numeric_normalisation_does_not_change_hash(self):
        self.assertEqual(sha(encode({'v': [-0.0, 1.0, 1e20, 1e-20]})),
                         sha(encode({'v': [0, 1, 100000000000000000000, .00000000000000000001]})))

    def test_retry_ignores_execution_time_and_cache_hits_and_row_order(self):
        first = self.packed()
        self.summary.update(seconds=99, cache={'shared': 3})
        self.results.reverse()
        self.assertEqual(first, self.packed())

    def test_changed_routing_or_pending_outcome_creates_new_run(self):
        first = self.packed()[0]
        self.summary['routingSHA256'] = 's'*64
        self.assertNotEqual(first, self.packed()[0])
        second = self.packed()[0]
        self.results[0]['geometryError'] = 'exact asset unavailable'
        self.assertNotEqual(second, self.packed()[0])

    def test_missing_duplicate_or_mismatched_input_rejected(self):
        for change in ('missing', 'duplicate', 'input'):
            with self.subTest(change=change):
                rows = copy.deepcopy(self.results)
                if change == 'missing': rows.pop()
                elif change == 'duplicate': rows[1] = rows[0]
                else: rows[0]['inputHash'] = 'stale'
                with self.assertRaises(ValueError): package(self.path, self.summary, rows)

    def test_controls_cannot_inflate_sample(self):
        self.e['sampleUids'].append('c'); self.freeze()
        with self.assertRaises(ValueError): self.packed()

    def test_unaccepted_skip_or_incomplete_summary_rejected(self):
        self.results[0]['action'] = 'skip'
        with self.assertRaises(ValueError): self.packed()
        self.results[0]['action'] = 'retain-pending'; self.summary['counts'] = {'retain-pending': 1}
        with self.assertRaises(ValueError): self.packed()

    def test_stored_content_and_missing_rows_checked(self):
        _, manifest, rows = self.packed(); stored = self.database_rows(rows)
        with self.assertRaises(ValueError): verify(manifest, stored[:-1], manifest, rows)
        stored[0][-1]['reasons'] = ['tampered']
        with self.assertRaises(ValueError): verify(manifest, stored, manifest, rows)

    def test_bounded_batches_account_for_ambiguous_and_missing_sources(self):
        e = {'rows': {str(i): {} for i in range(2005)}, 'native': [
            {'sheet': str(i//10), 'model': {'asset': {'sha256': str(i)},
              'matching': {'viewerMatches': [{'uid': str(i)}]}}} for i in range(2003)]}
        e['native'].append(copy.deepcopy(e['native'][-1]))
        groups, errors = batches(e)
        self.assertEqual(list(map(len, groups)), [1000, 1000, 2])
        ids = [uid for group in groups for uid in group]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(set(ids) | set(errors), set(e['rows']))
        self.assertEqual(errors['2002'], 'native-source-ambiguous')
        self.assertEqual(errors['2003'], 'native-source-unavailable')
        with self.assertRaises(ValueError): batches(e, 1001)


if __name__ == '__main__': unittest.main()
