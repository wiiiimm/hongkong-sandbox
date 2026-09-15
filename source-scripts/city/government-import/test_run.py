import copy
import unittest
from run import select_candidates

class SelectionTests(unittest.TestCase):
    def setUp(self):
        self.cached={str(i):{'currentNative':None,'candidate':{'entry':{'sourceTile':'A','buildingCSUID':str(i),'objectId':i}}} for i in range(6)}
        self.current={str(i):{'building':{'objectId':i,'buildingCSUID':str(i)}} for i in range(6)}
        self.plan={str(i):{'action':'assess'} for i in range(6)}
    def test_skip_accepted_installed_completed_and_embedded(self):
        self.plan['0']['action']='skip';self.cached['1']['currentNative']={'installed':True};self.current['2']['building']['modelGeometry']={'native':True}
        self.assertEqual(select_candidates(self.cached,self.current,self.plan,{'3'},2),['4','5'])
    def test_identity_changes_and_missing_current_forms_do_not_enter_batch(self):
        self.current['0']['building']['buildingCSUID']='changed';del self.current['1'];del self.plan['2']
        self.assertEqual(select_candidates(self.cached,self.current,self.plan,set(),2),['3','4'])
    def test_exact_count_and_deterministic_source_order(self):
        self.cached['0']['candidate']['entry']['sourceTile']='Z'
        self.assertEqual(select_candidates(dict(reversed(list(self.cached.items()))),self.current,self.plan,set(),2),['1','2'])
        with self.assertRaises(ValueError):select_candidates(self.cached,self.current,self.plan,set(),7)

if __name__=='__main__': unittest.main()
