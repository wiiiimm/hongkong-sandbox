import unittest,json,gzip,copy
from pathlib import Path
from aqua_exact_existing_warning_review_v1_20261014 import bind_review
ROOT=Path(__file__).resolve().parents[3];BASE=ROOT/'docs/astra-city/government-import'
class Review(unittest.TestCase):
    def setUp(self):
        self.r=json.loads((BASE/'government-xl-aqua-marine193086-facade-bottom-functional-proposal-v1-20261014/ROOT-FUNCTIONAL-SOURCE-REVIEW.json').read_text());self.p=json.load(gzip.open(BASE/'government-xl-aqua-marine193086-three-foundation-source-attribution-v1-20261014/exact-three-source-face-attribution.json.gz','rt'));self.args=dict(uid=self.r['UID'],csuid=self.r['CSUID'],source_sha=self.r['sourceSHA256'],current_manifest=self.r['currentManifestSHA256'],current_snapshot=self.r['currentSnapshot'])
    def test_actual_honest_review_schema_preserves_raw_false(self):
        x=bind_review(self.r,self.p,**self.args);self.assertFalse(x['rawStrictFoundationPassed']);self.assertFalse(x['otherFaceApplicabilityGranted']);self.assertEqual(x['rootDecisionVerbatim'],self.r)
    def test_extra_reason_or_face_rejected(self):
        for k,v in [('acceptedReasons',self.r['acceptedReasons']+['unsupported']),('exactFailedFaceIDs',[7525,7526,7527,13595])]:
            r=copy.deepcopy(self.r);r[k]=v
            with self.assertRaises(AssertionError):bind_review(r,self.p,**self.args)
    def test_context_or_strict_relabelling_rejected(self):
        for k,v in [('all278PartialFacesRetained',False),('rawStrictFoundationPassed',True),('physicalAccepted',True)]:
            r=copy.deepcopy(self.r);r[k]=v
            with self.assertRaises(AssertionError):bind_review(r,self.p,**self.args)
    def test_changed_world_binding_rejected(self):
        r=copy.deepcopy(self.r);r['worldAndGroundBindings']['completeActualGroundSHA256']='0'*64
        with self.assertRaises(AssertionError):bind_review(r,self.p,**self.args)
    def test_raw_signed_zero_bytes_cannot_be_waived(self):
        r=copy.deepcopy(self.r);p=copy.deepcopy(self.p);r['rawFoundationVerbatim']['fixtureZero']=-0.;p['rawFoundationVerbatim']['fixtureZero']=0.
        with self.assertRaises(AssertionError):bind_review(r,p,**self.args)
if __name__=='__main__':unittest.main()
