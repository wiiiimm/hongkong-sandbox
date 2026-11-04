"""Pure current-surviving actor fixtures; does not import project/geometry/DB."""
import ast,unittest
from pathlib import Path
P=Path(__file__).with_name('citywalk134332_surviving_native_finite_interface_draft_v1_20261013.py')
fn=next(n for n in ast.parse(P.read_text()).body if isinstance(n,ast.FunctionDef)and n.name=='current_actor_partition')
ns={'UID':'landsd/134332:0','ACTORS':['landsd/175935:0','landsd/273839:0','landsd/305615:0']};exec(compile(ast.Module(body=[fn],type_ignores=[]),str(P),'exec'),ns)
class Scope(unittest.TestCase):
 def rows(self):return [dict(uid=u,sha256='fixture-source',suppressesBuildingUids=[])for u in ns['ACTORS']]
 def test_all_three_survive(self):self.assertEqual(set(ns['current_actor_partition'](self.rows())[0]),set(ns['ACTORS']))
 def test_missing_native(self):
  with self.assertRaises(AssertionError):ns['current_actor_partition'](self.rows()[:-1])
 def test_duplicate_uid(self):
  r=self.rows()
  with self.assertRaises(AssertionError):ns['current_actor_partition'](r+[r[0]])
 def test_owned_already_installed(self):
  with self.assertRaises(AssertionError):ns['current_actor_partition'](self.rows()+[dict(uid=ns['UID'])])
 def test_native_suppressed_by_other_actor(self):
  with self.assertRaises(AssertionError):ns['current_actor_partition'](self.rows()+[dict(uid='landsd/999999:0',suppressesBuildingUids=[ns['ACTORS'][1]])])
 def test_owned_suppressed_by_current_native(self):
  r=self.rows();r[0]['suppressesBuildingUids']=[ns['UID']]
  with self.assertRaises(AssertionError):ns['current_actor_partition'](r)
 def test_unrelated_suppression_retained(self):
  r=self.rows();r[0]['suppressesBuildingUids']=['landsd/999998:0'];lookup,_=ns['current_actor_partition'](r);self.assertEqual(lookup[ns['ACTORS'][0]]['suppressesBuildingUids'],['landsd/999998:0'])
if __name__=='__main__':unittest.main()
