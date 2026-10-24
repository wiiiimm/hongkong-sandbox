import unittest
from original_face_attachment_minimax_v2_20261024 import attachment_paths

class StrictRootDiagnosticTests(unittest.TestCase):
    tri=[[[0,2,0],[1,2,0],[0,3,0]],[[1,2,0],[1,3,0],[0,3,0]]]
    report=dict(targets=[dict(incidentFaces=[0],witness=dict(position=[0,2,0]))],proof=dict(contacts=[]))
    def root(self,gap):return dict(position=[1,2,0],supportHeight=2-gap,gap=gap,strictAccepted=True,incidentFaces=[1])
    def test_existing_strict_anchor_seeds_a_real_source_path(self):
        r=attachment_paths(self.tri,self.report,[],strict_anchors=[self.root(0)])[0]
        self.assertTrue(r['hasUnrestrictedFiniteAttachment']);self.assertTrue(r['passesExistingEndpointHeight']);self.assertEqual(r['terminal']['kind'],'canonical-strict-vertical-support-anchor');self.assertFalse(r['supportApproved'])
    def test_missing_anchor_stays_disconnected(self):
        self.assertFalse(attachment_paths(self.tri,self.report,[])[0]['hasUnrestrictedFiniteAttachment'])
    def test_bad_gap_cannot_be_promoted_by_boolean(self):
        with self.assertRaises(AssertionError):attachment_paths(self.tri,self.report,[],strict_anchors=[self.root(7)])
    def test_off_source_anchor_rejected(self):
        r=self.root(0);r['position']=[2,2,0]
        with self.assertRaises(AssertionError):attachment_paths(self.tri,self.report,[],strict_anchors=[r])

if __name__=='__main__':unittest.main()
