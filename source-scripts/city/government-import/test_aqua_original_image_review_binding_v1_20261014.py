import unittest,copy
from aqua_original_image_review_binding_v1_20261014 import validate_review,inventory_delta
class Images(unittest.TestCase):
    def setUp(self):
        self.q=lambda n:dict(path=n,sha256='1'*64);self.images=[self.q('image'+str(i))for i in range(4)];self.args=dict(job='job',report_ref=self.q('report'),stage_ref=self.q('stage'),functional_ref=self.q('functional'),manifest_sha='2'*64,image_refs=self.images);self.review=dict(reviewer='Codex ROOT',stagedExportsAccepted=True,stagedJobId='job',stagedBrowser=self.args['report_ref'],sourceStage=self.args['stage_ref'],acceptedFunctionalReview=self.args['functional_ref'],currentManifestSHA256='2'*64,all4ExportedImagesInspected=True,rawStrictFoundationPassed=False,imagesActuallyInspected=self.images,ownedUID='landsd/193086:0',sourceSHA256='d24d090ed2711744be1b4cd326da724a2a17baa5368720c8ac12e7bd42823b91')
    def test_exact_bound_review(self):self.assertTrue(validate_review(self.review,**self.args)['stagedImageReviewAccepted'])
    def test_cli_boolean_missing_images_cannot_approve(self):
        r=copy.deepcopy(self.review);r['imagesActuallyInspected']=[]
        with self.assertRaises(AssertionError):validate_review(r,**self.args)
    def test_changed_stage_source_hash_or_strict_label_rejected(self):
        for k,v in [('sourceStage',self.q('other')),('sourceSHA256','0'*64),('rawStrictFoundationPassed',True)]:
            r=copy.deepcopy(self.review);r[k]=v
            with self.assertRaises(AssertionError):validate_review(r,**self.args)
    def test_duplicate_or_changed_image_rejected(self):
        for images in [self.images[:3]+[self.images[0]],[{**self.images[0],'sha256':'0'*64}]+self.images[1:]]:
            r=copy.deepcopy(self.review);r['imagesActuallyInspected']=images
            with self.assertRaises(AssertionError):validate_review(r,**self.args)
    def test_fixed521_owned_membership_exact_delta(self):
        rows=[dict(sourceKey=str(i),uid=None,indexedSourceSHA256=None,installedVerified=False)for i in range(521)];rows[0].update(uid='landsd/193086:0',indexedSourceSHA256=self.review['sourceSHA256']);p=dict(manifestSHA256='m',snapshotId='s',rows=rows,counts=dict(total=521,installedVerified=0));d=inventory_delta(p,[dict(uid='landsd/193086:0',sha256=self.review['sourceSHA256'])],manifest_sha='m',snapshot='s');self.assertEqual(d['expectedFixedXLDelta'],1);rows[0]['indexedSourceSHA256']='0'*64
        with self.assertRaises(AssertionError):inventory_delta(p,[dict(uid='landsd/193086:0',sha256=self.review['sourceSHA256'])],manifest_sha='m',snapshot='s')
if __name__=='__main__':unittest.main()
