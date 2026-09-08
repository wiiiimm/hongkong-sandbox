"""Real pinned-Neon isolated fixtures; never modify source/model-review tables."""
import hashlib,json,os,time,unittest,uuid,concurrent.futures
import store
from contextlib import contextmanager
from unittest.mock import patch

def row(uid,salt='a'):
 r={'uid':uid,'sourceSha':salt,'modelSha':'model','pipelineSha':'pipeline','terrainSha':'terrain'};r['cacheKey']=hashlib.sha256(store.encode([uid,salt,'model','pipeline','terrain']).encode()).hexdigest();r['result']={'flags':[],'detail':'basic','terrain':{'state':'sampled-source-footprint-envelope'}};return r

def meta(rows):
 sha=hashlib.sha256(store.encode(rows).encode()).hexdigest();return{'runId':'test-'+sha,'planSha':sha,'pipelineSha':'fixture','buildings':len(rows),'tiles':1}

@unittest.skipUnless(os.getenv('MODELLING_INTEGRATION_TEST')=='1','Pinned Neon fixtures require explicit opt-in')
class StoreTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):store.migrate()
 def fixtures(self,n=4):return[row('audit-test/'+uuid.uuid4().hex)for _ in range(n)]
 def test_atomic_partial_rejection_and_reuse_across_labels(self):
  rows=self.fixtures(2);m=meta(rows);reg=store.register(m,rows,'fixture-first',2);j=store.claim(reg['batch'],'fixture',[store.STAGE]);self.assertIsNotNone(j)
  with self.assertRaises(ValueError):store.finish_chunk(j,rows[:1])
  self.assertEqual(store.report(m['runId'])['cached'],0)
  self.assertEqual(store.finish_chunk(j,rows),2)
  again=store.register(m,rows,'different-session-batch',2);self.assertEqual(len(again['cached']),2);self.assertEqual(again['chunks'],[])
 def test_restart_expiry_and_stale_owner_cannot_insert_cache(self):
  rows=self.fixtures(2);m=meta(rows);reg=store.register(m,rows,'fixture-expiry',2);old=store.claim(reg['batch'],'same-owner',[store.STAGE],lease_seconds=1);time.sleep(1.1);new=store.claim(reg['batch'],'same-owner',[store.STAGE]);self.assertNotEqual(old['token'],new['token'])
  with self.assertRaises(ValueError):store.finish_chunk(old,rows)
  self.assertEqual(store.report(m['runId'])['cached'],0);store.finish_chunk(new,rows);self.assertEqual(store.report(m['runId'])['missing'],0)
 def test_concurrent_chunks_and_selective_invalidation(self):
  rows=self.fixtures();m=meta(rows);reg=store.register(m,rows,'fixture-parallel',2)
  with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:jobs=list(pool.map(lambda n:store.claim(reg['batch'],'owner'+str(n),[store.STAGE]),range(2)))
  self.assertEqual(len({j['id']for j in jobs}),2);chunks={ch:{u for u,_,c,_ in reg['members']if c==ch}for ch in reg['chunks']}
  for j in jobs:store.finish_chunk(j,[r for r in rows if r['uid']in chunks[j['payload']['chunk']]])
  changed=[row(rows[0]['uid'],'changed-source')]+rows[1:];reg2=store.register(meta(changed),changed,'fixture-new-input',2);self.assertEqual(len(reg2['cached']),3);self.assertEqual(len(reg2['chunks']),1)
  j=store.claim(reg2['batch'],'new-owner',[store.STAGE]);store.finish_chunk(j,changed[:1]);self.assertEqual(store.report(meta(changed)['runId'])['missing'],0)
 def test_group_final_fence_rolls_back_all_after_copy(self):
  rows=self.fixtures(2);m=meta(rows);reg=store.register(m,rows,'fixture-group-final-fence',1);jobs=[store.claim(reg['batch'],'owner'+str(i),[store.STAGE])for i in range(2)];real_connect=store.connect
  class Connection:
   def __init__(self,con):self.con=con
   def __getattr__(self,name):return getattr(self.con,name)
   def execute(self,sql,params=None):
    result=self.con.execute(sql,params)
    if sql.startswith('INSERT INTO astra_modelling.city_audit_cache SELECT'):
     self.con.execute("UPDATE astra_modelling.jobs SET lease_until=clock_timestamp()-interval '1 second' WHERE id=%s",(jobs[0]['id'],))
    return result
  @contextmanager
  def injected_clock_expiry():
   with real_connect()as con:yield Connection(con)
  with patch.object(store,'connect',injected_clock_expiry):
   with self.assertRaisesRegex(ValueError,'expired during COPY'):store.finish_group(jobs,rows)
  self.assertEqual(store.report(m['runId'])['cached'],0)
  # The failed transaction also rolls back its fixture clock edit and other chunk completion.
  store.finish_group(jobs,rows);self.assertEqual(store.report(m['runId'])['missing'],0)
 def test_fingerprint_mismatch_rejects_whole_chunk(self):
  rows=self.fixtures(1);m=meta(rows);reg=store.register(m,rows,'fixture-corruption',1);j=store.claim(reg['batch'],'owner',[store.STAGE]);bad={**rows[0],'terrainSha':'wrong'}
  with self.assertRaises(ValueError):store.finish_chunk(j,[bad])
  self.assertEqual(store.report(m['runId'])['cached'],0);store.finish_chunk(j,rows)
if __name__=='__main__':unittest.main()
