"""Reject changed identities, omitted warnings, and weakened foundation evidence."""
import copy, unittest
import olympian_one_functional_applicability_v1_20261018 as a
class ScopeTests(unittest.TestCase):
 def setUp(self):
  self.inputs=[a.read(a.folder('source-review-v1')/'ROOT-SOURCE-INTERPRETATION.json'),a.read(a.folder('wall-binding-v1')/'exact-source-face-bindings.json.gz'),[a.read(p)for p in a.folder('pair-physical-v2').glob('*-foundation.json')],a.read(a.folder('global-bottom-resolution-v1')/'summary.json')['remainingReasons']]
 def test_exact_accepted_and_raw_failures_retained(self):
  result=a.apply(*self.inputs)
  self.assertFalse(result['strictInterfacePassed']);self.assertEqual(result['rawStrictInterfaceVerbatim'],self.inputs[0]['rawStrictInterfaceVerbatim']);self.assertFalse(result['installationApproved'])
 def test_reject_scope_changes(self):
  def source(x):x[0]['sourceBindings'][0]['sourceSHA256']='0'*64
  def csuid(x):x[1]['bindings'][0]['buildingCSUID']='foreign'
  def face(x):x[1]['descriptors'][0]['faces'][0]['originalFaceID']=0
  def world(x):x[2][0]['worldSHA256']='0'*64
  def foundation(x):x[2][0]['strictFoundationAccepted']=False
  def uncovered(x):x[2][0]['foundation']['completeTerrainTriangles']-=1
  def warning(x):x[3].append('unreviewed-foreign-regression')
  def missing(x):x[3].pop()
  def relabel(x):x[0]['rawStrictInterfaceVerbatim']['passed']=True
  def unsupported(x):x[0]['independentSupportFor47SamplesProved']=True
  for mutation in [source,csuid,face,world,foundation,uncovered,warning,missing,relabel,unsupported]:
   with self.subTest(mutation=mutation.__name__):
    inputs=copy.deepcopy(self.inputs);mutation(inputs)
    with self.assertRaises(AssertionError):a.apply(*inputs)
if __name__=='__main__':unittest.main()
