"""Unique pinned-Neon fixtures; no source payload downloads or model publication."""
import concurrent.futures
from contextlib import contextmanager
import copy
import importlib.util
import os
from pathlib import Path
import time
import unittest
from unittest.mock import patch
import uuid

# Avoid another component's generic store module in combined test discovery.
spec = importlib.util.spec_from_file_location('native_stage_store', Path(__file__).with_name('store.py'))
store = importlib.util.module_from_spec(spec)
spec.loader.exec_module(store)


def item(sheet='fixture-sheet'):
    return {'sheet': sheet, 'stage': 'prepare', 'sourceSha256': '1'*64,
            'pipelineSha256': '2'*64, 'footprintSha256': '3'*64, 'terrainSha256': None,
            'inputs': {'sourceETag': 'revision-a', 'directorySHA256': '4'*64}}


def result(status='prepared'):
    return {'status': status, 'counts': {'models': 1},
            'artifacts': [{'key': 'astra-modelling/objects/sha256/'+'5'*64,
                           'sha256': '5'*64, 'bytes': 12, 'kind': 'fixture-bundle'}],
            'models': [{'modelId': 'fixture-model', 'state': 'candidate', 'checks': {'source': True}}],
            'qualification': store.QUALIFICATION}


class ValidationTests(unittest.TestCase):
    def test_fingerprints_cover_sources_pipeline_footprints_terrain_and_parameters(self):
        original=item(); key=store.cache_key(original)
        for field in ('sourceSha256','pipelineSha256','footprintSha256','terrainSha256'):
            changed=copy.deepcopy(original); changed[field]='9'*64
            self.assertNotEqual(key,store.cache_key(changed))
        changed=copy.deepcopy(original); changed['inputs']['sourceETag']='revision-b'
        self.assertNotEqual(key,store.cache_key(changed))
        self.assertEqual(key,store.cache_key(dict(reversed(list(original.items())))))

    def test_incomplete_or_batch_dependent_inputs_are_rejected(self):
        for change in ({'pipelineSha256':'short'},{'batch':'label'},{'terrainSha256':9**64}):
            with self.assertRaises(ValueError): store.cache_key({**item(),**change})

    def test_artifact_bindings_and_preparation_scope_are_required(self):
        for key in ('../escape','https://signed.example/token','astra-modelling/../escape'):
            r=result();r['artifacts'][0]['key']=key
            with self.assertRaises(ValueError):store.validate_result(r)
        for field,value in [('sha256','bad'),('bytes',-1),('kind','')]:
            r=result();r['artifacts'][0][field]=value
            with self.assertRaises(ValueError):store.validate_result(r)
        for changes in ({'publicationApproved':True},{'qualification':'approved'},{'artifacts':[]}):
            with self.assertRaises(ValueError):store.validate_result({**result(),**changes})
        self.assertEqual(store.validate_result(result())['status'],'prepared')


@unittest.skipUnless(os.getenv('MODELLING_INTEGRATION_TEST')=='1','Pinned Neon fixtures require opt-in')
class LiveStoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):store.migrate()

    def inputs(self,n):
        prefix='fixture-'+uuid.uuid4().hex
        return[item(prefix+'-'+str(i))for i in range(n)]

    def test_overlapping_runs_share_ownership_and_cross_label_cache(self):
        inputs=self.inputs(2);a=store.register('fixture-one',inputs[:1]);both=store.register('fixture-overlap',inputs)
        first=store.claim(a['runId'],'first');second=store.claim(both['runId'],'second')
        self.assertNotEqual(first['id'],second['id']);self.assertIsNone(store.claim(both['runId'],'third'))
        self.assertTrue(store.heartbeat_many([first,second]))
        store.finish_group([{'job':j,'result':result()}for j in (first,second)])
        replay=store.register('fixture-new-label',list(reversed(inputs)))
        self.assertEqual(replay['runId'],both['runId']);self.assertEqual(replay['cached'],2)
        self.assertEqual(store.report(a['runId'])['cached'],1)
        self.assertEqual(len(store.cached_results(both['runId'])),2)
        changed=copy.deepcopy(inputs);changed[0]['pipelineSha256']='8'*64
        fresh=store.register('fixture-new-pipeline',changed)
        self.assertEqual(fresh['cached'],1);j=store.claim(fresh['runId'],'new');store.finish_group([{'job':j,'result':result('exceptions')}])

    def test_concurrent_claims_are_distinct(self):
        run=store.register('fixture-concurrent',self.inputs(2))
        with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:
            jobs=list(pool.map(lambda i:store.claim(run['runId'],'worker-'+str(i)),range(2)))
        self.assertEqual(len({j['id']for j in jobs}),2)
        store.finish_group([{'job':j,'result':result()}for j in jobs])
        self.assertEqual(store.report(run['runId'])['pending'],0)

    def test_expired_worker_cannot_write_and_can_resume(self):
        run=store.register('fixture-expiry',self.inputs(1));old=store.claim(run['runId'],'same-owner',lease_seconds=1)
        time.sleep(1.1);new=store.claim(run['runId'],'same-owner')
        self.assertNotEqual(old['token'],new['token'])
        with self.assertRaises(ValueError):store.finish_group([{'job':old,'result':result()}])
        self.assertEqual(store.report(run['runId'])['cached'],0)
        store.finish_group([{'job':new,'result':result('source-empty')}])

    def test_final_expiry_rolls_back_all_group_results_after_copy(self):
        run=store.register('fixture-final-clock',self.inputs(2));jobs=[store.claim(run['runId'],'worker-'+str(i))for i in range(2)]
        real_connect=store.connect
        class Connection:
            def __init__(self,con):self.con=con
            def __getattr__(self,name):return getattr(self.con,name)
            def execute(self,sql,params=None):
                returned=self.con.execute(sql,params)
                if sql.startswith('INSERT INTO astra_modelling.native_stage_results SELECT'):
                    self.con.execute("UPDATE astra_modelling.jobs SET lease_until=clock_timestamp()-interval '1 second' WHERE id=%s",(jobs[0]['id'],))
                return returned
        @contextmanager
        def clock_expiry():
            with real_connect()as con:yield Connection(con)
        entries=[{'job':j,'result':result()}for j in jobs]
        with patch.object(store,'connect',clock_expiry):
            with self.assertRaisesRegex(ValueError,'expired during result'):store.finish_group(entries)
        self.assertEqual(store.report(run['runId'])['cached'],0)
        store.finish_group(entries);self.assertEqual(store.report(run['runId'])['cached'],2)

    def test_retryable_failures_do_not_become_immutable_results(self):
        run=store.register('fixture-retry',self.inputs(1));job=store.claim(run['runId'],'owner')
        self.assertTrue(store.fail(job,'network-timeout',retry=True));self.assertEqual(store.report(run['runId'])['cached'],0)
        time.sleep(2.1);again=store.claim(run['runId'],'retry')
        self.assertNotEqual(job['token'],again['token']);store.finish_group([{'job':again,'result':result()}])


if __name__=='__main__':unittest.main()
