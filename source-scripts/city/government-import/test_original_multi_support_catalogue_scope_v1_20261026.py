import copy
import unittest
from original_multi_support_catalogue_scope_v1_20261026 import verify

class MultiParentScopeTests(unittest.TestCase):
    def setUp(self):
        self.sources={u:u*64 for u in ['a','b','c']};self.graph={'a':['b','c'],'b':[],'c':[]}
        self.models=[dict(uid=u,sha256=h,buildingCSUID='cs-'+u,proceduralWindows=False)for u,h in self.sources.items()]
        self.models[0]['supportDependencies']=[dict(uid=u,state='installed',buildingCSUID='cs-'+u,sha256=self.sources[u])for u in ['b','c']]
    def test_exact_multi_parent(self):self.assertTrue(verify(self.models,self.sources,self.graph))
    def reject(self,change):
        change()
        with self.assertRaises((AssertionError,ValueError,KeyError)):verify(self.models,self.sources,self.graph)
    def test_missing_parent(self):self.reject(lambda:self.models[0]['supportDependencies'].pop())
    def test_changed_sha(self):self.reject(lambda:self.models[0]['supportDependencies'][0].update(sha256='changed'))
    def test_changed_identity(self):self.reject(lambda:self.models[0]['supportDependencies'][0].update(buildingCSUID='other'))
    def test_changed_state(self):self.reject(lambda:self.models[0]['supportDependencies'][0].update(state='pending'))
    def test_unknown_parent(self):self.reject(lambda:self.graph['a'].append('other'))
    def test_duplicate_parent(self):self.reject(lambda:self.graph['a'].append('b'))
    def test_cycle(self):self.reject(lambda:self.graph['b'].append('a'))
    def test_windows(self):self.reject(lambda:self.models[0].update(proceduralWindows=True))
    def test_suppression(self):self.reject(lambda:self.models[0].update(suppressesBuildingUids=['c']))
    def test_duplicate_model(self):self.reject(lambda:self.models.append(copy.deepcopy(self.models[0])))
    def test_missing_graph_row(self):self.reject(lambda:self.graph.pop('c'))

if __name__=='__main__':unittest.main()
