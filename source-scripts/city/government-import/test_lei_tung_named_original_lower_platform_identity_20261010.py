"""Complete actual-source platform assembly and adverse fixtures, proposal only."""
import copy,importlib.util,unittest,numpy as np
from run import ROOT,HERE,read
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from lei_tung_named_original_lower_platform_identity_20261010 import UID,PLATFORM,named_proof
BASE=ROOT/'docs/astra-city/government-import';C=BASE/'government-xl-tung-sing-commercial-current-identity-diagnostic-20261010';UPPER=read(C/'selection.json.gz')['rows'][0];LOWER=next(r for r in read(BASE/'government-xl-tung-sing-interior-current-identity-inputs-v2-20261010/selection.json.gz')['rows'] if r['uid']==PLATFORM);A=decode_original_world_triangles((ROOT/UPPER['candidate']['path']).read_bytes());B=decode_original_world_triangles((ROOT/LOWER['candidate']['path']).read_bytes());s=importlib.util.spec_from_file_location('lei_tung_complete_paired_foreign_fixture',HERE/'xl-final-script-pass.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);alltri=np.concatenate([A,B]);lo,hi=alltri.min((0,1)),alltri.max((0,1));FORMS=[b for b,_,_ in m.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2])];PRIMARY=read(BASE/'government-xl-tung-sing-three-original-primary-family-20261010/primary-family-context.json.gz')['exactPrimaryFeatures'];PREVIOUS=read(C/'identity.json')
for row in [UPPER,LOWER]:row['source']['building']=next(b for b in FORMS if b['uid']==row['uid'])
def fixture():return [copy.deepcopy(PREVIOUS),copy.deepcopy(UPPER),copy.deepcopy(LOWER),A.copy(),B.copy(),copy.deepcopy(FORMS),copy.deepcopy(PRIMARY)]
class OriginalPlatformTests(unittest.TestCase):
 def reject(self,mutate):
  x=fixture();mutate(x)
  with self.assertRaises((AssertionError,KeyError,ValueError)):named_proof(*x)
 def test_complete_actual_two_originals_proposal(self):
  p=named_proof(*fixture());self.assertTrue(p['passed'],p['reasons']);self.assertEqual(p['mandatoryOriginalRuntimeUIDs'],[UID,PLATFORM]);self.assertFalse(p['standaloneOriginalImportAccepted']);self.assertFalse(p['physicalAccepted'])
 def test_standalone_upper_failed95_retained(self):
  p=named_proof(*fixture());self.assertEqual(len(p['rawStandaloneUpperCoverageReasonsRetained']),2);self.assertLess(p['independentPairedCurrentProviderChecks']['current']['rawStandaloneUpperCoverage'],.95)
 def test_other_raw_failures_preserved(self):
  x=fixture();x[0]['reasons'].append('other-independent-gate');self.assertFalse(named_proof(*x)['passed'])
 def test_upper_y_change_rejected(self):self.reject(lambda x:x[3].__setitem__((0,0,1),x[3][0,0,1]+.0001))
 def test_platform_y_change_rejected(self):self.reject(lambda x:x[4].__setitem__((0,0,1),x[4][0,0,1]+.0001))
 def test_upper_missing_original_face_rejected(self):self.reject(lambda x:x.__setitem__(3,x[3][:-1]))
 def test_platform_missing_original_face_rejected(self):self.reject(lambda x:x.__setitem__(4,x[4][:-1]))
 def test_nonfinite_source_rejected(self):self.reject(lambda x:x[4].__setitem__((0,0,0),float('nan')))
 def test_wrong_upper_source_version_rejected(self):self.reject(lambda x:x[1].__setitem__('sourceSHA256','0'*64))
 def test_wrong_platform_source_version_rejected(self):self.reject(lambda x:x[2].__setitem__('sourceSHA256','0'*64))
 def test_missing_required_current_platform_rejected(self):self.reject(lambda x:x.__setitem__(5,[b for b in x[5] if b['uid']!=PLATFORM]))
 def test_duplicate_current_actor_rejected(self):self.reject(lambda x:x[5].append(copy.deepcopy(x[5][0])))
 def test_duplicate_unique_primary_rejected(self):self.reject(lambda x:x[6].append(copy.deepcopy(x[6][0])))
 def test_wrong_primary_component_role_rejected(self):self.reject(lambda x:next(p for p in x[6] if p['attributes']['BuildingCSUID']=='3417111358P20060312')['attributes'].__setitem__('BuildingBlockType','Tower'))
 def test_primary_platform_inactive_rejected(self):self.reject(lambda x:next(p for p in x[6] if p['attributes']['BuildingCSUID']=='3417111358P20060312')['attributes'].__setitem__('Status','Inactive'))
 def test_source_graph_not_owned_rejected(self):self.reject(lambda x:x[0]['originalOwnership'].__setitem__('sourceGraphVerified',False))
 def test_platform_vertical_role_reversed_rejected(self):
  def mutate(x):
   next(b for b in x[5] if b['uid']==PLATFORM)['topHeightHKPD']=74;x[2]['source']['building']=copy.deepcopy(next(b for b in x[5] if b['uid']==PLATFORM));next(p for p in x[6] if p['attributes']['BuildingCSUID']=='3417111358P20060312')['attributes']['TopHeight']=74
  self.reject(mutate)
 def test_primary_source_creation_date_changed_rejected(self):self.reject(lambda x:next(p for p in x[6] if p['attributes']['BuildingCSUID']=='3417011358T20050430')['attributes'].__setitem__('DateCreate',0))
 def test_unrelated_actor_still_foreign(self):
  x=fixture();actor=copy.deepcopy(next(b for b in x[5] if b['uid']==UID));actor['uid']='adverse-unrelated-actor';lo=np.concatenate([A,B]).min((0,1));hi=np.concatenate([A,B]).max((0,1));actor['rings']=[[[lo[0]-1,lo[2]-1],[hi[0]+1,lo[2]-1],[hi[0]+1,hi[2]+1],[lo[0]-1,hi[2]+1],[lo[0]-1,lo[2]-1]]];x[5].append(actor);p=named_proof(*x);self.assertFalse(p['passed']);self.assertGreater(p['independentPairedCurrentProviderChecks']['current']['allOtherForeignExcessM2'],1)
 def test_all_parts_actors_and_independent_physics_retained(self):
  x=fixture();p=named_proof(*x);self.assertEqual(p['completeOriginalPartCounts'],[19,3]);self.assertEqual(p['completeCurrentForeignActorsRetained'],x[5]);self.assertFalse(p['foreignCollisionExemption']);self.assertFalse(p['foreignTerrainExemption']);self.assertFalse(p['foreignRemoval']);self.assertFalse(p['installationApproved'])
if __name__=='__main__':unittest.main()
