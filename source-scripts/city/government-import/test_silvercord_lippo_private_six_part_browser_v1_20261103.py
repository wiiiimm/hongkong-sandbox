import copy
import unittest
from silvercord_lippo_private_six_part_browser_v1_20261103 import diagnostic_catalogue, exact_owner_after


class PrivateProposalGuards(unittest.TestCase):
    def setUp(self):
        self.sources = {str(i): 'sha'+str(i) for i in range(5)}
        self.catalogue = dict(models=[dict(uid=u, sha256=h, activationGroup=sorted(self.sources),
            proceduralWindows=False, publicationApproved=False, placementReviewed=False,
            identityReviewApproved=False, sourceIdentityReviewed=False, priority='unreviewed',
            supportDependencies=[], transform=[1,0,0]) for u,h in self.sources.items()])

    def test_priority_only_copy(self):
        before = copy.deepcopy(self.catalogue)
        result = diagnostic_catalogue(self.catalogue, self.sources)
        self.assertEqual(self.catalogue, before)
        expected = copy.deepcopy(before)
        for model in expected['models']:
            model['priority'] = 'landmark'
        self.assertEqual(result, expected)

    def test_missing_atomic_member_or_approval_rejected(self):
        for field, value in [('activationGroup', ['0']), ('publicationApproved', True),
                             ('placementReviewed', True), ('proceduralWindows', True)]:
            changed = copy.deepcopy(self.catalogue)
            changed['models'][0][field] = value
            with self.assertRaises(AssertionError):
                diagnostic_catalogue(changed, self.sources)

    def test_wrong_dependency_or_source_rejected(self):
        for dep in [dict(uid='missing',sha256='sha0',state='candidate'),
                    dict(uid='0',sha256='wrong',state='candidate'),
                    dict(uid='0',sha256='sha0',state='installed')]:
            changed = copy.deepcopy(self.catalogue)
            changed['models'][1]['supportDependencies'] = [dep]
            with self.assertRaises(AssertionError):
                diagnostic_catalogue(changed, self.sources)
        with self.assertRaises(AssertionError):
            diagnostic_catalogue(self.catalogue, {**self.sources,'0':'wrong'})

    def test_owner_update_cannot_change_pose_flags_or_unrelated_entry(self):
        owner = dict(uid='owner',sha256='original',supportDependencies=[],transform=[1,0,0],publicationApproved=True)
        before = dict(models=[owner,dict(uid='other',sha256='other')])
        after = copy.deepcopy(before)
        after['models'][0]['supportDependencies'] = [dict(uid='0',sha256='sha0',state='installed')]
        update = dict(ownerUid='owner',ownerSHA256='original',beforeEntry=owner,
                      afterEntry=copy.deepcopy(after['models'][0]),changedFields=['supportDependencies'])
        self.assertTrue(exact_owner_after(before,after,update))
        for field,value in [('transform',[2,0,0]),('publicationApproved',False),('sha256','replacement')]:
            bad = copy.deepcopy(after)
            bad['models'][0][field] = value
            forged = {**update,'afterEntry':bad['models'][0]}
            with self.assertRaises(AssertionError):
                exact_owner_after(before,bad,forged)
        bad = copy.deepcopy(after)
        bad['models'][1]['sha256'] = 'replacement'
        with self.assertRaises(AssertionError):
            exact_owner_after(before,bad,update)


if __name__ == '__main__':
    unittest.main()
