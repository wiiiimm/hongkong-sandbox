"""Actual full Ching Hin acceptance and stale numeric/current-scope counterexamples."""
import importlib.util,json,copy,unittest
from unittest.mock import patch
from pathlib import Path
HERE=Path(__file__).parent
s=importlib.util.spec_from_file_location('ching_fixture',HERE/'xl-terrain-recovery-20261010-ching-hin-current-complete-role-v2.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class ActualSource(unittest.TestCase):
 def test_complete_actual_source(self):
  value=m.recheck();self.assertEqual(json.loads(json.dumps(value)),m.read(m.DOC/'typed-role.json.gz'));self.assertTrue(value['independentPhysicalChecksPassed']);self.assertEqual(value['completeOriginalGradeSupport']['resolvedOriginalComponents'],list(range(963)));self.assertEqual(value['completeOriginalGradeSupport']['ordinaryGroundRootComponents'],[]);self.assertEqual(value['originalWallRole']['creditedWallFaces'],[1161,1518,1998]);self.assertEqual(value['currentNativeNeighboursAccounted'],5)
 def bad_read(self,target,mutate):
  original=m.read
  def changed(path):
   v=original(path)
   if Path(path)==target:v=copy.deepcopy(v);mutate(v)
   return v
  with patch.object(m,'read',side_effect=changed),self.assertRaises(AssertionError):m.recheck()
 def test_actual_rendered_face_proof_omitted(self):
  self.bad_read(m.FINITE/'diagnostic.json.gz',lambda v:v['rows'][0]['allFaces'][0].update(completeActualRenderedBoundProved=False))
 def test_false_exact_source_context_binding(self):
  self.bad_read(m.FINITE/'diagnostic.json.gz',lambda v:v['rows'][0].update(completeGroundSHA256='0'*64))
 def test_missing_current_foreign_actor(self):
  self.bad_read(m.PHYSICAL/'neighbour-inputs.json.gz',lambda v:v['rows'].pop())
 def test_context_changed_without_binding_change(self):
  self.bad_read(m.CONTEXT/'diagnostic.json.gz',lambda v:v['completeCertifiedLowerBoundContexts'][0]['minimum'].update(minimumGapM=999))
if __name__=='__main__':unittest.main()
