"""Offline contracts and opt-in isolated Postgres lifecycle tests; no source models processed."""
import copy
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import uuid

import registry as r


def recipe(status='draft'):
    return {'schemaVersion': 1, 'tier': 'original', 'status': status, 'lossy': False,
            'tools': {'test-tool': '1.0.0'}, 'parameters': {'transport': 'gzip'},
            'acceptance': {'exact': True}}


def source():
    value = {'entry': {'uid': 'landsd/' + str(uuid.uuid4().int) + ':0', 'sha256': 'a' * 64},
             'rootTranslation': [-834500, 0, 816500]}
    return {'revisionId': r.digest(value), 'source': value, 'uid': value['entry']['uid'],
            'sourceSha256': 'a' * 64, 'sourceCommit': 'fixture-not-a-real-source'}


def result(variant):
    return {**variant, 'artifact': {'path': 'fixture/immutable.glb.gz', 'sha256': 'b' * 64},
            'metrics': {'triangles': 1}}


def evidence(variant):
    return {**variant, 'artifactSha256': 'b' * 64, 'report': 'fixture/report.json',
            'reportSha256': 'c' * 64, 'observation': 'Synthetic database fixture only',
            'gates': {gate: 'passed' for gate in r.GATES}}


class ContractTests(unittest.TestCase):
    def test_source_record_accepts_both_viewer_catalogue_kinds(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            asset = root / 'source.glb.gz'
            asset.write_bytes(b'synthetic source identity fixture')
            entry = {'uid': 'landsd/42:0', 'asset': asset.name,
                     'sha256': hashlib.sha256(asset.read_bytes()).hexdigest()}
            cat = {'schemaVersion': 1, 'crs': 'EPSG:2326',
                   'verticalDatum': 'Hong Kong Principal Datum',
                   'rootTranslation': [-834500, 0, 816500], 'models': [entry]}
            path = root / 'catalogue.json'
            with patch.object(r, 'ROOT', root), patch.object(r.subprocess, 'check_output', return_value='fixture-source-commit\n'):
                for kind in ('official-model-catalogue', 'staged-official-model-catalogue'):
                    with self.subTest(kind=kind):
                        cat['kind'] = kind
                        path.write_text(json.dumps(cat))
                        record = r.source_record(path, entry['uid'])
                        self.assertEqual(record['source']['entry'], entry)
                        self.assertEqual(record['sourceSha256'], entry['sha256'])
                        self.assertEqual(record['revisionId'], r.digest(record['source']))
                for changes in ({'kind': 'unknown'}, {'rootTranslation': [-834500, 1, 816500]}):
                    path.write_text(json.dumps({**cat, **changes}))
                    with self.subTest(changes=changes), self.assertRaisesRegex(ValueError, 'fixed 1x'):
                        r.source_record(path, entry['uid'])

    def test_recipe_flags_versions_and_original_precision(self):
        self.assertEqual(r.validate_recipe(recipe()), recipe())
        for update in [{'tier': 'base'}, {'lossy': True}, {'status': 'unknown'},
                       {'status': 'ready', 'tools': {'meshopt': '^0.24.0'}},
                       {'status': 'ready', 'acceptance': {}}]:
            with self.subTest(update=update), self.assertRaises(ValueError):
                r.validate_recipe({**recipe(), **update})

    def test_source_pose_and_recipe_change_identity(self):
        original = source()
        other = copy.deepcopy(original['source'])
        other['rootTranslation'][1] = 1
        self.assertNotEqual(r.digest(other), original['revisionId'])
        self.assertNotEqual(r.digest(recipe()), r.digest(recipe('ready')))
        self.assertEqual(r.digest({'a': 1, 'b': 2}), r.digest({'b': 2, 'a': 1}))
        with self.assertRaises(ValueError):
            r.plan({**original, 'revisionId': 'd' * 64}, recipe(), 'fixture')

    def test_completed_result_must_bind_every_identity_and_output(self):
        variant = {'variantId': 'a' * 64, 'revisionId': 'b' * 64, 'recipeSha256': 'c' * 64}
        row = {'processing_status': 'complete', 'variant_id': variant['variantId'],
               'revision_id': variant['revisionId'], 'recipe_sha256': variant['recipeSha256'],
               'result': result(variant)}
        self.assertEqual(r.validate_result(row, evidence(variant)), 'b' * 64)
        for field in ('variantId', 'revisionId', 'recipeSha256', 'artifactSha256'):
            with self.subTest(field=field), self.assertRaises(ValueError):
                r.validate_result(row, {**evidence(variant), field: 'd' * 64})
        with self.assertRaises(ValueError):
            r.validate_result({**row, 'processing_status': 'pending'}, evidence(variant))


@unittest.skipUnless(os.getenv('OPTIMISATION_TEST_DATABASE_URL'), 'Local Postgres integration opt-in')
class DatabaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import psycopg
        from psycopg.conninfo import conninfo_to_dict
        url = os.environ['OPTIMISATION_TEST_DATABASE_URL']
        params = conninfo_to_dict(url)
        if params.get('host') not in ('localhost', '127.0.0.1') or not params.get('dbname', '').startswith('astra_optimisation_test_'):
            raise ValueError('Integration tests require an isolated named localhost database')
        if params.get('hostaddr') or params.get('service') or params.get('options'):
            raise ValueError('No alternative routing for test databases')
        cls.connection_patch = patch.object(r, 'connect', lambda: psycopg.connect(url))
        cls.connection_patch.start()
        cls.addClassCleanup(cls.connection_patch.stop)
        with r.connect() as con:
            con.execute((r.HERE.parent / 'shared-modelling/schema.sql').read_text())
        r.migrate()
        r.migrate()

    def test_plan_does_not_queue_and_drafts_cannot_run(self):
        src = source()
        first = r.plan(src, recipe(), 'fixture')
        self.assertEqual(first, r.plan(src, recipe(), 'another-session'))
        report = r.report(src['uid'])['variants']
        self.assertEqual(len(report), 1)
        self.assertEqual(report[0]['processing_status'], 'planned')
        self.assertIsNone(report[0]['job_id'])
        with self.assertRaisesRegex(ValueError, 'Draft'):
            r.queue(first['variantId'], 'test')
        with self.assertRaisesRegex(ValueError, 'complete'):
            r.review(first['variantId'], 'approved', 'fixture', evidence(first))

    def test_queue_is_cross_batch_idempotent_and_unsupported_by_current_workers(self):
        src = source()
        first = r.plan(src, recipe('ready'), 'fixture')
        job = r.queue(first['variantId'], 'batch-one-' + uuid.uuid4().hex)
        other = r.queue(first['variantId'], 'batch-two')
        self.assertEqual(job['jobId'], other['jobId'])
        with r.connect() as con:
            row = con.execute('SELECT stage,status,attempts FROM astra_modelling.jobs WHERE id=%s', (job['jobId'],)).fetchone()
        self.assertEqual(row, (r.STAGE, 'pending', 0))

    def test_reviews_preserve_history_and_reject_partial_approval(self):
        src = source()
        first = r.plan(src, recipe('ready'), 'fixture')
        job = r.queue(first['variantId'], 'batch-' + uuid.uuid4().hex)
        with r.connect() as con:
            con.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s WHERE id=%s",
                        (r.Jsonb(result(first)), job['jobId']))
        missing = evidence(first)
        del missing['gates']['visual']
        with self.assertRaisesRegex(ValueError, 'gates'):
            r.review(first['variantId'], 'approved', 'fixture', missing)
        a = r.review(first['variantId'], 'approved', 'fixture', evidence(first))
        b = r.review(first['variantId'], 'rejected', 'fixture', missing)
        self.assertGreater(b['reviewId'], a['reviewId'])
        self.assertEqual(r.report(src['uid'])['variants'][0]['validation_status'], 'rejected')
        self.assertFalse(a['published'])

    def test_new_recipe_and_source_have_no_inherited_status(self):
        src = source()
        a = r.plan(src, recipe(), 'fixture')
        b = r.plan(src, recipe('ready'), 'fixture')
        altered = copy.deepcopy(src)
        altered['source']['entry']['sha256'] = 'e' * 64
        altered['sourceSha256'] = 'e' * 64
        altered['revisionId'] = r.digest(altered['source'])
        c = r.plan(altered, recipe(), 'fixture')
        self.assertEqual(len({a['variantId'], b['variantId'], c['variantId']}), 3)
        self.assertTrue(all(row['validation_status'] == 'unreviewed' for row in r.report(src['uid'])['variants']))


if __name__ == '__main__':
    unittest.main()
