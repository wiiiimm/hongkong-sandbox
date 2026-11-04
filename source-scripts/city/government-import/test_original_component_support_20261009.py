import unittest
import original_component_support_20261009 as module

class OriginalComponentSupportTests(unittest.TestCase):
    def fixture(self):
        tri=[[[0,0,0],[2,0,0],[0,0,2]],[[0,0,0],[2,0,0],[0,3,0]]]
        anchor={'passed':True,'samples':3,'strictContacts':3,'wallIntersections':0,'unresolved':[],
            'strictLowRim':{'samples':3,'contacts':3,'missing':0,'failed':[],
                'minimumGap':-.1,'maximumGap':1,'minGap':0,'maxGap':0}}
        return tri,[[0],[1]],[anchor,{'passed':False}],[{'component':1,'anchorComponent':0,'sourceFace':1,'anchorFace':0}]
    def test_attached_original_keeps_all_faces(self):
        r=module.verify(*self.fixture());self.assertTrue(r['supportInterfaceAccepted'])
        self.assertEqual(r['sourceFaces'],2);self.assertFalse(r['fullAcceptance'])
    def test_shifted_appendage_is_unresolved(self):
        a,b,c,d=self.fixture();a[1]=[[x,y+1,z] for x,y,z in a[1]]
        self.assertFalse(module.verify(a,b,c,d)['supportInterfaceAccepted'])
    def test_point_contact_is_not_attachment(self):
        a,b,c,d=self.fixture();a[1]=[[0,0,0],[-2,0,0],[0,3,0]]
        self.assertFalse(module.verify(a,b,c,d)['supportInterfaceAccepted'])
    def test_anchor_boolean_cannot_hide_bad_support(self):
        a,b,c,d=self.fixture();c[0]['strictLowRim']['failed']=[{'reason':'no-vertical-support'}]
        with self.assertRaises(AssertionError):module.verify(a,b,c,d)
    def test_missing_and_duplicate_faces_reject(self):
        a,b,c,d=self.fixture()
        for partition in [[[0],[]],[[0],[0,1]]]:
            with self.assertRaises(AssertionError):module.verify(a,partition,c,d)
    def test_false_component_ownership_rejects(self):
        a,b,c,d=self.fixture();d[0]['sourceFace']=0
        with self.assertRaises(AssertionError):module.verify(a,b,c,d)
    def test_disconnected_partition_rejects(self):
        a,b,c,d=self.fixture();a.append([[10,0,0],[12,0,0],[10,0,2]]);b[0].append(2)
        with self.assertRaises(AssertionError):module.verify(a,b,c,d)
    def test_floating_anchor_cannot_support_other_parts(self):
        a,b,c,d=self.fixture();c[0]['strictLowRim'].update(minGap=.5,maxGap=.6)
        with self.assertRaises(AssertionError):module.verify(a,b,c,d)
    def test_failed_anchor_cannot_support_other_parts(self):
        a,b,c,d=self.fixture();c[0]['passed']=False
        with self.assertRaises(AssertionError):module.verify(a,b,c,d)

if __name__=='__main__':unittest.main()
