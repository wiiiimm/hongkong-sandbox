import copy,builtins,symtable,unittest
from pathlib import Path
import aqua_marine193086_current_ordinary_physical_v2_20261014 as a

def inputs():
    row=a.read(a.INPUT/'selection.json.gz')['rows'][0];context=a.read(a.INPUT/'context.json.gz')['rows'][0];forms=a.read(a.INPUT/'current-inputs.json.gz')['forms'];pins=a.read(a.INPUT/'complete-original-stream-pins.json.gz');saved=a.read(a.IDENTITY/'identity.json')
    return dict(saved=saved,original_row=row,current_row=copy.deepcopy(row),old_context=context,current_context=copy.deepcopy(context),old_forms=forms,current_forms=copy.deepcopy(forms),old_pins=pins,current_pins=copy.deepcopy(pins))
class Tests(unittest.TestCase):
    def test_actual_saved_complete_tuple_reuses_verbatim_only(self):
        x=inputs();before=copy.deepcopy(x);r=a.reuse_identity(**x);self.assertEqual(r['savedIdentityVerbatim'],x['saved']);self.assertTrue(r['noOldKernelHashRelabel']);self.assertTrue(r['noPhysicalOrSupportCredit']);self.assertEqual(x,before)
    def test_changed_form_source_pose_stream_tile_rejected(self):
        for kind in ['form','source','pose','stream','tile']:
            x=inputs()
            if kind=='form':x['current_forms'][0]['base']+=1
            elif kind=='source':x['current_row']['sourceSHA256']='0'*64
            elif kind=='pose':x['current_row']['candidate']['entry']['worldBounds'][0][0]+=1
            elif kind=='stream':x['current_pins']['own']['allBufferViews'][0]['sha256']='0'*64
            else:x['current_context']['neighbourTileHashes']['city/data/tiles/-1_-3.json']='0'*64
            with self.assertRaises(AssertionError):a.reuse_identity(**x)
    def test_missing_or_added_current_actor_rejected(self):
        for addition in [True,False]:
            x=inputs()
            if addition:x['current_forms'].append(copy.deepcopy(x['current_forms'][0]))
            else:x['current_forms'].pop()
            with self.assertRaises(AssertionError):a.reuse_identity(**x)
    def test_equal_numeric_values_different_zero_or_type_rejected(self):
        for value in [-0.0,False]:
            x=inputs();x['old_context']['fixtureNumericIdentity']=0.0 if type(value)is float else 0;x['current_context']['fixtureNumericIdentity']=value
            with self.assertRaises(AssertionError):a.reuse_identity(**x)
    def test_old_failed_worker_stopped_before_any_physical_tool(self):
        r=a.read(a.FAILED/'result.json');failure=a.read(a.FAILED/'guard-failure.json');self.assertEqual(r['jobId'],'4a8753ed334b3651abd5a8464c990a0483b7b232f6a02236178b263fde6b0f57');self.assertTrue(all(u in failure['error']for u in a.RETAINED));self.assertFalse((a.FAILED/'metrics.json').exists());self.assertIn('complete-original-role:ten-unattached-source-parts-pending-independent-role-review',r['reasons'])
    def test_actual_caller_globals_and_owned_setup_dependencies(self):
        t=symtable.symtable(Path(a.__file__).read_text(),a.__file__,'exec');known={s.get_name()for s in t.get_symbols()if s.is_assigned()or s.is_imported()}|set(dir(builtins))|{'__file__','__name__'}
        def visit(t):
            for s in t.get_symbols():
                if s.is_referenced()and s.is_global():self.assertIn(s.get_name(),known)
            for child in t.get_children():visit(child)
        visit(t)
if __name__=='__main__':unittest.main()
