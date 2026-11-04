import unittest
from ocean_four_mixed_basic_state_audit_v1_20261027 import face_context, enumerate_states


class MixedStateAudit(unittest.TestCase):
    def test_positive_faces_keep_actual_ids(self):
        authored = [dict(dimension=1, sourceFaceA=7, sourceFaceB=9)]
        mixed = [dict(dimension=1, sourceFaceA=8), dict(dimension=0, sourceFaceA=10)]
        result = face_context(authored, mixed, 'A')
        self.assertEqual(result['positiveMixedContacts'], 1)
        self.assertEqual(result['mixedSourceFacesWithoutPositiveAuthoredPairContact'], [8])

    def test_reverse_uses_other_source_face(self):
        authored = [dict(dimension=2, sourceFaceA=7, sourceFaceB=9)]
        self.assertEqual(face_context(authored, [dict(dimension=1, sourceFaceA=9)], 'B')
                         ['mixedSourceFacesWithoutPositiveAuthoredPairContact'], [])

    def test_original_point_is_not_positive_authored_contact(self):
        authored = [dict(dimension=0, sourceFaceA=7, sourceFaceB=9)]
        self.assertEqual(face_context(authored, [dict(dimension=1, sourceFaceA=7)], 'A')
                         ['mixedSourceFacesWithoutPositiveAuthoredPairContact'], [7])

    def test_all_states_and_directed_requirement(self):
        states = enumerate_states(['a', 'b', 'c', 'd'], {('a', 'b'), ('b', 'a')})
        self.assertEqual(len(states), 16)
        self.assertEqual(sum(s['freeOfMeasuredMixedPositiveContacts'] for s in states), 8)
        self.assertTrue(all(s['physicalAcceptance'] is False for s in states))
        self.assertFalse(next(s for s in states if s['originalUids'] == ['a'])
                         ['freeOfMeasuredMixedPositiveContacts'])

    def test_unknown_member_rejected(self):
        with self.assertRaises(AssertionError):
            enumerate_states(['a', 'b'], {('a', 'unknown')})


if __name__ == '__main__':
    unittest.main()
