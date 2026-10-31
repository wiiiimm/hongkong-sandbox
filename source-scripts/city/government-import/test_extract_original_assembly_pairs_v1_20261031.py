import copy
import unittest

from extract_original_assembly_pairs_v1_20261031 import pair_rows


class PairBinding(unittest.TestCase):
    def fixture(self):
        return dict(uids=['a', 'b', 'c'], rows=[dict(uid='a', peerUid='b', mode=m)
                    for m in ['original', 'literal', 'leftF32', 'balancedF32']])

    def test_request_order_does_not_reverse_contact_face_indices(self):
        data = self.fixture()
        self.assertEqual(pair_rows(data, 'b', 'a')[0], ['a', 'b'])

    def test_four_rows_with_duplicate_mode_do_not_cover_four_worlds(self):
        data = self.fixture()
        data['rows'][0]['mode'] = 'literal'
        with self.assertRaises(AssertionError):
            pair_rows(data, 'a', 'b')

    def test_mode_cannot_silently_reverse_contact_face_indices(self):
        data = self.fixture()
        data['rows'][0].update(uid='b', peerUid='a')
        with self.assertRaises(AssertionError):
            pair_rows(data, 'a', 'b')

    def test_returned_records_do_not_mutate_the_completed_parent(self):
        data = self.fixture()
        before = copy.deepcopy(data)
        _, rows = pair_rows(data, 'a', 'b')
        rows[0]['mode'] = 'changed'
        self.assertEqual(data, before)


if __name__ == '__main__':
    unittest.main()
