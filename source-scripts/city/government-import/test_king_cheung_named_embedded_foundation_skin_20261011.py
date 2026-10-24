"""Actual pinned four-world foundation fixtures and adverse binding/geometry cases."""
import copy,unittest
import numpy as np
from run import ROOT,read
import king_cheung_named_embedded_foundation_skin_20261011 as k
BASE=ROOT/'docs/astra-city/government-import'
def fixture(mode='providerOriginal'):
 data=read(BASE/'government-xl-king-cheung-95691-current-actual-ground-capture-v1-20261011/complete-four-stream-ground-inputs.json.gz')
 finite=read(BASE/'government-xl-king-cheung-95691-complete18742-current-finite-diagnostic-v1-20261011/diagnostic.json.gz')
 w=np.asarray(data['completeWorldStreams'][mode]['completeWorldTriangles'],dtype='<f8');g=np.asarray(data['completeDrawnGround'],dtype='<f8')
 rows=next(r['complete18742FaceComparisons']for r in finite['rows']if r['arithmetic']==mode)
 binding=dict(uid=k.UID,sourceSHA256=k.SOURCE,mode=mode,completeWorldSHA256=k.sha(w),completeGroundSHA256=k.sha(g),completeFiniteRowsSHA256=k.canonical(rows))
 return dict(world=w,ground=g,finite_rows=rows,mode=mode,interpreted_role=k.ROLE,expected_binding=binding,current_binding=binding)
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.f=fixture()
 def test_actual_all_four_complete_foundation_worlds(self):
  for mode in k.FINITE_ROWS:
   with self.subTest(mode=mode):
    r=k.verify(**fixture(mode));self.assertFalse(r['installationApproved']);self.assertFalse(r['closedSolidCertified']);self.assertEqual(r['sourceBackedFoundationLeaf799']['soleSharedEdgeNeighbour'],798)
 def reject(self,mutation):
  f=copy.deepcopy(self.f);mutation(f)
  with self.assertRaises((AssertionError,ValueError)):k.verify(**f)
 def test_wrong_named_role(self):self.reject(lambda f:f.update(interpreted_role='generic foundation'))
 def test_wrong_uid(self):self.reject(lambda f:f['current_binding'].update(uid='landsd/1:0'))
 def test_wrong_source(self):self.reject(lambda f:f['current_binding'].update(sourceSHA256='0'*64))
 def test_wrong_world_binding(self):self.reject(lambda f:f['current_binding'].update(completeWorldSHA256='0'*64))
 def test_wrong_ground_binding(self):self.reject(lambda f:f['current_binding'].update(completeGroundSHA256='0'*64))
 def test_wrong_row_binding(self):self.reject(lambda f:f['current_binding'].update(completeFiniteRowsSHA256='0'*64))
 def test_wrong_arithmetic(self):self.reject(lambda f:f.update(mode='rounded'))
 def test_missing_world_face(self):self.reject(lambda f:f.update(world=f['world'][:-1]))
 def test_missing_ground_facet(self):self.reject(lambda f:f.update(ground=f['ground'][:-1]))
 def test_source_raise_is_rejected(self):self.reject(lambda f:f['world'].__setitem__((799,slice(None),1),14.0))
 def test_source_lower_cap_is_rejected(self):self.reject(lambda f:f['world'].__setitem__((2473,slice(None),1),13.0))
 def test_changed_actual_grade(self):self.reject(lambda f:f['ground'].__setitem__((slice(None),slice(None),1),13.0))
 def test_zero_area_glue_is_rejected(self):self.reject(lambda f:f['world'].__setitem__(799,f['world'][799,0]))
 def test_missing_finite_record(self):self.reject(lambda f:f.update(finite_rows=f['finite_rows'][:-1]))
 def test_duplicate_finite_record(self):self.reject(lambda f:f['finite_rows'].__setitem__(799,f['finite_rows'][798]))
 def test_reordered_finite_record(self):self.reject(lambda f:f['finite_rows'].reverse())
 def test_unknown_failure_cannot_be_removed(self):self.reject(lambda f:f['finite_rows'][2473]['groundComparisons']['currentDrawn'].update(completeFiniteOrdinaryBoundProved=False))
 def test_buried_leaf_raw_measurement_cannot_change(self):self.reject(lambda f:f['finite_rows'][799]['groundComparisons']['currentDrawn']['coarse'].update(exactCertifiedLowerClearanceM='0'))
 def test_nonfinite_source(self):self.reject(lambda f:f['world'].__setitem__((799,0,0),float('nan')))
 def test_nonfinite_ground(self):self.reject(lambda f:f['ground'].__setitem__((0,0,0),float('inf')))
if __name__=='__main__':unittest.main()
