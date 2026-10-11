"""Checks for source cohort selection and borrowed transaction fencing."""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import batch
from db import transaction, CONFIG
from types import SimpleNamespace


class BatchTests(unittest.TestCase):
    def test_worker_partitions_cover_each_source_once(self):
        sources=list(range(4272))
        groups=[group for shard in range(16) for group in batch.source_groups(sources,shard,16)]
        self.assertEqual(sorted(item for group in groups for item in group),sources)
        self.assertTrue(all(len(group)<=100 for group in groups))
        with self.assertRaises(ValueError): batch.source_groups(sources,16,16)

    def test_explicit_negative_acceptance_wins(self):
        self.assertFalse(batch.accepted({}))
        self.assertFalse(batch.accepted({'placementScreening': 'historical', 'placementReviewed': False}))
        self.assertTrue(batch.accepted({'placementReviewed': True}))
        self.assertTrue(batch.accepted({'publicationApproved': True}))
        self.assertFalse(batch.accepted({'placementReviewed': True, 'publicationApproved': False}))
        self.assertFalse(batch.accepted({'publicationApproved': True, 'identityReviewApproved': False}))

    def test_snapshot_is_committed_and_source_revision_matches_registry(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = root/'3d-viewer/city/data/official-models/example'
            folder.mkdir(parents=True)
            asset = folder/'model.glb.gz'; asset.write_bytes(b'fixture asset bytes')
            entry = {'uid': 'landsd/123:0', 'asset': asset.name,
                'sha256': hashlib.sha256(asset.read_bytes()).hexdigest(), 'placementReviewed': True}
            catalogue = {'schemaVersion': 1, 'kind': 'official-model-catalogue',
                'crs': 'EPSG:2326', 'verticalDatum': 'Hong Kong Principal Datum',
                'rootTranslation': [-834500,0,816500], 'models': [entry]}
            path = folder/'catalogue.json'; path.write_text(json.dumps(catalogue))
            manifest = root/'3d-viewer/city/data/manifest.json'
            manifest.write_text(json.dumps({'officialModelCatalogues': ['city/data/official-models/example/catalogue.json']}))
            def git(*args):
                return subprocess.check_output(['git',*args], cwd=root, stderr=subprocess.DEVNULL)
            git('init'); git('add','.'); git('-c','user.name=Test','-c','user.email=test@example.com','commit','-m','fixture')
            with patch.object(batch, 'ROOT', root):
                snap = batch.snapshot()
                self.assertEqual(len(snap['selected']),1)
                self.assertEqual(batch.registry.digest(snap['selected'][0]['source']),snap['selected'][0]['revisionId'])
                asset.write_bytes(b'changed')
                with self.assertRaisesRegex(ValueError,'unchanged committed'):
                    batch.snapshot()
                asset.write_bytes(b'fixture asset bytes')
                catalogue['models'].append(entry);path.write_text(json.dumps(catalogue));git('add','.');git('-c','user.name=Test','-c','user.email=test@example.com','commit','-m','ambiguous')
                with self.assertRaisesRegex(ValueError,'Ambiguous'):
                    batch.snapshot()

    def test_borrowed_connection_transaction_never_closes_connection(self):
        events=[]
        class Scope:
            def __enter__(self): events.append('begin')
            def __exit__(self,kind,value,tb): events.append('rollback' if kind else 'commit')
        class Connection:
            info=SimpleNamespace(host=CONFIG['host'],dbname=CONFIG['database'])
            def transaction(self): return Scope()
        connection=Connection()
        with transaction(connection) as con:
            self.assertIs(connection,con)
        with self.assertRaises(ValueError):
            with transaction(connection): raise ValueError('fenced failure')
        self.assertEqual(events,['begin','commit','begin','rollback'])
        connection.info=SimpleNamespace(host='application.example.com',dbname='app')
        with self.assertRaisesRegex(ValueError,'pinned modelling'):
            with transaction(connection): self.fail('must not begin a transaction')


if __name__ == '__main__': unittest.main()
