import copy,hashlib,unittest,symtable,builtins
from pathlib import Path
from upton_georef_dimensions_metadata_v1_20261014 import correct,assert_equivalent,encoded,bare
HERE=Path(__file__).parent

def fixture():
    x=dict(w=43,h=29,cell=5,elev=[0]*1247,vegetation=[0]*1247,renderedElev=[None]*1247,meta=dict(georef=dict(W=29,H=29,aE=5,aN=-5,bE=832022.5,bN=816537.5)),nativeMesh=dict(position=[1,2,3],index=[0,0,0],source=dict(provenance='synthetic'),sourceOverlap=dict(policy='highest-native-surface',measuredProjectedExcessM2=1,evidencePath='old.json',evidenceSHA256='x')))
    return x,dict(stagedGeometrySha256=hashlib.sha256(encoded(bare(x))).hexdigest())
class Tests(unittest.TestCase):
    def test_only_stale_width_and_audit_binding_changes(self):
        x,a=fixture();before=copy.deepcopy(x);y,p=correct(x,a);self.assertEqual(x,before);self.assertEqual(y['meta']['georef']['W'],43);self.assertEqual(p['changedJSONPaths'],['meta.georef.W']);y['nativeMesh']['sourceOverlap'].update(evidencePath='new.json',evidenceSHA256='y');assert_equivalent(x,y)
    def test_geometry_grid_provenance_affine_and_threshold_mutations_rejected(self):
        for key in ['position','index','provenance','elev','vegetation','renderedElev','origin','overlap','signedzero','booltype']:
            x,a=fixture()
            if key=='signedzero':x['nativeMesh']['position'][0]=0.0;a['stagedGeometrySha256']=hashlib.sha256(encoded(bare(x))).hexdigest()
            y,_=correct(x,a)
            if key=='signedzero':y['nativeMesh']['position'][0]=-0.0
            elif key=='booltype':y['elev'][0]=False
            elif key in ['position','index']:y['nativeMesh'][key][0]+=1
            elif key=='provenance':y['nativeMesh']['source']['provenance']='changed'
            elif key in ['elev','vegetation','renderedElev']:y[key][0]=99
            elif key=='origin':y['meta']['georef']['bE']+=1
            else:y['nativeMesh']['sourceOverlap']['measuredProjectedExcessM2']+=1
            with self.assertRaises(AssertionError):assert_equivalent(x,y)
    def test_wrong_original_hash_or_dimensions_fail_closed(self):
        for mutation in ['hash','width','shape']:
            x,a=fixture()
            if mutation=='hash':a['stagedGeometrySha256']='0'*64
            elif mutation=='width':x['w']=29;a['stagedGeometrySha256']=hashlib.sha256(encoded(bare(x))).hexdigest()
            else:x['vegetation'].pop();a['stagedGeometrySha256']=hashlib.sha256(encoded(bare(x))).hexdigest()
            with self.assertRaises(AssertionError):correct(x,a)
    def test_actual_pinned_consumers_do_not_read_descriptive_dimensions(self):
        root=HERE.parents[2]
        for name in ['world.js','geo.js','terrain-patch-index.js']:
            s=(root/'3d-viewer/city'/name).read_text()
            import re
            self.assertIsNone(re.search(r'\.(?:W|H)\b|\[\s*[\"\x27](?:W|H)[\"\x27]\s*\]',s))
    def test_browser_all_existing_runtime_guards_byte_identical(self):
        old=(HERE/'upton_functional_joint_resolution_browser_v1_20261014.mjs').read_text();new=(HERE/'upton_dimension_joint_resolution_browser_v2_20261014.mjs').read_text();a=new.index('const correction=');b=new.index('const browserModels=',a);new=new[:a]+new[b:];new=new.replace('assert.equal(t.sha256,config.dimensionMetadataCorrection.newTerrainSHA256);',"assert.equal(t.sha256,'f367dc82a617357da96ddeb004d4e6aa75329ca237a5f5033ce3f21daf1f7848');");self.assertEqual(new,old)
    def test_actual_publisher_grid_rejects_stale_and_accepts_correction(self):
        import importlib.util
        root=HERE.parents[2];path=root/'source-scripts/city/island-detail-integration/publish.py';spec=importlib.util.spec_from_file_location('upton_synthetic_actual_publisher',path);publisher=importlib.util.module_from_spec(spec);spec.loader.exec_module(publisher)
        x,a=fixture()
        with self.assertRaisesRegex(AssertionError,'Terrain georef dimensions mismatch'):publisher.validate_grid(x)
        y,_=correct(x,a);publisher.validate_grid(y)
    def test_new_caller_globals_bound(self):
        for name in ['upton_joint_original_dimension_private_stage_v2_20261014.py','upton_joint_original_dimension_staged_browser_v2_20261014.py','upton_slot_preserving_guarded_publish_v2_20261014.py']:
            tree=symtable.symtable((HERE/name).read_text(),name,'exec');known={s.get_name()for s in tree.get_symbols()if s.is_assigned()or s.is_imported()}|set(dir(builtins))|{'__file__','__name__'}
            def visit(t):
                for symbol in t.get_symbols():
                    if symbol.is_referenced()and symbol.is_global():self.assertIn(symbol.get_name(),known,(name,symbol.get_name()))
                for child in t.get_children():visit(child)
            visit(tree)
if __name__=='__main__':unittest.main()
