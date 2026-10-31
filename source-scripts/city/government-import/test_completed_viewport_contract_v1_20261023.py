import copy,unittest
from completed_viewport_contract_v1_20261023 import validate_completed,unchanged_render_config

class WholeViewportTests(unittest.TestCase):
    def setUp(self):
        self.sources={'source':{'sha256':'original','triangles':5}};self.retained={'old':{'sha256':'old-bytes','triangles':12}}
        source=dict(uid='source',width=1280,sourceSHA256='original',originalTriangles=5,meshVisibility=[True],wireframeFlags=[False],active=True,visible=True,fullyFramed=True,solidAppearance=True,fallbackFaces=0,pick='source',collision='source')
        old=dict(uid='old',width=1280,sourceSHA256='old-bytes',originalTriangles=12,active=True,visible=True,fullyFramed=True,fallbackFaces=0,meshVisibility=[True],wireframeFlags=[False])
        self.report=dict(passed=True,errors=[],views=[dict(source,time=t)for t in ['15:00','22:00']],retainedNativeOwnViews=[dict(old,time=t)for t in ['15:00','22:00']],jointViews=[{'models':[dict(source)]}])
    def test_complete_viewport(self):self.assertTrue(validate_completed(self.report,1280,self.sources,self.retained))
    def test_partial_error_never_accepted(self):
        r=copy.deepcopy(self.report);r['errors']=['activation timed out']
        with self.assertRaises(AssertionError):validate_completed(r,1280,self.sources,self.retained)
    def test_missing_retained_case(self):
        r=copy.deepcopy(self.report);r['retainedNativeOwnViews'].pop()
        with self.assertRaises(AssertionError):validate_completed(r,1280,self.sources,self.retained)
    def test_changed_retained_source(self):
        r=copy.deepcopy(self.report);r['retainedNativeOwnViews'][0]['sourceSHA256']='changed'
        with self.assertRaises(AssertionError):validate_completed(r,1280,self.sources,self.retained)
    def test_source_fallback_rejected(self):
        r=copy.deepcopy(self.report);r['views'][0]['fallbackFaces']=12
        with self.assertRaises(AssertionError):validate_completed(r,1280,self.sources,self.retained)
    def test_source_triangle_loss_rejected(self):
        r=copy.deepcopy(self.report);r['views'][0]['originalTriangles']=4
        with self.assertRaises(AssertionError):validate_completed(r,1280,self.sources,self.retained)
    def test_hidden_source_mesh_rejected(self):
        r=copy.deepcopy(self.report);r['views'][0]['meshVisibility']=[False]
        with self.assertRaises(AssertionError):validate_completed(r,1280,self.sources,self.retained)
    def test_duplicate_source_time_rejected(self):
        r=copy.deepcopy(self.report);r['views'][1]['time']='15:00'
        with self.assertRaises(AssertionError):validate_completed(r,1280,self.sources,self.retained)
    def test_mobile_needs_failure_recovery(self):
        r=copy.deepcopy(self.report)
        for row in r['views']+r['retainedNativeOwnViews']:row['width']=390
        with self.assertRaises(AssertionError):validate_completed(r,390,self.sources,self.retained)
    def test_output_folder_may_change(self):unchanged_render_config({'doc':'old','stage':'source','terrain':[1]},{'doc':'new','stage':'source','terrain':[1]})
    def test_render_input_change_rejected(self):
        with self.assertRaises(AssertionError):unchanged_render_config({'doc':'old','stage':'source'},{'doc':'new','stage':'different'})
    def test_retained_only_shortcut_rejected(self):
        with self.assertRaises(AssertionError):unchanged_render_config({'retainedOnly':True},{'retainedOnly':True})

if __name__=='__main__':unittest.main()
