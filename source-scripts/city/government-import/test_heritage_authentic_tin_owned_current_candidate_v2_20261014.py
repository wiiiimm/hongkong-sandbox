"""Actual saved nominee/owned setup schema, no geometry/render/DB/lease."""
import copy,unittest
import heritage165054_authentic_tin_owned_ordinary_v2_20261014 as a
class CurrentTwoSourceCandidate(unittest.TestCase):
    def test_actual8341_candidate_and_raw18_22_context_bind(self):
        packet=a.read(a.NOMINATION/'diagnostic.json');c=a.read(a.NOMINATION/'terrain-candidates.json');patch=a.read(a.ROOT/c[0]['path'])
        self.assertEqual(a.bind_candidate(packet,c,patch),c[0]);self.assertEqual(c[0]['triangles'],8341);self.assertTrue(packet['all22SourceBelowMinus05WarningsUnresolved']);self.assertTrue(packet['rawStrictFoundationRemainsFalse'])
    def test_actual45_pending_record_retains_false_acceptance_without_duplicate_keys(self):
        s=a.read(a.nomination.prior.north.DOC/'proposal-input.json');before=copy.deepcopy(s);c=a.read(a.NOMINATION/'terrain-candidates.json')[0];o=a.pending_scope_record(s,c)
        self.assertEqual(s,before);self.assertFalse(o['physicalAccepted']);self.assertFalse(o['installationApproved']);self.assertTrue(o['wholeNativeBASICBeforeAfterQualificationNotExecuted']);self.assertEqual(len(a.resources(s['scope']['allActorsForNominationLease'])),91)
if __name__=='__main__':unittest.main()
