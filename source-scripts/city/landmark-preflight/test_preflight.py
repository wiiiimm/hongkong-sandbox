import importlib.util,pathlib,tempfile,unittest
spec=importlib.util.spec_from_file_location('preflight',pathlib.Path(__file__).with_name('preflight.py'));p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
class PreflightTests(unittest.TestCase):
 def test_known_hold_is_not_overruled_by_clean_cpu(self):
  tags,_=p.classify({'state':'candidate-staged','knownHold':{'reason':'Unsupported native roof'}},{'outcome':'runtime-accepted-placement-unreviewed','concerns':[]})
  self.assertIn('known-placement-or-source-hold',tags);self.assertNotIn('cpu-clear-awaiting-visual-review',tags)
 def test_runtime_failure_remains_exception(self):
  tags,_=p.classify({'state':'candidate-staged'},{'outcome':'validation-exception','error':'Source surface collision missed'})
  self.assertIn('runtime-validation-exception',tags);self.assertNotIn('cpu-clear-awaiting-visual-review',tags)
 def test_source_absence_is_not_identity_mismatch_or_pending(self):
  part={'state':'not-in-retained-staged-models'}
  absent,_=p.classify(part,None,None,'exact-source-absent-in-checked-sheets');pending,_=p.classify(part,None,None,'acquisition-pending');mismatch,_=p.classify(part,None,{'reason':'Exact ref failed CSUID'})
  self.assertEqual(absent,['exact-source-absent-in-checked-sheets']);self.assertEqual(pending,['acquisition-pending']);self.assertEqual(mismatch,['exact-reference-identity-or-footprint-mismatch'])
 def test_native_bounds_are_hints_not_support_proof(self):
  target={'uid':'tower','modelId':'t','worldBounds':[[0,20,0],[10,90,10]]};support={'uid':'podium','modelId':'p','worldBounds':[[-2,0,-2],[12,20,12]]};distant={'uid':'far','modelId':'f','worldBounds':[[100,0,100],[120,20,120]]}
  hints=p.support_hints(target,[target,support,distant]);self.assertEqual(len(hints),1);self.assertEqual(hints[0]['uid'],'podium');self.assertFalse(hints[0]['supportVerified'])
 def test_duplicate_part_cannot_silently_replace_record(self):
  with self.assertRaisesRegex(AssertionError,'Duplicate'):p.unique([{'uid':'a'},{'uid':'a'}])
 def test_snapshot_tamper_stops_preflight(self):
  with tempfile.TemporaryDirectory()as tmp:
   root=pathlib.Path(tmp);asset=root/'model.glb.gz';asset.write_bytes(b'original');pin={'files':{'model.glb.gz':{'sha256':p.sha(asset)}}};p.verify_snapshot(root,pin);asset.write_bytes(b'changed')
   with self.assertRaisesRegex(AssertionError,'Snapshot changed'):p.verify_snapshot(root,pin)
 def test_terrain_diagnostics_do_not_invent_unsupported_result(self):
  tags,actions=p.classify({'state':'candidate-staged'},{'outcome':'runtime-accepted-placement-unreviewed','concerns':['sampled-ground-gap-below-model-bottom']})
  self.assertEqual(tags,['elevated-component-support-context']);self.assertIn('does not prove unsupported',actions[0])
class GalleryAccountingTests(unittest.TestCase):
 def test_missing_or_duplicate_worker_group_rejected(self):
  spec=importlib.util.spec_from_file_location('merge_gallery',pathlib.Path(__file__).with_name('merge_gallery.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
  with self.assertRaisesRegex(AssertionError,'omits'):m.combine(['a','b'],[{'landmarks':[{'id':'a'}]}])
  with self.assertRaisesRegex(AssertionError,'Duplicate'):m.combine(['a'],[{'landmarks':[{'id':'a'}]},{'landmarks':[{'id':'a'}]}])
  self.assertEqual(len(m.combine(['a','b'],[{'landmarks':[{'id':'b'}]},{'landmarks':[{'id':'a'}]}])),2)
if __name__=='__main__':unittest.main()
