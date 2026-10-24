"""Live isolated-branch tests; opt in with MODELLING_INTEGRATION_TEST=1."""
import concurrent.futures
import os
import time
import unittest
import uuid
from unittest.mock import patch
from db import CONFIG, connection_parameters, migrate, connect
import jobs


class RoutingTests(unittest.TestCase):
    def test_refuses_production_or_missing(self):
        for url in (None, 'postgresql://u:p@production.example/neondb',
                    'postgresql://u:p@'+CONFIG['host']+'/wrong',
                    'postgresql://u:p@'+CONFIG['host']+'/neondb?hostaddr=127.0.0.1'):
            with self.assertRaises(ValueError): connection_parameters(url)

    def test_refuses_environment_routing(self):
        for key in ('PGHOSTADDR', 'PGSERVICE', 'PGSERVICEFILE', 'PGOPTIONS'):
            with patch.dict(os.environ,{key:'override'}):
                with self.assertRaises(ValueError):
                    connection_parameters('postgresql://u:p@'+CONFIG['host']+'/neondb')

    def test_requires_verified_tls(self):
        p=connection_parameters('postgresql://u:p@'+CONFIG['host']+'/neondb?sslmode=disable')
        self.assertEqual(p['sslmode'],'verify-full')
        self.assertTrue(p['sslrootcert'].endswith('cacert.pem'))


@unittest.skipUnless(os.getenv('MODELLING_INTEGRATION_TEST')=='1','Live tests require opt-in')
class QueueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): migrate()

    def setUp(self): self.batch='verification-'+uuid.uuid4().hex

    def test_parallel_claim_idempotence_and_completion(self):
        ids=[jobs.enqueue(self.batch,'test',{'i':i}) for i in range(16)]
        self.assertEqual(jobs.enqueue(self.batch,'test',{'i':0}),ids[0])
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            results=list(pool.map(lambda i: jobs.claim(self.batch,'worker-'+str(i),['test']),range(16)))
        self.assertEqual(len({j['id'] for j in results}),16)
        self.assertFalse(jobs.claim(self.batch,'extra',['test']))
        for job in results:
            self.assertTrue(jobs.finish(job,result={'checked':True}))
            self.assertFalse(jobs.finish(job,result={'overwrite':True}))
        self.assertEqual(jobs.report(self.batch)['status'],{'complete':16})

    def test_expiry_reclaim_fences_old_worker(self):
        jobs.enqueue(self.batch,'test',{'expiry':True})
        old=jobs.claim(self.batch,'same-owner',['test'],lease_seconds=1)
        time.sleep(1.1)
        self.assertFalse(jobs.heartbeat(old))
        self.assertFalse(jobs.finish(old,result='late'))
        new=jobs.claim(self.batch,'same-owner',['test'])
        self.assertEqual(old['id'],new['id'])
        self.assertNotEqual(old['token'],new['token'])
        self.assertFalse(jobs.finish(old,result='stale'))
        self.assertTrue(jobs.heartbeat(new))
        self.assertTrue(jobs.finish(new,result='current'))

    def test_capabilities_and_terminal_expiry(self):
        identity=jobs.enqueue(self.batch,'future-model-adapter',{})
        self.assertFalse(jobs.claim(self.batch,'worker',['test']))
        with connect() as c:
            c.execute('UPDATE astra_modelling.jobs SET max_attempts=1 WHERE id=%s',(identity,))
        j=jobs.claim(self.batch,'crashed',['future-model-adapter'],lease_seconds=1)
        time.sleep(1.1)
        self.assertFalse(jobs.claim(self.batch,'new',['future-model-adapter']))
        self.assertEqual(jobs.report(self.batch)['status'],{'failed':1})

    def test_error_is_terminal_and_batch_isolation(self):
        jobs.enqueue(self.batch,'test',{})
        self.assertFalse(jobs.claim(self.batch+'-other','worker',['test']))
        j=jobs.claim(self.batch,'worker',['test'])
        self.assertTrue(jobs.finish(j,error='test failure'))
        self.assertEqual(jobs.report(self.batch)['status'],{'failed':1})


if __name__=='__main__': unittest.main()
