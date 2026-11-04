"""Twelve hermetic actual-capture/provenance counterexamples; no DB or writes."""
import copy,unittest
import numpy as np
from run import ROOT,read
from heya_aqua_current_exposed_grade_path_20261011 import verify,P

BASE=ROOT/'docs/astra-city/government-import'
ACTUAL=BASE/'government-xl-heya-aqua-184286-184285-current-actual-ground-capture-v1-20261011'
INTERFACE=BASE/'government-xl-heya-aqua-184286-184285-current-four-world-interfaces-grade-v1-20261011'
FINITE=BASE/'government-xl-heya-aqua-184286-184285-complete-four-stream-current-finite-v1-20261011'

class ActualGradePath(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  item=read(ACTUAL/'complete-two-actor-four-stream-ground-inputs.json.gz')['rows'][P]
  interfaces=next(r for r in read(INTERFACE/'diagnostic.json.gz')['rows']if r['arithmetic']=='providerOriginal')
  finite=next(r for r in read(FINITE/'diagnostic.json.gz')['rows']if r['uid']==P and r['arithmetic']=='providerOriginal')
  cls.actual=dict(world=np.asarray(item['completeWorldStreams']['providerOriginal']['completeWorldTriangles'],dtype='<f8'),
   ground=np.asarray(item['completeDrawnGround'],dtype='<f8'),
   parts=interfaces['completeActualTopologies'][P]['sharedEdgeConnectedComponents'],
   grade_records=interfaces['allGroundPrimitiveRecordsWithRealComponentBindings'],
   cross_records=interfaces['allCrossPrimitiveRecordsWithRealComponentBindings'],finite_row=finite)
 def bad(self,change):
  data=copy.deepcopy(self.actual);change(data)
  with self.assertRaises(AssertionError):verify(**data)
 def test_actual_complete_grade_exposed_upper_interface(self):
  result=verify(**self.actual)
  self.assertGreater(len(result['podiumOriginalFacePath']),1)
  self.assertTrue(result['completeTerminalInterfaceExposure']['strictlyExposedWholePositiveInterface'])
  self.assertFalse(result['engineeringSupportCertified']);self.assertFalse(result['installedPodiumReapproved'])
 def test_changed_actual_source_vertex(self):
  self.bad(lambda d:d['world'].__setitem__((0,0,0),np.nextafter(d['world'][0,0,0],np.inf)))
 def test_changed_actual_ground_vertex(self):
  self.bad(lambda d:d['ground'].__setitem__((0,0,1),np.nextafter(d['ground'][0,0,1],np.inf)))
 def test_ground_omission(self):self.bad(lambda d:d.update(ground=d['ground'][:-1]))
 def test_stale_world_hash(self):self.bad(lambda d:d['finite_row'].update(completeWholeWorldSHA256='0'*64))
 def test_stale_ground_hash(self):self.bad(lambda d:d['finite_row'].update(completeCurrentGroundSHA256='0'*64))
 def test_missing_face_comparison(self):self.bad(lambda d:d['finite_row']['completeOriginalFaceComparisons'].pop())
 def test_false_positive_finite_coverage_record(self):
  self.bad(lambda d:d['finite_row']['completeOriginalFaceComparisons'][0]['currentDrawnGroundComparison'].update(completeFiniteOrdinaryBoundProved=False))
 def test_plausible_but_changed_facet_hash(self):
  self.bad(lambda d:d['finite_row']['completeOriginalFaceComparisons'][0].update(completeOriginalFacetSHA256='f'*64))
 def test_point_contacts_do_not_root(self):
  self.bad(lambda d:[c.update(dimension=0)for c in d['grade_records']])
 def test_unrelated_tower_contact_does_not_root(self):
  self.bad(lambda d:[c.update(towerComponent=5)for c in d['cross_records']])
 def test_duplicate_component_membership(self):
  self.bad(lambda d:d['parts'][0].__setitem__(0,d['parts'][0][1]))

if __name__=='__main__':unittest.main()
