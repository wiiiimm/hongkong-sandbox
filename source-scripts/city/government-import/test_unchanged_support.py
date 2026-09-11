import unittest
from unchanged_support import unchanged_supports
class UnchangedSupportTests(unittest.TestCase):
    def inputs(self):
        def form(uid,base,height):return {'building':{'uid':uid,'base':base,'height':height,'rings':[[[0,0],[10,0],[10,10],[0,10],[0,0]]]},'existingNative':False}
        return {'rows':[form('tower',10,20),form('podium',1,9)]},{'rows':[{'uid':'tower','reasons':['increased-neighbour-ground-gap']},{'uid':'podium','reasons':[]}]}
    def test_unchanged_solid_support_resolves_ground_only_warning(self):
        a,b=self.inputs();self.assertEqual(unchanged_supports(a,b,set())[0]['supportUid'],'podium')
    def test_replaced_native_or_regressed_support_never_resolves(self):
        for kind in ['replaced','native','regressed']:
            a,b=self.inputs()
            if kind=='native':a['rows'][1]['existingNative']=True
            if kind=='regressed':b['rows'][1]['reasons']=['increased-neighbour-burial']
            self.assertEqual(unchanged_supports(a,b,{'podium'} if kind=='replaced' else set()),[])
    def test_incomplete_or_wrong_height_support_does_not_resolve(self):
        a,b=self.inputs();a['rows'][1]['building']['height']=8;self.assertEqual(unchanged_supports(a,b,set()),[])
        a,b=self.inputs();a['rows'][1]['building']['rings'][0][1]=[5,0];self.assertEqual(unchanged_supports(a,b,set()),[])
if __name__=='__main__':unittest.main()
