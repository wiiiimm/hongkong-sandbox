import copy,unittest,symtable,builtins,json
from pathlib import Path
from upton_staged_image_review_binding_v1_20261014 import validate_review,inventory_delta
HERE=Path(__file__).parent

def fixture():
    images=[dict(path='staged/image-'+str(i)+'.png',sha256=str(i).zfill(64))for i in range(12)]
    x=dict(job='j',report_ref=dict(path='report',sha256='r'),stage_ref=dict(path='stage',sha256='s'),functional_ref=dict(path='functional',sha256='f'),manifest_sha='m',image_refs=images)
    r=dict(reviewer='Codex ROOT',stagedExportsAccepted=True,stagedJobId='j',stagedBrowser=x['report_ref'],sourceStage=x['stage_ref'],acceptedFunctionalReview=x['functional_ref'],currentManifestSHA256='m',all12ExportedImagesInspected=True,strictOriginalInterfacePassed=False,imagesActuallyInspected=images)
    return copy.deepcopy(r),copy.deepcopy(x)
class Tests(unittest.TestCase):
    def test_exact_review_acceptance_preserves_strict_false(self):
        r,x=fixture();before=copy.deepcopy(r);a=validate_review(r,**x);self.assertTrue(a['stagedImageReviewAccepted']);self.assertFalse(a['strictInterfacePassed']);self.assertEqual(r,before)
    def test_boolean_without_bound_review_cannot_authorize(self):
        with self.assertRaises((KeyError,TypeError)):validate_review(True,**fixture()[1])
        r,x=fixture();r.pop('imagesActuallyInspected')
        with self.assertRaises(KeyError):validate_review(r,**x)
    def test_changed_png_duplicate_missing_or_changed_job_manifest_source_fails(self):
        for key in ['png','duplicate','missing','stagedJobId','currentManifestSHA256','sourceStage','acceptedFunctionalReview','strictOriginalInterfacePassed','stagedExportsAccepted']:
            r,x=fixture()
            if key=='png':r['imagesActuallyInspected'][0]['sha256']='changed'
            elif key=='duplicate':r['imagesActuallyInspected'][0]=r['imagesActuallyInspected'][1]
            elif key=='missing':r['imagesActuallyInspected'].pop()
            elif key in ['strictOriginalInterfacePassed','stagedExportsAccepted']:r[key]=not r[key]
            else:r[key]='changed'
            with self.assertRaises(AssertionError):validate_review(r,**x)
    def test_actual_fixed521_counts_two_models_only_one_XL(self):
        root=HERE.parents[2];p=json.loads((root/'docs/astra-city/government-import/government-xl-nam-fung79099-unchanged-installed-v1-20261013/full-xl-current-count.json').read_text());m=json.loads((HERE/'accepted/government-xl-upton-joint-original-functional-private-stage-v1-20261014/catalogue.json').read_text())['models'];r=inventory_delta(p,m,manifest_sha=p['manifestSHA256'],snapshot=p['snapshotId']);self.assertEqual(r['returnedModels'],2);self.assertEqual(r['newFixedXLUids'],['landsd/338946:0']);self.assertEqual(r['expectedFixedXLDelta'],1);self.assertEqual(r['previousInstalled'],234)
    def test_changed_count_source_or_current_binding_fails(self):
        rows=[dict(uid='u'+str(i),sourceKey='source'+str(i),indexedSourceSHA256='s',installedVerified=False)for i in range(521)];p=dict(rows=rows,counts=dict(total=521,installedVerified=0),manifestSHA256='m',snapshotId='n');m=[dict(uid='u0',sha256='s')]
        for key in ['manifest','source','count','duplicate']:
            q=copy.deepcopy(p)
            if key=='manifest':q['manifestSHA256']='changed'
            elif key=='source':q['rows'][0]['indexedSourceSHA256']='changed'
            elif key=='count':q['counts']['installedVerified']=1
            else:q['rows'][1]=q['rows'][0]
            with self.assertRaises(AssertionError):inventory_delta(q,m,manifest_sha='m',snapshot='n')
    def test_live_runner_global_bindings(self):
        f=HERE/'upton_joint_original_functional_publication_v2_20261014.py';t=symtable.symtable(f.read_text(),str(f),'exec');bound={s.get_name()for s in t.get_symbols()if s.is_imported()or s.is_assigned()}|set(dir(builtins))|{'__file__','__name__'}
        def visit(tree):
            for s in tree.get_symbols():
                if s.is_referenced()and s.is_global():self.assertIn(s.get_name(),bound)
            for child in tree.get_children():visit(child)
        visit(t)
if __name__=='__main__':unittest.main()
