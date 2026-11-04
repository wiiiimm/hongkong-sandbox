"""Configuration counterexamples; source acceptance remains adapter-owned."""
import copy,importlib.util,unittest
from unittest.mock import patch
from pathlib import Path
HERE=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('plain_stage_test',HERE/'xl-terrain-recovery-20261010-plain-single-source-stage-v1.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class Interface(unittest.TestCase):
 def setUp(self):
  binding=dict(path=str((HERE/'xl-terrain-recovery-20261010-green18-current-complete-support-v1.py').relative_to(m.ROOT)),sha256='a'*64)
  self.cfg=dict(schema='plain-single-source-original-stage-v1',batch='government-xl-test-stage-20261010',sources={'landsd/6462:0':'b'*64},completeOriginalFaces=11088,completeOriginalComponents=903,plainNewTerrain=True,retainedNativeUIDs=[],supportDependencies=[],physicalReceipt=binding,currentRoleReceipt=binding,currentTypedRole=binding,currentRoleRunner=binding)
 def check(self,cfg=None,changed=False):
  c=copy.deepcopy(self.cfg if cfg is None else cfg)
  with patch.object(m,'read',return_value=c),patch.object(m,'ref',side_effect=lambda p:dict(path=str(p.relative_to(m.ROOT)),sha256='c'*64 if changed else 'a'*64)):
   return m.configuration(m.ROOT/'placeholder-config.json')
 def test_valid_pinned_plain_single_configuration(self):self.assertEqual(self.check(),self.cfg)
 def bad(self,key,value):
  cfg=copy.deepcopy(self.cfg);cfg[key]=value
  with self.assertRaises(AssertionError):self.check(cfg)
 def test_schema_change(self):self.bad('schema','arbitrary-acceptance')
 def test_traversing_batch(self):self.bad('batch','../government-xl-test')
 def test_two_sources(self):self.bad('sources',{'landsd/6462:0':'b'*64,'landsd/99:0':'d'*64})
 def test_malformed_source_hash(self):self.bad('sources',{'landsd/6462:0':'z'*64})
 def test_short_source_hash(self):self.bad('sources',{'landsd/6462:0':'b'*63})
 def test_unreviewed_replacement(self):self.bad('plainNewTerrain',False)
 def test_retained_native_requires_distinct_harness(self):self.bad('retainedNativeUIDs',['landsd/99:0'])
 def test_support_dependencies_require_distinct_harness(self):self.bad('supportDependencies',[dict(uid='landsd/99:0')])
 def test_zero_source_faces(self):self.bad('completeOriginalFaces',0)
 def test_boolean_source_faces(self):self.bad('completeOriginalFaces',True)
 def test_fractional_component_inventory(self):self.bad('completeOriginalComponents',1.5)
 def test_changed_acceptance_runner_or_receipt(self):
  with self.assertRaises(AssertionError):self.check(changed=True)
 def test_runner_outside_government_import_scope(self):
  cfg=copy.deepcopy(self.cfg);cfg['currentRoleRunner']=dict(path='3d-viewer/city/app.js',sha256='a'*64)
  with self.assertRaises(AssertionError):self.check(cfg)
 def test_runner_parent_escape_resolves_outside_scope(self):
  cfg=copy.deepcopy(self.cfg);cfg['currentRoleRunner']=dict(path=str(HERE.relative_to(m.ROOT))+'/../building-batch/fake.py',sha256='a'*64)
  with self.assertRaises(AssertionError):self.check(cfg)
 def test_config_parent_escape_outside_repository(self):
  with patch.object(m,'read',return_value=self.cfg):
   with self.assertRaises(AssertionError):m.configuration(m.ROOT/'../outside-config.json')
class CurrentAcceptance(unittest.TestCase):
 def setUp(self):
  self.cfg=dict(sources={'landsd/6462:0':'b'*64},completeOriginalFaces=11088,completeOriginalComponents=903,**{k:dict(path='placeholder-'+k,sha256='a'*64) for k in ['physicalReceipt','currentRoleReceipt','currentTypedRole','currentRoleRunner']})
  self.typed=dict(independentPhysicalChecksPassed=True,unresolvedIndependentPhysicalReasons=[],uids=['landsd/6462:0'],completeOriginalFaces=11088,completeOriginalComponents=903,manifestSHA256=m.digest(b'current-manifest'),sourceGeometryChanges=0,installationApproved=False,publication=False,completeCurrentIdentities=[dict(uid='landsd/6462:0',passed=True)])
 def rejects(self,key,value):
  import types
  typed=copy.deepcopy(self.typed);typed[key]=value
  with patch.object(m,'ref',side_effect=lambda p:dict(path=str(p.relative_to(m.ROOT)),sha256='a'*64)),patch.object(m,'read',return_value=typed),patch.object(m,'module',return_value=types.SimpleNamespace(recheck=lambda:typed)),patch.object(Path,'read_bytes',return_value=b'current-manifest'):
   with self.assertRaises(AssertionError):m.recheck(self.cfg)
 def test_independent_physics_not_passed(self):self.rejects('independentPhysicalChecksPassed',False)
 def test_truthy_physics_label_is_not_true(self):self.rejects('independentPhysicalChecksPassed','yes')
 def test_unresolved_original_component(self):self.rejects('unresolvedIndependentPhysicalReasons',['unsupported-original-component'])
 def test_different_source_actor(self):self.rejects('uids',['landsd/99:0'])
 def test_omitted_original_face(self):self.rejects('completeOriginalFaces',11087)
 def test_omitted_original_component(self):self.rejects('completeOriginalComponents',902)
 def test_stale_current_manifest(self):self.rejects('manifestSHA256','c'*64)
 def test_geometry_changed(self):self.rejects('sourceGeometryChanges',1)
 def test_installation_approval_not_inferred(self):self.rejects('installationApproved',True)
 def test_prior_publication_not_accepted(self):self.rejects('publication',True)
 def test_identity_failure(self):self.rejects('completeCurrentIdentities',[dict(uid='landsd/6462:0',passed=False)])
if __name__=='__main__':unittest.main()
