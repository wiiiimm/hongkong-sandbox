"""Actual saved source baseline and bounded adverse identity-only cases. ROOT runs."""
from copy import deepcopy
import importlib.util
from pathlib import Path
import unittest
from heritage_current_typed_identity_draft_v1 import compose,validate_scope
_spec=importlib.util.spec_from_file_location('heritage_identity_actual_fixture',Path(__file__).with_name('heritage-current-typed-identity-caller-draft-v2.py'))
_caller=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(_caller)
actual_test_fixture=_caller.actual_test_fixture

class MuseumIdentityTests(unittest.TestCase):
 def inputs(self):return deepcopy(actual_test_fixture())
 def rejected(self,change):
  x=self.inputs();change(x)
  with self.assertRaises(AssertionError):compose(**x)
 def test_actual_complete_baseline(self):
  r=compose(**self.inputs());self.assertTrue(r['passed']);self.assertEqual(r['reasons'],[])
  self.assertEqual(len(r['ordinaryExtentFaceIds']),14678);self.assertIn('landsd/57455:0',r['independentForeignUIDs'])
  self.assertNotIn('landsd/104467:0',r['independentForeignUIDs'])
  self.assertFalse(r['physicalAccepted']);self.assertFalse(r['associatedIdentityActor']['all1106ClassifiedAsCanopy'])
 def test_source_world_change(self):self.rejected(lambda x:x['world'].__setitem__((0,0,0),x['world'][0,0,0]+1))
 def test_missing_complete_face(self):self.rejected(lambda x:x.__setitem__('world',x['world'][:-1]))
 def test_changed_source_tuple(self):self.rejected(lambda x:x['row'].__setitem__('sourceSHA256','0'*64))
 def test_changed_model(self):self.rejected(lambda x:x['row'].__setitem__('modelId','B371252646702063C0'))
 def test_changed_pose(self):self.rejected(lambda x:x['row']['candidate']['entry'].__setitem__('rootTranslation',[0,0,0]))
 def test_missing_far_face(self):self.rejected(lambda x:x['source_context']['attribution']['farOriginalFaceIds'].pop())
 def test_missing_perimeter_interpretation_face(self):self.rejected(lambda x:x['interpretation']['viewInventoryOnlyNotComponents'][1]['farFaceIds'].pop())
 def test_blanket1106_scope_mutation(self):self.rejected(lambda x:x['source_context']['attribution']['overlaps'][0].__setitem__('completeAttributedOriginalFaceIds',[0]))
 def test_source_context_false_physics_promoted(self):self.rejected(lambda x:x['source_context'].__setitem__('physicalAccepted',True))
 def test_missing_starmart(self):self.rejected(lambda x:x.__setitem__('forms',[b for b in x['forms']if b['uid']!='landsd/57455:0']))
 def test_changed_starmart_form(self):self.rejected(lambda x:next(b for b in x['forms']if b['uid']=='landsd/57455:0').__setitem__('height',999))
 def test_target_hole_removed(self):self.rejected(lambda x:next(b for b in x['forms']if b['uid']=='landsd/165054:0')['rings'].pop())
 def test_other_raw_guard_survives(self):
  x=self.inputs();x['previous']['reasons'].append('fresh-exact-component-route-not-unique-or-differs');r=compose(**x)
  self.assertFalse(r['passed']);self.assertIn('fresh-exact-component-route-not-unique-or-differs',r['reasons'])
 def test_cell_negative_survives(self):
  x=self.inputs();x['previous']['exactWholeCellCoverage']['covered']=False;x['previous']['reasons'].append('original-source-does-not-cover-whole-georef-cell');r=compose(**x)
  self.assertFalse(r['passed']);self.assertIn('original-source-does-not-cover-whole-georef-cell',r['reasons'])
 def test_graph_negative_survives(self):
  x=self.inputs();x['previous']['originalOwnership']['sourceGraphVerified']=False;x['previous']['reasons'].append('source-root-name');r=compose(**x)
  self.assertFalse(r['passed']);self.assertIn('source-root-name',r['reasons'])

if __name__=='__main__':unittest.main()
