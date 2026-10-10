"""Actual captured current/native/provider adversaries; no physical approval."""
import copy,json,unittest,numpy as np
from run import ROOT,read,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
import man_hei_current_bound_mandatory_platform_identity_v2_20261010 as k
from man_hei_dependent_platform_current_identity_v2_20261010 import verify_native_rows as dependent_native
DOC=k.DOC;ROWS=read(DOC/'selection.json.gz')['rows'];CONTEXTS=read(DOC/'context.json.gz')['rows'];CAP=read(DOC/'current-inputs.json.gz');NATIVE=read(DOC/'source-lookup.json.gz')['rows'];RECEIPT=read(DOC/'result.json')
WORLD=np.concatenate([decode_original_world_triangles((ROOT/r['candidate']['path']).read_bytes()) for r in ROWS])
FINAL=k.module('manhei_adapter_actual_forms_fixture','xl-final-script-pass.py')

class ManHeiBindingTests(unittest.TestCase):
    def rejects(self,func):
        with self.assertRaises((AssertionError,KeyError,ValueError)):func()
    def test_actual_native_unique(self):self.assertTrue(k.verify_native_rows(copy.deepcopy(NATIVE)))
    def test_duplicate_native_rows(self):self.rejects(lambda:k.verify_native_rows(NATIVE+[NATIVE[0]]))
    def test_ambiguous_native_same_model(self):self.rejects(lambda:k.verify_native_rows([NATIVE[0],NATIVE[0]]))
    def test_wrong_native_source_sha(self):
        n=copy.deepcopy(NATIVE);n[0]['model']['asset']['sha256']='0'*64;self.rejects(lambda:k.verify_native_rows(n))
    def test_wrong_native_key(self):
        n=copy.deepcopy(NATIVE);n[0]['sourceKey']='different/model';self.rejects(lambda:k.verify_native_rows(n))
    def test_actual_provider_exact_queries(self):
        self.assertEqual(len(k.checked_provider('exact-current-primary',0,True)),2);self.assertEqual(k.checked_provider('exact-current-structure-relations',1002,False),[])
    def provider_bad(self,key,value):
        def load(p):
            d=copy.deepcopy(read(p));d['parameters'][key]=value;return d
        self.rejects(lambda:k.checked_provider('exact-current-primary',0,True,load=load))
    def test_provider_missing_geometry(self):self.provider_bad('returnGeometry','false')
    def test_provider_wrong_csuid(self):self.provider_bad('where','BuildingCSUID IS NOT NULL')
    def test_provider_wrong_units(self):self.provider_bad('outSR','4326')
    def test_provider_wrong_http(self):
        def load(p):
            d=copy.deepcopy(read(p));d['method']='POST';return d
        self.rejects(lambda:k.checked_provider('exact-current-primary',0,True,load=load))
    def test_provider_response_changed(self):
        def bytes_(p):return p.read_bytes()+b' ' if p.name=='exact-current-primary.json' else p.read_bytes()
        self.rejects(lambda:k.checked_provider('exact-current-primary',0,True,read_bytes=bytes_))
    def test_actual_complete_current_binding(self):
        self.assertEqual(k.current_binding(copy.deepcopy(ROWS),copy.deepcopy(CONTEXTS),WORLD,CAP,FINAL.load_forms),CAP['forms'])
    def test_stale_manifest_rejected(self):
        cap=copy.deepcopy(CAP);cap['manifestSHA256']='0'*64;self.rejects(lambda:k.current_binding(ROWS,CONTEXTS,WORLD,cap,FINAL.load_forms))
    def test_missing_current_foreign_actor(self):
        cap=copy.deepcopy(CAP);cap['forms'].pop(0);self.rejects(lambda:k.current_binding(ROWS,CONTEXTS,WORLD,cap,FINAL.load_forms))
    def test_current_tile_changed(self):
        cap=copy.deepcopy(CAP);cap['tileHashes'][next(iter(cap['tileHashes']))]='0'*64;self.rejects(lambda:k.current_binding(ROWS,CONTEXTS,WORLD,cap,FINAL.load_forms))
    def test_context_tile_changed(self):
        c=copy.deepcopy(CONTEXTS);c[0]['neighbourTileHashes']={};self.rejects(lambda:k.current_binding(ROWS,c,WORLD,CAP,FINAL.load_forms))
    def test_missing_required_platform_row(self):self.rejects(lambda:k.current_binding(ROWS[:1],CONTEXTS,WORLD,CAP,FINAL.load_forms))
    def test_current_own_footprint_changed(self):
        r=copy.deepcopy(ROWS);r[0]['source']['building']['rings'][0][0][0]+=.001;self.rejects(lambda:k.current_binding(r,CONTEXTS,WORLD,CAP,FINAL.load_forms))
    def test_actual_frozen_receipt(self):self.assertTrue(k.verify_receipt(RECEIPT))
    def test_frozen_evidence_changed(self):self.rejects(lambda:k.verify_receipt(RECEIPT,read_bytes=lambda p:p.read_bytes()+b' '))
    def test_duplicate_evidence_reference(self):
        r=copy.deepcopy(RECEIPT);r['evidenceRefs'].append(r['evidenceRefs'][0]);self.rejects(lambda:k.verify_receipt(r))
    def test_evidence_path_escape(self):
        r=copy.deepcopy(RECEIPT);r['evidenceRefs'][0]['path']='../../tmp/not-authorized-source';self.rejects(lambda:k.verify_receipt(r))
    def test_dependent_platform_duplicate_native_rejected(self):
        p=k.module('manhei_test_dep','man_hei_dependent_platform_current_identity_v2_20261010.py');m=p.adapter();rows=read(p.DOC/'original-source-lookup.json.gz')['rows'];self.assertTrue(dependent_native(rows,m.RELATED_SHA));self.rejects(lambda:dependent_native([rows[0],rows[0]],m.RELATED_SHA))

if __name__=='__main__':unittest.main()
