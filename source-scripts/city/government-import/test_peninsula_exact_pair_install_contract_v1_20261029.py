"""Reject forged revisions, approvals, source forms and availability declarations."""
import copy,json,unittest,gzip
from pathlib import Path
from peninsula_exact_pair_install_contract_v1_20261029 import verify
from peninsula_private_group_roof_contract_v1_20261029 import OWNER,TOWER,ROOF
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'docs/astra-city/government-import'
def read(p):
 return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
class AdmissionTests(unittest.TestCase):
 def setUp(self):
  stage=ROOT/'source-scripts/city/government-import/accepted/government-xl-peninsula-exact-original-pair-qualified-stage-v2-20261029'
  folder=BASE/'government-xl-peninsula-final-source-physical-review-v1-20261029'
  scope=read(BASE/'government-xl-peninsula-pair-current-v1-20261029-model-scope/270876:0-forms.json.gz')
  self.args=[read(stage/'catalogue.json')['models'],read(folder/'ROOT-SOURCE-REVIEW.json'),read(folder/'ROOT-PHYSICAL-REVIEW.json'),read(BASE/'government-xl-peninsula-group-roof-lifecycle-v1-20261029/summary.json'),read(BASE/'government-xl-peninsula-private-group-roof-review-v1-20261029/ROOT-PRIVATE-EXPERIMENT-REVIEW.json'),{r['building']['uid']:r['building']for r in scope}]
 def check(self):return verify(*self.args,approved=True)
 def reject(self):
  with self.assertRaises((AssertionError,KeyError)):self.check()
 def test_exact_reviewed_pair(self):self.assertTrue(self.check()['exactPairAvailabilityAndConditionalRoofVerified'])
 def test_source_revision(self):self.args[0][0]['sha256']='0'*64;self.reject()
 def test_no_duplicate_uid(self):self.args[0].append(copy.deepcopy(self.args[0][0]));self.reject()
 def test_false_review(self):self.args[1]['visualAcceptance']=False;self.reject()
 def test_unreviewed_physical(self):self.args[2]['completeNeighbourInterpretationAccepted']=False;self.reject()
 def test_missing_lifecycle(self):self.args[3]['completeAtomicPairAndRoofLifecycleVerified']=False;self.reject()
 def test_changed_manifest(self):self.args[1]['currentManifest']['sha256']='0'*64;self.reject()
 def test_changed_roof(self):self.args[5][ROOF]['height']+=1;self.reject()
 def test_changed_source_form(self):self.args[5][OWNER]['height']+=1;self.reject()
 def test_independent_activation(self):self.args[0][0]['activationGroup']=[self.args[0][0]['uid']];self.reject()
 def test_missing_support(self):next(m for m in self.args[0]if m['uid']==TOWER)['supportDependencies']=[];self.reject()
 def test_arbitrary_suppression(self):next(m for m in self.args[0]if m['uid']==OWNER)['suppressesBuildingUids'].append('way/other:0');self.reject()
 def test_unapproved_model(self):self.args[0][0]['publicationApproved']=False;self.reject()
 def test_geometry_edit_record(self):self.args[2]['sourceGeometryChanges']=1;self.reject()
 def test_no_terrain_edits(self):self.args[2]['terrainEdits']=True;self.reject()
if __name__=='__main__':unittest.main()
