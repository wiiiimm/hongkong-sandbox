import unittest,copy,json,gzip
from pathlib import Path
from aqua_original_private_stage_guard_v1_20261014 import qualify
from aqua_exact_existing_warning_review_v1_20261014 import bind_review
ROOT=Path(__file__).resolve().parents[3];B=ROOT/'docs/astra-city/government-import'
def read(p):return json.load(gzip.open(p,'rt'))if str(p).endswith('.gz')else json.loads(p.read_text())
class Guard(unittest.TestCase):
    def setUp(self):
        self.uid='landsd/193086:0';self.foreign='landsd/138449:0';self.p=read(B/'government-xl-aqua-marine193086-three-foundation-source-attribution-v1-20261014/exact-three-source-face-attribution.json.gz');self.d=read(B/'government-xl-aqua-marine193086-unchanged-current-ordinary-physical-v3-20261014/diagnostic.json.gz');self.f=read(B/'government-xl-aqua-marine193086138449-saved-four-world-guards-v2-20261014/complete-four-world-guard-result.json');self.i=read(B/'government-xl-aqua-marine-current-bound-overhead-promotion-v3-20261010/identity.json');r=read(B/'government-xl-aqua-marine193086-facade-bottom-functional-proposal-v1-20261014/ROOT-FUNCTIONAL-SOURCE-REVIEW.json');self.a=bind_review(r,self.p,uid=self.uid,csuid=r['CSUID'],source_sha=r['sourceSHA256'],current_manifest=r['currentManifestSHA256'],current_snapshot=r['currentSnapshot'])
    def call(self):return qualify(self.d,self.f,self.p,self.i,self.a,self.uid,self.foreign)
    def test_actual_metadata_preserves_strict_false_and_foreign(self):
        x=self.call();self.assertFalse(x['rawStrictFoundationPassed']);self.assertFalse(x['independentForeignCollisionExemption']);self.assertEqual(len(x['all278PartialFaceIDsVerbatim']),278);self.assertFalse(x['physicalFinalAccepted'])
    def test_new_reason_or_runtime_concern_rejected(self):
        for changed in ['reason','runtime']:
            d=copy.deepcopy(self.d)
            if changed=='reason':d['ordinaryNumericReasons'].append('unsupported')
            else:d['rawRuntimeConcerns'][0]['concerns'].append('unsupported')
            with self.assertRaises(AssertionError):qualify(d,self.f,self.p,self.i,self.a,self.uid,self.foreign)
    def test_missing_world_or_uncovered_face_rejected(self):
        for changed in ['world','coverage']:
            f=copy.deepcopy(self.f)
            if changed=='world':f['rows'].pop()
            else:next(r for r in f['rows']if r['uid']==self.uid)['rawProjectionUncoveredFaceIDs']=[1]
            with self.assertRaises(AssertionError):qualify(self.d,f,self.p,self.i,self.a,self.uid,self.foreign)
    def test_new_below_grade_or_foreign_contact_rejected(self):
        for changed in ['below','contact']:
            f=copy.deepcopy(self.f)
            if changed=='below':next(r for r in f['rows']if r['uid']==self.uid)['ownedRawBelowGradeIDsOutsideSaved281']=[1]
            else:f['foreignCollisionRows'][0]['contactCount']=1
            with self.assertRaises(AssertionError):qualify(self.d,f,self.p,self.i,self.a,self.uid,self.foreign)
    def test_identity_exemption_rejected(self):
        i=copy.deepcopy(self.i);i['foreignCollisionExemption']=True
        with self.assertRaises(AssertionError):qualify(self.d,self.f,self.p,i,self.a,self.uid,self.foreign)
if __name__=='__main__':unittest.main()
