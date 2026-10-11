"""Offline contracts and opt-in isolated Postgres lifecycle tests; no source models processed."""
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
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


class SourceRecordTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name).resolve()
        root_patch = patch.object(r, 'ROOT', self.root)
        root_patch.start()
        self.addCleanup(root_patch.stop)
        self.data = self.root / '3d-viewer/city/data'
        self.data.mkdir(parents=True)
        self.asset = self.data / 'source.glb.gz'
        self.asset.write_bytes(b'synthetic source identity fixture')
        self.entry = {'uid': 'landsd/42:0', 'asset': self.asset.name,
                      'sha256': hashlib.sha256(self.asset.read_bytes()).hexdigest()}
        self.cat = {'schemaVersion': 1, 'kind': 'official-model-catalogue', 'crs': 'EPSG:2326',
                    'verticalDatum': 'Hong Kong Principal Datum',
                    'rootTranslation': [-834500, 0, 816500], 'models': [self.entry]}
        self.catalogue = self.data / 'catalogue.json'
        self.catalogue.write_text(json.dumps(self.cat))
        self.manifest = self.data / 'manifest.json'
        self.manifest.write_text(json.dumps({'officialModelCatalogues': ['city/data/catalogue.json']}))
        self.git('init', '--quiet')
        self.commit()

    def git(self, *args):
        return subprocess.check_output(['git', *args], cwd=self.root, text=True,
                                       env={**os.environ, 'GIT_AUTHOR_NAME': 'Fixture',
                                            'GIT_AUTHOR_EMAIL': 'fixture@example.invalid',
                                            'GIT_COMMITTER_NAME': 'Fixture',
                                            'GIT_COMMITTER_EMAIL': 'fixture@example.invalid'})

    def commit(self):
        self.git('add', '--all', '--', '3d-viewer/city/data')
        self.git('commit', '--quiet', '--allow-empty', '-m', 'test: source fixture')

    def record(self):
        return r.source_record(self.catalogue, self.entry['uid'])

    def test_accepts_both_installed_catalogue_kinds(self):
        for kind in ('official-model-catalogue', 'staged-official-model-catalogue'):
            with self.subTest(kind=kind):
                self.catalogue.write_text(json.dumps({**self.cat, 'kind': kind}))
                self.commit()
                record = self.record()
                self.assertEqual(record['source']['entry'], self.entry)
                self.assertEqual(record['sourceSha256'], self.entry['sha256'])
                self.assertEqual(record['revisionId'], r.digest(record['source']))
                self.assertEqual(record['sourceCommit'], self.git('rev-parse', 'HEAD').strip())
        for changes in ({'kind': 'unknown'}, {'rootTranslation': [-834500, 1, 816500]}):
            self.catalogue.write_text(json.dumps({**self.cat, **changes}))
            self.commit()
            with self.subTest(changes=changes), self.assertRaisesRegex(ValueError, 'fixed 1x'):
                self.record()

    def test_rejects_uninstalled_candidate_and_duplicate_current_uid(self):
        candidate = self.data / 'candidate.json'
        candidate.write_text(json.dumps({**self.cat, 'kind': 'staged-official-model-catalogue'}))
        self.commit()
        with self.assertRaisesRegex(ValueError, 'not installed'):
            r.source_record(candidate, self.entry['uid'])
        self.manifest.write_text(json.dumps({'officialModelCatalogues': [
            'city/data/catalogue.json', 'city/data/candidate.json']}))
        self.commit()
        with self.assertRaisesRegex(ValueError, 'exactly one current'):
            self.record()

    def test_rejects_uncommitted_inputs_but_ignores_unrelated_edits(self):
        original = self.record()
        for path in (self.asset, self.catalogue, self.manifest):
            content = path.read_bytes()
            with self.subTest(path=path.name):
                path.write_bytes(content + b' ')
                with self.assertRaisesRegex(ValueError, 'uncommitted'):
                    self.record()
                self.git('add', str(path.relative_to(self.root)))
                with self.assertRaisesRegex(ValueError, 'uncommitted'):
                    self.record()
                path.write_bytes(content)
                with self.assertRaisesRegex(ValueError, 'staged'):
                    self.record()
                self.git('add', str(path.relative_to(self.root)))
        (self.root / 'unrelated.txt').write_text('another agent is working')
        self.assertEqual(self.record(), original)

    def test_rejects_untracked_or_staged_new_asset(self):
        missing = self.data / 'new.glb.gz'
        self.catalogue.write_text(json.dumps({**self.cat, 'models': [{**self.entry, 'asset': missing.name}]}))
        self.commit()
        missing.write_bytes(self.asset.read_bytes())
        for staged in (False, True):
            with self.subTest(staged=staged):
                if staged:
                    self.git('add', str(missing.relative_to(self.root)))
                with self.assertRaisesRegex(ValueError, 'must be committed'):
                    self.record()


class ContractTests(unittest.TestCase):

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
