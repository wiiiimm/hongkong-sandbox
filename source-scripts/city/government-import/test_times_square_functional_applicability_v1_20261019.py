"""Reject swapped source evidence, omitted modes and silently cleared raw failures."""
import copy,unittest
from times_square_functional_applicability_v1_20261019 import inputs,qualify,T1
class ApplicabilityTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.evidence=inputs()
 def test_exact_evidence_preserves_raw_failures(self):
  r=qualify(**copy.deepcopy(self.evidence));self.assertTrue(r['sourceScopedApplicabilityAccepted']);self.assertFalse(r['strictInterfacePassed']);self.assertFalse(r['installationApproved'])
 def test_invalid_evidence_rejected(self):
  mutations=[lambda x:x['binding']['bindings'].pop(),lambda x:x['binding']['bindings'][0].update(sourceSHA256='0'*64),lambda x:x['physical']['rows'][0]['remainingPolicyReasons'].append('unexpected-identity'),lambda x:x['contexts'][T1]['incidentFaces'][0].update(normal=[0,1,0]),lambda x:x['attributions']['original']['terrainOnlyFoundation'].update(fullyBuriedTriangles=1),lambda x:x['overlap']['checks'][0].update(rawCompoundBuried=0),lambda x:next(r for r in x['physical']['rows']if r['uid']==T1)['rawStrictSupport'].update(passed=True),lambda x:x['facade']['rows'][0].update(sourceSHA256='f'*64)]
  for i,mutate in enumerate(mutations):
   with self.subTest(case=i):
    x=copy.deepcopy(self.evidence);mutate(x)
    with self.assertRaises(AssertionError):qualify(**x)
if __name__=='__main__':unittest.main()
