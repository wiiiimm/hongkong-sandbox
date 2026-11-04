import unittest
from exact_distinct_evidence_refs_v1_20261014 import distinct_refs,check_distinct_refs
class Tests(unittest.TestCase):
 def setUp(self):self.a=dict(path='saved/original.json.gz',sha256='0'*64);self.b=dict(path='saved/current.json.gz',sha256='1'*64)
 def test_many_ancestors_only_two_distinct_hashes_first_order(self):
  calls=[];out=check_distinct_refs([self.b,self.a]*2362,lambda q:calls.append(q.copy()));self.assertEqual(calls,[self.b,self.a]);self.assertEqual(out,calls)
 def test_conflicting_samepath_different_sha_fails_before_any_check(self):
  calls=[]
  with self.assertRaises(AssertionError):check_distinct_refs([self.a,self.b,{**self.a,'sha256':'2'*64}],calls.append)
  self.assertEqual(calls,[])
 def test_each_phase_rechecks_same_sources_no_mtime_cache(self):
  calls=[]
  for _ in range(3):check_distinct_refs([self.a,self.a,self.b],calls.append)
  self.assertEqual(len(calls),6)
 def test_source_mutation_callback_failure_propagates(self):
  def changed(q):raise AssertionError('actual bytes changed')
  with self.assertRaises(AssertionError):check_distinct_refs([self.a,self.a],changed)
 def test_return_does_not_mutate_input(self):
  out=distinct_refs([self.a]);out[0]['sha256']='3'*64;self.assertEqual(self.a['sha256'],'0'*64)
 def test_bad_path_or_digest_fails_closed(self):
  for ref in [{**self.a,'path':'../escape'},{**self.a,'path':'/absolute'},{**self.a,'sha256':'x'*64}]:
   with self.assertRaises(AssertionError):distinct_refs([ref])
if __name__=='__main__':unittest.main()
