import copy
import unittest
from nested_child_preservation import child_sha,parent_without_retained_child


class NestedChildPreservationTests(unittest.TestCase):
    def setUp(self):
        self.child={'id':'old','coarseCells':[2,2,4,4],'meta':{'targetUids':['native','basic']},
                    'nativeMesh':{'position':[0,1,0,1,1,0,0,1,1],'index':[0,1,2]}}
        self.other={'id':'other','coarseCells':[8,8,10,10],'meta':{'targetUids':['other']},
                    'nativeMesh':{'position':[8,1,8,9,1,8,8,1,9],'index':[0,1,2]}}
        self.parent={'elev':[1,2,3,4],'renderedElev':[1,2,3,4],
                     'meta':{'georef':{'aE':5,'aN':-5}},'patches':[self.child,self.other]}
        self.new={'id':'new','coarseCells':[1,1,5,5],'meta':{'targetUids':['native','basic','new']}}
        self.proof={'supersededChildId':'old','supersededChildSHA256':child_sha(self.child),
                    'boundsOfEveryRetainedModelInsideProtectedProjection':True,'sourceProjectionIntersectionM2':0}

    def run_scope(self):
        return parent_without_retained_child(self.parent,self.new,'old',self.proof)

    def test_preserves_grid_other_native_and_input(self):
        before=copy.deepcopy(self.parent);result=self.run_scope()
        self.assertEqual(self.parent,before)
        self.assertEqual(result['elev'],before['elev']);self.assertEqual(result['renderedElev'],before['renderedElev'])
        self.assertEqual(result['meta'],before['meta']);self.assertEqual(result['patches'],[self.other])
        result['patches'][0]['nativeMesh']['position'][0]=99
        self.assertEqual(self.other['nativeMesh']['position'][0],8)

    def test_rejects_stale_child_geometry_proof(self):
        self.child['nativeMesh']['position'][1]=2
        with self.assertRaisesRegex(AssertionError,'Stale'):self.run_scope()

    def test_rejects_dropped_basic_target_or_native_region(self):
        self.new['meta']['targetUids'].remove('basic')
        with self.assertRaisesRegex(AssertionError,'target'):self.run_scope()
        self.new['meta']['targetUids'].append('basic');self.new['coarseCells'][0]=3
        with self.assertRaisesRegex(AssertionError,'region'):self.run_scope()

    def test_rejects_source_or_other_child_overlap(self):
        self.proof['sourceProjectionIntersectionM2']=1
        with self.assertRaisesRegex(AssertionError,'source'):self.run_scope()
        self.proof['sourceProjectionIntersectionM2']=0;self.new['coarseCells'][2:]=[9,9]
        with self.assertRaisesRegex(AssertionError,'another'):self.run_scope()

    def test_rejects_ambiguous_or_non_native_child(self):
        self.parent['patches'].append(copy.deepcopy(self.child))
        with self.assertRaisesRegex(AssertionError,'ambiguous'):self.run_scope()
        self.parent['patches'].pop();self.child['nativeMesh']={}
        with self.assertRaisesRegex(AssertionError,'Native'):self.run_scope()


if __name__=='__main__':unittest.main()
