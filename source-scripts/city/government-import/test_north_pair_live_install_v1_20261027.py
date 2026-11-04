import ast,copy,tempfile,unittest
from pathlib import Path
import north_pair_live_install_v1_20261027 as install
class LiveGuards(unittest.TestCase):
 def test_rollback_keeps_canonical_implementation(self):
  def function(path,name):return next(n for n in ast.parse(path.read_text()).body if isinstance(n,ast.FunctionDef)and n.name==name)
  old=function(Path(install.HERE/'ocean_coordinated_live_install_v1_20261027.py'),'restore');new=function(Path(install.__file__),'restore')
  self.assertEqual(ast.dump(old,include_attributes=False),ast.dump(new,include_attributes=False))
 def test_rollback_restores_and_removes(self):
  with tempfile.TemporaryDirectory()as t:
   old=install.ROOT;install.ROOT=Path(t)
   try:
    (install.ROOT/'old').write_bytes(b'changed');(install.ROOT/'new').write_bytes(b'new')
    self.assertEqual(install.restore({'old':b'original','new':None}),[])
    self.assertEqual((install.ROOT/'old').read_bytes(),b'original');self.assertFalse((install.ROOT/'new').exists())
   finally:install.ROOT=old
 def report(self):
  models=[dict(uid=str(i),sha256=str(i))for i in range(3)]
  report=dict(passed=True,pageErrors=[],cases=[dict(failedUid=f,width=390 if f is not None else 1280,baseOnlyRestoredCompleteGroup=True,completeGroupEvicted=True,audit=dict(violations=[]),sources=models,failureKeptAllBasics=f is not None)for f in [None,'0','1','2']])
  return report,models
 def test_all_actual_peer_cases(self):self.assertTrue(install.verify_atomic(*self.report()))
 def test_missing_peer_failure_rejected(self):
  r,m=self.report();r['cases'].pop()
  with self.assertRaises(AssertionError):install.verify_atomic(r,m)
 def test_partial_activation_rejected(self):
  r,m=self.report();r['cases'][1]['audit']['violations']=['partial']
  with self.assertRaises(AssertionError):install.verify_atomic(r,m)
 def test_wrong_source_rejected(self):
  r,m=self.report();r=copy.deepcopy(r);r['cases'][0]['sources'][0]['sha256']='changed'
  with self.assertRaises(AssertionError):install.verify_atomic(r,m)
 def test_basic_failure_rejected(self):
  r,m=self.report();r['cases'][1]['failureKeptAllBasics']=False
  with self.assertRaises(AssertionError):install.verify_atomic(r,m)
if __name__=='__main__':unittest.main()
