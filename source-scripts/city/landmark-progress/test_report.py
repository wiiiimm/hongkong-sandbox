import hashlib, pathlib, tempfile, unittest
from report import review_status, source_status

class ReadinessTests(unittest.TestCase):
    def test_checked_absence_is_not_outstanding_download(self):
        part={'uid':'x','state':'not-in-retained-staged-models'}
        self.assertEqual(source_status(part,set(),{'x':{'outcome':'no-exact-model-in-complete-checked-sheets'}}),'exact-source-absent-in-checked-sheets')
        self.assertEqual(source_status(part,set(),{}),'acquisition-pending')
        self.assertEqual(source_status(part,set(),{'x':{'outcome':'acquired-and-staged','standardMatch':False}}),'acquired-match-review')
        self.assertEqual(source_status(part,set(),{'x':{'outcome':'acquired-and-staged','standardMatch':True}}),'acquired-preparation-pending')
    def test_current_prepared_and_installed_override_old_source_gap(self):
        old={'x':{'outcome':'no-exact-model-in-complete-checked-sheets'}}
        self.assertEqual(source_status({'uid':'x','state':'candidate-staged'},set(),old),'prepared-for-review')
        self.assertEqual(source_status({'uid':'x'}, {'x'},old),'installed')
    def test_parts_or_cache_alone_never_certify_landmark(self):
        self.assertEqual(review_status(None,{'x'},{'x'},pathlib.Path('.')),'not-reviewed')
    def test_whole_landmark_needs_matching_membership_and_current_evidence(self):
        with tempfile.TemporaryDirectory() as folder:
            root=pathlib.Path(folder);(root/'evidence.json').write_text('verified')
            record=dict(identityReviewed=True,componentMembershipComplete=True,sourceUids=['x'],
                        checks={k:True for k in ['appearance','placement','picking','collision','viewerLoading']},
                        evidence={'evidence.json':hashlib.sha256(b'verified').hexdigest()},blockingGaps=[])
            self.assertEqual(review_status(record,{'x'},{'x'},root),'ready-for-review')
            self.assertEqual(review_status(record,{'x','y'},{'x','y'},root),'component-set-changed')
            self.assertEqual(review_status(record,{'x'},set(),root),'models-not-installed')
            record['blockingGaps']=['missing podium'];self.assertEqual(review_status(record,{'x'},{'x'},root),'evidence-or-gap-pending')
            record['blockingGaps']=[];(root/'evidence.json').write_text('changed')
            self.assertEqual(review_status(record,{'x'},{'x'},root),'evidence-changed')
    def test_partial_checks_are_not_acceptance(self):
        r=dict(identityReviewed=True,componentMembershipComplete=True,sourceUids=['x'],checks={'appearance':True})
        self.assertEqual(review_status(r,{'x'},{'x'},pathlib.Path('.')),'checks-incomplete')
if __name__=='__main__':unittest.main()
