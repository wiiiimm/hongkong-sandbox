import unittest
from candidate_availability_graph_v1_20261026 import validate


class CandidateAvailabilityGraphTest(unittest.TestCase):
    def test_diamond_has_dependency_first_order_without_duplicate_root(self):
        graph,order=validate(['podium','main','d','t'],['podium,main','podium,d','main,d','main,t'])
        self.assertEqual(graph['main'],['d','t'])
        self.assertEqual(set(order),{'podium','main','d','t'})
        self.assertEqual(len(order),4)
        for owner,peers in graph.items():
            for peer in peers:self.assertLess(order.index(peer),order.index(owner))

    def test_no_edges_preserves_independent_sources(self):
        self.assertEqual(validate(['a','b'],[]),({'a':[],'b':[]},['a','b']))

    def test_cycle_rejected(self):
        with self.assertRaisesRegex(AssertionError,'cycle'):validate(['a','b'],['a,b','b,a'])

    def test_self_dependency_rejected(self):
        with self.assertRaises(AssertionError):validate(['a'],['a,a'])

    def test_foreign_uid_rejected(self):
        with self.assertRaises(AssertionError):validate(['a'],['a,other'])

    def test_duplicate_edge_rejected(self):
        with self.assertRaisesRegex(AssertionError,'Duplicate'):validate(['a','b'],['a,b','a,b'])

    def test_duplicate_source_rejected(self):
        with self.assertRaises(AssertionError):validate(['a','a'],[])

    def test_malformed_edge_rejected(self):
        with self.assertRaises(AssertionError):validate(['a','b'],['a,b,c'])


if __name__=='__main__':unittest.main()
