import copy,hashlib,json,unittest,numpy as np
from original_multi_actor_support_graph_20261009 import verify

class MultiActorSupportTests(unittest.TestCase):
    def fixture(self):
        tri=np.asarray([[[0,0,0],[1,0,0],[0,0,1]],[[0,0,0],[1,0,0],[0,1,0]]],float)
        actors=[dict(uid=str(i),sourceSHA256='source'+str(i),originalStreamBindingSHA256='stream'+str(i),globalFaceRange=[i,i+1],completeOriginalFaceCount=1,originalWorldTrianglesSHA256=hashlib.sha256(tri[i:i+1].tobytes()).hexdigest()) for i in range(2)]
        components=[dict(actorUID=str(i),globalOriginalFaces=[i]) for i in range(2)]
        ground=[dict(passed=True,samples=3,strictContacts=3,unresolved=[],wallIntersections=0,strictLowRim=dict(samples=3,contacts=3,failed=[],missing=0,minimumGap=-.1,maximumGap=1,minGap=0,maxGap=0)),dict(passed=False)]
        contact=[dict(components=[0,1],globalOriginalFaces=[0,1])]
        return tri,actors,components,ground,contact
    def run_fixture(self,fixture,changed=None):
        tri,actors,components,ground,contacts=fixture
        binding=dict(completeOriginalWorldTrianglesSHA256=hashlib.sha256(tri.tobytes()).hexdigest(),currentDrawnGroundSHA256='ground',groundInterfacesInputSHA256='pinned-actual-ground-only-compute',supportScope='complete-current-drawn-ground-only',groundInterfacesSHA256=hashlib.sha256(json.dumps(ground,sort_keys=True,separators=(',',':')).encode()).hexdigest())
        return verify(*fixture,expected_binding=binding,current_binding=changed or binding)
    def test_complete_original_cross_actor_contact(self):
        r=self.run_fixture(self.fixture());self.assertTrue(r['supportInterfaceAccepted']);self.assertEqual(r['resolvedOriginalComponents'],[0,1]);self.assertFalse(r['fullAcceptance'])
    def test_source_omission_rejected(self):
        f=list(self.fixture());f[1]=f[1][:1]
        with self.assertRaises(AssertionError):self.run_fixture(f)
    def test_component_omission_rejected(self):
        f=list(self.fixture());f[2]=f[2][:1];f[3]=f[3][:1];f[4]=[]
        with self.assertRaises(AssertionError):self.run_fixture(f)
    def test_wrong_actor_component_rejected(self):
        f=self.fixture();f[2][1]['actorUID']='0'
        with self.assertRaises(AssertionError):self.run_fixture(f)
    def test_vertex_kiss_rejected(self):
        f=list(self.fixture());f[0][1]=[[0,0,0],[-1,0,0],[0,1,-1]];f[1][1]['originalWorldTrianglesSHA256']=hashlib.sha256(f[0][1:2].tobytes()).hexdigest()
        with self.assertRaises(AssertionError):self.run_fixture(f)
    def test_tiny_real_separation_rejected(self):
        f=list(self.fixture());f[0][1,:,1]+=1e-12;f[1][1]['originalWorldTrianglesSHA256']=hashlib.sha256(f[0][1:2].tobytes()).hexdigest()
        with self.assertRaises(AssertionError):self.run_fixture(f)
    def test_contact_without_ground_cannot_root_cycle(self):
        f=self.fixture();f[3][0]['passed']=False;self.assertFalse(self.run_fixture(f)['supportInterfaceAccepted'])
    def test_favourable_boolean_with_failed_contacts_rejected(self):
        f=self.fixture();f[3][0]['strictContacts']=2
        with self.assertRaises(AssertionError):self.run_fixture(f)
    def test_missing_ground_rejected(self):
        f=self.fixture();f[3][0]['strictLowRim']['missing']=1
        with self.assertRaises(AssertionError):self.run_fixture(f)
    def test_higher_other_actor_is_not_ground_anchor(self):
        with self.assertRaises(AssertionError):self.run_fixture(self.fixture(),dict(supportScope='combined-source-roofs'))
    def test_stale_ground_rejected(self):
        f=self.fixture();binding=dict(completeOriginalWorldTrianglesSHA256='stale')
        with self.assertRaises(AssertionError):self.run_fixture(f,binding)
    def test_repeated_actor_faces_rejected(self):
        f=self.fixture();f[1][1]['globalFaceRange']=[0,1];f[1][1]['originalWorldTrianglesSHA256']=f[1][0]['originalWorldTrianglesSHA256']
        with self.assertRaises(AssertionError):self.run_fixture(f)
    def test_contact_wrong_component_face_rejected(self):
        f=self.fixture();f[4][0]['globalOriginalFaces']=[1,0]
        with self.assertRaises(AssertionError):self.run_fixture(f)

if __name__=='__main__':unittest.main()
