"""DRAFT source metadata guards against mutation of independently saved review."""
import copy,json,unittest
from pathlib import Path
from west_wing26195_verified_body0_candidate_certificate_draft_v2_20261012 import verify
BASE=Path(__file__).resolve().parents[3]/'docs/astra-city/government-import/government-xl-west-wing26195-body0-source-bound-grade-role-proposal-v1-20261012'
def fixture():
 r=json.loads((BASE/'ROOT-source-bound-candidate-reconciliation-v1.json').read_text());i=json.loads((BASE/'ROOT-bounded-source-interpretation-v1.json').read_text());return [copy.deepcopy(r),r,i]
class Tests(unittest.TestCase):
 def bad(self,mutate):
  x=fixture();mutate(x)
  with self.assertRaises((AssertionError,KeyError)):verify(*x)
 def test_bound_candidate_no_acceptance(self):
  r=verify(*fixture());self.assertTrue(r['body0SourceRoleCandidateQualified']);self.assertFalse(r['groundRootAccepted']);self.assertFalse(r['physicalAccepted']);self.assertTrue(r['sourceFacet154SegmentOnly'])
 def test_record_mutation(self):self.bad(lambda x:x[0].update(completeOriginalBodies=117))
 def test_wrong_source(self):self.bad(lambda x:x[2].update(sourceSHA256='other'))
 def test_wrong_reviewer(self):self.bad(lambda x:x[2].update(reviewer='another'))
 def test_missing_grade(self):self.bad(lambda x:x[2]['completeGradeFaceIds'].pop())
 def test_wrong_body_incidence(self):self.bad(lambda x:x[2]['completeBody0FaceIds'].__setitem__(0,999999))
 def test_changed_tuple(self):self.bad(lambda x:x[2]['allFourWorldBindings']['literal'].update(wholeGroundSHA256='other'))
 def test_added_engineering_function(self):self.bad(lambda x:x[2].update(engineeringFunctionClaim=True))
 def test_whole_wall154_credit(self):self.bad(lambda x:x[2].update(sourceFacet154SegmentOnly=False))
 def test_root_transfer(self):self.bad(lambda x:x[2].update(gradeRootAccepted=True))
 def test_missing_interpretation(self):self.bad(lambda x:x[2].update(actualUnchangedSourceViewsInspected=False))
 def test_legacy_backfill(self):self.bad(lambda x:x[2].update(legacyAcceptanceBackfillAllowed=True))
 def test_actual_integer_seed_keys_normalise(self):
  x=fixture()
  for r in x[0]['distinctRouteEvidence'].values():r['strictCapsBySeed']={int(k):v for k,v in r['strictCapsBySeed'].items()}
  self.assertTrue(verify(*x)['body0SourceRoleCandidateQualified'])
 def test_changed_cap_value_not_normalised_away(self):
  def mutate(x):
   r=next(iter(x[0]['distinctRouteEvidence'].values()));key=next(iter(r['strictCapsBySeed']));r['strictCapsBySeed'][key]+=1
  self.bad(mutate)
 def test_omitted_seed_not_normalised_away(self):
  def mutate(x):
   r=next(iter(x[0]['distinctRouteEvidence'].values()));r['strictCapsBySeed'].pop(next(iter(r['strictCapsBySeed'])))
  self.bad(mutate)
 def test_nonfinite_never_serialises(self):
  x=fixture();x[0]['geometryChanges']=float('nan')
  with self.assertRaises(ValueError):verify(*x)
if __name__=='__main__':unittest.main()
