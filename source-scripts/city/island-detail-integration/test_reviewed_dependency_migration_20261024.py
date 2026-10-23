"""Exercise the production atomic dependency migration, including rejected mutations."""
import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from model_dependencies import stage_dependencies


class ReviewedMigration(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.owner = dict(uid='owner',sha256='original-owner',modelId='M1',buildingCSUID='C1',publicationApproved=False,supportDependencies=[dict(uid='podium',state='surveyed-footprint-fallback')])
        self.other = dict(uid='unrelated',sha256='untouched',identityReviewApproved=False)
        self.oldurl = 'city/old.json'
        self.oldpath = self.root/'3d-viewer'/self.oldurl
        self.write(self.oldpath,dict(models=[self.owner,self.other]))
        self.write(self.root/'3d-viewer/city/new.json',dict(models=[dict(uid='podium',sha256='original-parent')]))
        self.manifest = dict(officialModelCatalogues=[self.oldurl,'city/new.json'])
        contact = self.refwrite('contact.json',dict(exactOriginalContacts=True))
        approval = self.refwrite('approval.json',dict(status='approved-for-integration'))
        self.review = dict(contactReport=contact['path'],contactReportSHA256=contact['sha256'],catalogues=[dict(source='3d-viewer/'+self.oldurl,url=self.oldurl,oldSHA256=self.sha(self.oldpath),models=['owner'])],changes=[dict(catalogue='3d-viewer/'+self.oldurl,uid='owner',modelSHA256=self.owner['sha256'],modelId='M1',buildingCSUID='C1',oldSupportDependencies=copy.deepcopy(self.owner['supportDependencies']),supportDependencies=[dict(uid='podium',state='installed',sha256='original-parent',buildingCSUID='CP')])],requiresNewNativeUids=['podium'])
        self.approval = approval

    @staticmethod
    def sha(path):
        return hashlib.sha256(path.read_bytes()).hexdigest()

    @staticmethod
    def write(path,data):
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(data)+'\n')

    def refwrite(self,name,data):
        path=self.root/name
        self.write(path,data)
        return dict(path=name,sha256=self.sha(path))

    def run_plan(self,plan=None):
        if plan is None:
            entry=dict(**self.refwrite('review.json',self.review),visualApproval=self.approval)
            plan=dict(dependencyReviews=[entry])
        edits,report={},{}
        stage_dependencies(self.root,plan,self.manifest,edits,{'podium':{}},report)
        return edits,report

    def test_only_reviewed_support_changes_and_negative_flags_remain(self):
        edits,report=self.run_plan()
        expected=copy.deepcopy(self.owner)
        expected['supportDependencies']=self.review['changes'][0]['supportDependencies']
        self.assertEqual(json.loads(edits[self.oldpath]),dict(models=[expected,self.other]))
        self.assertEqual(len(report['dependencyUpdates']),1)
        self.assertEqual(set(edits),{self.oldpath})

    def test_no_review_cannot_replace_surveyed_fallback(self):
        with self.assertRaisesRegex(AssertionError,'surveyed fallback'):
            self.run_plan({})

    def test_stale_catalogue_rejected(self):
        self.oldpath.write_text(self.oldpath.read_text()+' ')
        with self.assertRaisesRegex(AssertionError,'catalogue changed'):
            self.run_plan()

    def test_changed_owner_source_rejected(self):
        self.review['changes'][0]['modelSHA256']='different-source'
        with self.assertRaisesRegex(AssertionError,'identity changed'):
            self.run_plan()

    def test_changed_prior_support_rejected(self):
        self.review['changes'][0]['oldSupportDependencies']=[]
        with self.assertRaisesRegex(AssertionError,'metadata changed'):
            self.run_plan()

    def test_missing_parent_rejected(self):
        self.write(self.root/'3d-viewer/city/new.json',dict(models=[]))
        with self.assertRaisesRegex(AssertionError,'Missing required'):
            self.run_plan()

    def test_cyclic_migration_rejected(self):
        self.review['changes'][0]['supportDependencies']=[dict(uid='owner',state='installed')]
        with self.assertRaisesRegex(AssertionError,'Cyclic'):
            self.run_plan()

    def test_unapproved_review_rejected(self):
        self.approval=self.refwrite('approval.json',dict(status='pending'))
        with self.assertRaisesRegex(AssertionError,'visual review missing'):
            self.run_plan()

if __name__=='__main__':
    unittest.main()
