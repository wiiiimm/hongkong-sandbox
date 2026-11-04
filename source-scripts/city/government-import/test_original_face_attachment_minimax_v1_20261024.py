import unittest
from original_face_attachment_minimax_v1_20261024 import attachment_paths

class AttachmentDiagnosticTests(unittest.TestCase):
    def contact(self,face,p):return dict(sourceFaceA=face,sourcePrimitiveDimensionA=2,sourcePrimitiveDimensionB=2,dimension=1,exactPoints=[[str(v)for v in p]])
    def target(self,face,p):return dict(incidentFaces=[face],witness=dict(position=p))
    def test_attachment_above_endpoints_is_not_admitted(self):
        tri=[[[0,0,0],[1,2,0],[0,2,0]],[[1,2,0],[1,0,0],[0,2,0]]]
        report=dict(targets=[self.target(0,[0,0,0])],proof=dict(contacts=[self.contact(1,[1,0,0])]))
        r=attachment_paths(tri,report,[])[0]
        self.assertTrue(r['hasUnrestrictedFiniteAttachment']);self.assertEqual(r['riseAboveEndpointsM'],2)
        self.assertFalse(r['passesExistingEndpointHeight']);self.assertFalse(r['supportApproved'])
    def test_low_join_keeps_zero_rise(self):
        tri=[[[0,0,0],[1,0,0],[0,2,0]],[[1,0,0],[1,2,0],[0,2,0]]]
        report=dict(targets=[self.target(0,[0,0,0])],proof=dict(contacts=[self.contact(1,[1,0,0])]))
        r=attachment_paths(tri,report,[])[0];self.assertEqual(r['riseAboveEndpointsM'],0);self.assertTrue(r['passesExistingEndpointHeight']);self.assertFalse(r['supportApproved'])
    def test_point_only_touch_is_disconnected(self):
        tri=[[[0,0,0],[1,0,0],[0,1,0]],[[1,0,0],[2,0,0],[2,1,0]]]
        report=dict(targets=[self.target(0,[0,0,0])],proof=dict(contacts=[self.contact(1,[2,0,0])]))
        r=attachment_paths(tri,report,[])[0];self.assertFalse(r['hasUnrestrictedFiniteAttachment']);self.assertFalse(r['supportApproved'])
    def test_point_join_rejected(self):
        tri=[[[0,0,0],[1,0,0],[0,1,0]],[[1,0,0],[2,0,0],[2,1,0]]]
        report=dict(targets=[self.target(0,[0,0,0])],proof=dict(contacts=[self.contact(1,[2,0,0])]))
        with self.assertRaises(AssertionError):attachment_paths(tri,report,[dict(dimension=0,primitiveDimensions=[2,2])])

if __name__=='__main__':unittest.main()
