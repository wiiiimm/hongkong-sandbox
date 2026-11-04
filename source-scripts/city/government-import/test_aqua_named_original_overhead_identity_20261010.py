"""Actual complete source fixtures and adverse mutations; no physical approval."""
import unittest,copy
from run import ROOT,read
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from aqua_named_original_overhead_identity_20261010 import named_proof,UID,FOREIGN
BASE=ROOT/'docs/astra-city/government-import';RAW=BASE/'government-xl-aqua-marine-current-full-cell-preflight-20261010';CONTEXT=BASE/'government-xl-aqua-marine-fresh-overhead-source-context-20261010'
ROW=read(RAW/'selection.json.gz')['rows'][0];PREVIOUS=read(RAW/'raw-full-cell-proof.json');FORMS=read(RAW/'all-current-forms.json.gz')['forms'];PRIMARY=read(CONTEXT/'exact-current-primary.json')['features'];SEL=read(BASE/'government-xl-aqua-marine-original-recovery-20261010/selection.json.gz')['rows'];OWN=decode_original_world_triangles((ROOT/next(r['candidate']['path'] for r in SEL if r['uid']==UID)).read_bytes());OTHER=decode_original_world_triangles((ROOT/next(r['candidate']['path'] for r in SEL if r['uid']==FOREIGN)).read_bytes())
def fixture():return [copy.deepcopy(PREVIOUS),copy.deepcopy(ROW),OWN.copy(),OTHER.copy(),copy.deepcopy(FORMS),copy.deepcopy(PRIMARY)]
class OriginalTests(unittest.TestCase):
 def rejected(self,f):
  args=fixture();f(args)
  with self.assertRaises((AssertionError,KeyError,ValueError)):named_proof(*args)
 def test_actual_complete_sources_positive_identity_only(self):
  p=named_proof(*fixture());self.assertTrue(p['passed']);self.assertFalse(p['physicalAccepted']);self.assertFalse(p['foreignCollisionExemption']);self.assertEqual(len(p['completeOriginalOverheadFaceIds']),656)
 def test_all_raw_overlap_retained(self):self.assertEqual(len(named_proof(*fixture())['rawUnrelatedOverlapReasonsRetained']),2)
 def test_other_failure_preserved(self):
  x=fixture();x[0]['reasons'].append('ground-identity-independent-failure');self.assertFalse(named_proof(*x)['passed'])
 def test_own_y_mutation(self):self.rejected(lambda x:x[2].__setitem__((0,0,1),x[2][0,0,1]+.0001))
 def test_other_y_mutation(self):self.rejected(lambda x:x[3].__setitem__((0,0,1),x[3][0,0,1]+.0001))
 def test_own_x_mutation(self):self.rejected(lambda x:x[2].__setitem__((0,0,0),x[2][0,0,0]+.0001))
 def test_missing_face(self):self.rejected(lambda x:x.__setitem__(2,x[2][:-1]))
 def test_nonfinite_original(self):self.rejected(lambda x:x[2].__setitem__((0,0,1),float('nan')))
 def test_wrong_source_version(self):self.rejected(lambda x:x[1].__setitem__('sourceSHA256','0'*64))
 def test_wrong_original_model(self):self.rejected(lambda x:x[1].__setitem__('modelId','B333622156101063C0'))
 def test_false_ownership(self):self.rejected(lambda x:x[0]['originalOwnership'].__setitem__('sourceGraphVerified',False))
 def test_duplicate_current_actor(self):self.rejected(lambda x:x[4].append(copy.deepcopy(x[4][0])))
 def test_missing_foreign_actor(self):self.rejected(lambda x:x.__setitem__(4,[b for b in x[4] if b['uid']!=FOREIGN]))
 def test_duplicate_primary(self):self.rejected(lambda x:x[5].append(copy.deepcopy(x[5][0])))
 def test_primary_inactive(self):self.rejected(lambda x:x[5][0]['attributes'].__setitem__('Status','Retired'))
 def test_provider_wrong_type(self):self.rejected(lambda x:x[5][0]['attributes'].__setitem__('BuildingBlockType','Podium'))
 def test_provider_wrong_id(self):self.rejected(lambda x:x[5][0]['attributes'].__setitem__('BuildingID',1))
 def test_provider_wrong_date(self):self.rejected(lambda x:x[5][0]['attributes'].__setitem__('DateCreate',0))
 def test_provider_current_height_mismatch(self):self.rejected(lambda x:x[5][0]['attributes'].__setitem__('TopHeight',12))
 def test_complete_separate_body_reaches_overhead(self):
  def f(x):
   next(b for b in x[4] if b['uid']==FOREIGN)['topHeightHKPD']=14;next(b for b in x[5] if b['attributes']['BuildingCSUID']=='3336221561T20060914')['attributes']['TopHeight']=14
  self.rejected(f)
 def test_current_name_changed(self):
  def f(x):
   next(b for b in x[4] if b['uid']==UID)['name']='Other';x[1]['source']['building']['name']='Other'
  self.rejected(f)
if __name__=='__main__':unittest.main()
