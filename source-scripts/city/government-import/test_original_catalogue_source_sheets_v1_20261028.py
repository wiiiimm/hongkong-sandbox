import copy
import unittest
from original_catalogue_source_sheets_v1_20261028 import source_sheet_bindings


class DB:
    def __init__(self, records):
        self.records = records

    def execute(self, query, params):
        assert query.startswith('SELECT ')
        self.params = params
        return self

    def fetchall(self):
        return self.records


def row(uid):
    entry = dict(uid=uid, modelId='B'+uid, sha256='a'*64)
    return dict(uid=uid, modelId=entry['modelId'], sourceSHA256=entry['sha256'],
        candidate=dict(entry=entry), native=dict(cacheKey='shared-cache', resultSha='b'*64,
        model=dict(candidate=copy.deepcopy(entry), modelId=entry['modelId'], asset=dict(sha256=entry['sha256']))))


class SourceSheetBinding(unittest.TestCase):
    def setUp(self):
        self.db = DB([('shared-cache', '11-SW-7B', 'b'*64)])
        self.rows = [row('landsd/1:0'), row('landsd/2:0')]

    def test_shared_cache_key_and_missing_field_without_mutation(self):
        original = copy.deepcopy(self.rows)
        out = source_sheet_bindings(self.db, self.rows)
        self.assertEqual({r['sourceTile'] for r in out.values()}, {'11-SW-7B'})
        self.assertEqual(self.db.params, (['shared-cache'],))
        self.assertEqual(self.rows, original)

    def test_conflicting_existing_sheet(self):
        self.rows[0]['candidate']['entry']['sourceTile'] = 'wrong'
        with self.assertRaises(AssertionError):
            source_sheet_bindings(self.db, self.rows)

    def test_changed_stage_result(self):
        self.rows[0]['native']['resultSha'] = 'c'*64
        with self.assertRaises(AssertionError):
            source_sheet_bindings(self.db, self.rows)

    def test_asset_or_model_substitution(self):
        for field in ['asset', 'modelId']:
            rows = copy.deepcopy(self.rows)
            if field == 'asset':
                rows[0]['native']['model']['asset']['sha256'] = 'd'*64
            else:
                rows[0]['native']['model']['modelId'] = 'other-model'
            with self.assertRaises(AssertionError):
                source_sheet_bindings(self.db, rows)

    def test_missing_record_or_duplicate_uid(self):
        with self.assertRaises(AssertionError):
            source_sheet_bindings(DB([]), self.rows)
        with self.assertRaises(AssertionError):
            source_sheet_bindings(self.db, [self.rows[0], self.rows[0]])


if __name__ == '__main__':
    unittest.main()
