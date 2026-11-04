import copy
import unittest
import numpy as np
from original_face_attachment_endpoint_choices_v1_20261029 import attachment_paths

class ExactEndpointChoiceTests(unittest.TestCase):
    tri=[[[0,0,0],[0,1.5,0],[1,1.5,0]],[[0,1.5,0],[1,1.5,0],[.5,0,0]]]
    contact=dict(sourceFaceA=1,sourceFaceB=4,sourcePrimitiveDimensionA=2,sourcePrimitiveDimensionB=2,dimension=1,exactPoints=[['1/2','1','0'],['1/2','3/2','0']])
    def report(self):return dict(targets=[dict(witness=dict(position=[0,0,0]),incidentFaces=[0])],proof=dict(contacts=[copy.deepcopy(self.contact)]))
    def test_existing_low_endpoint_failure_is_preserved(self):
        r=attachment_paths(self.tri,self.report(),[])[0]
        self.assertFalse(r['passesExistingEndpointHeight']);self.assertEqual(r['riseAboveEndpointsM'],.5)
    def test_actual_upper_endpoint_resolves_without_tolerance_change(self):
        r=attachment_paths(self.tri,self.report(),[],endpoint_selection='highest')[0]
        self.assertTrue(r['passesExistingEndpointHeight']);self.assertEqual(r['riseAboveEndpointsM'],0)
        self.assertEqual(r['terminal']['exactEndpointHeight'],'3/2');self.assertFalse(r['supportApproved'])
    def test_no_authored_upper_endpoint_stays_failed(self):
        d=self.report();d['proof']['contacts'][0]['exactPoints']=d['proof']['contacts'][0]['exactPoints'][:1]
        self.assertFalse(attachment_paths(self.tri,d,[],endpoint_selection='highest')[0]['passesExistingEndpointHeight'])
    def test_off_surface_endpoint_is_rejected(self):
        d=self.report();d['proof']['contacts'][0]['exactPoints'].append(['10','10','10'])
        with self.assertRaises(AssertionError):attachment_paths(self.tri,d,[],endpoint_selection='highest')
    def test_inputs_remain_exact(self):
        tri=np.asarray(self.tri);before=tri.copy();d=self.report();before_report=copy.deepcopy(d)
        attachment_paths(tri,d,[],endpoint_selection='highest')
        self.assertTrue(np.array_equal(tri,before));self.assertEqual(d,before_report)
    def test_unknown_strategy_is_rejected(self):
        with self.assertRaises(AssertionError):attachment_paths(self.tri,self.report(),[],endpoint_selection='invent')

if __name__=='__main__':unittest.main()
