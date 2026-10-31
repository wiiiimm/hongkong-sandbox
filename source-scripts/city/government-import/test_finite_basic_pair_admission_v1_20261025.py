"""Real frozen pair evidence exercises admission refusals without database writes."""
import copy
import unittest
from unittest.mock import patch
import finite_basic_pair_admission_v1_20261025 as admission
BASE = admission.BASE
CONFIG = admission.read(BASE/'government-xl-beverly-fe-finite-original-install-config-v1-20261025.json')
REVIEW = admission.read(BASE/CONFIG['review']/'ROOT-PHYSICAL-REVIEW.json')
ORIGINAL_READ = admission.read

def local_receipt(folder):
    result = ORIGINAL_READ(folder/'result.json')
    return result,{r['path']:r['sha256'] for r in result['evidenceRefs']}

class PairAdmission(unittest.TestCase):
    def run_profile(self, *, config=None, review=None, change=None):
        def read(path):
            result = ORIGINAL_READ(path)
            return change(path,result) if change else result
        with patch.object(admission,'authenticate',side_effect=local_receipt),patch.object(admission,'read',side_effect=read):
            return admission.replay(config or copy.deepcopy(CONFIG),review or copy.deepcopy(REVIEW))
    def test_exact_pair_and_actual_dependency_failure_pass(self):
        self.assertTrue(self.run_profile())
    def test_canonical_failure_cannot_be_renamed_pass(self):
        review=copy.deepcopy(REVIEW);review['completeFourWorldCanonicalRetainedBasicSupport']=True
        with self.assertRaises(AssertionError):self.run_profile(review=review)
    def test_missing_neighbour_replacement_dependency_rejected(self):
        config=copy.deepcopy(CONFIG);config['replacementDependenciesByUid']={}
        with self.assertRaises(AssertionError):self.run_profile(config=config)
    def test_exact_pair_review_is_required(self):
        review=copy.deepcopy(REVIEW);review['acceptedExactOriginalPair']=False
        with self.assertRaises(AssertionError):self.run_profile(review=review)
    def test_missing_source_coordinate_mode_rejected(self):
        def change(path,data):
            if str(path).endswith('mode-inputs.json.gz'):data['rows'][0]['modes'].pop()
            return data
        with self.assertRaises(AssertionError):self.run_profile(change=change)
    def test_omitted_pair_faces_rejected(self):
        def change(path,data):
            if path.parent.name==CONFIG['pairContacts'] and path.name=='original.json.gz':data['sourceFacesOmitted']=1
            return data
        with self.assertRaises(AssertionError):self.run_profile(change=change)
    def test_nonempty_or_unproven_native_context_rejected(self):
        def change(path,data):
            if path.parent.name==CONFIG['emptyNative'] and path.name=='summary.json':data['emptyNativeContactSetProved']=False
            return data
        with self.assertRaises(AssertionError):self.run_profile(change=change)
    def test_missing_podium_lifetime_binding_rejected(self):
        review=copy.deepcopy(REVIEW);review['retainedBasicSupportDependencies'].pop()
        with self.assertRaises(AssertionError):self.run_profile(review=review)
    def test_failed_neighbour_must_leave_dependent_basic_visible(self):
        for key,value in [('active',True),('ownFeaturePresent',False),('basicHidden',True)]:
            def change(path,data):
                if str(path).endswith('/390/staged-browser.json'):data['candidateDependencyFallbacks'][0][key]=value
                return data
            with self.subTest(key=key),self.assertRaises(AssertionError):self.run_profile(change=change)
    def test_changed_source_binding_rejected(self):
        review=copy.deepcopy(REVIEW);review['sourceSHA256ByUid']['landsd/256334:0']='0'*64
        with self.assertRaises(AssertionError):self.run_profile(review=review)
if __name__=='__main__':unittest.main()
