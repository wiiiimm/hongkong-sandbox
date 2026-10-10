"""Actual frozen inputs and adverse full-binding cases for Villa identity."""
import copy
import json
import unittest
from run import ROOT,read
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from villa_current_native_inventory_20261010 import verify_native_rows
import villa_current_bound_courtyard_upper_boundary_identity_20261010 as v

ROW=read(v.DOC/'selection.json.gz')['rows'][0]
CONTEXT=read(v.DOC/'context.json.gz')['rows'][0]
CAPTURE=read(v.DOC/'current-inputs.json.gz')
LOOKUP=read(v.DOC/'source-lookup.json.gz')
RECEIPT=read(v.DOC/'result.json')
TRI=decode_original_world_triangles((ROOT/ROW['candidate']['path']).read_bytes())
final=v.module('villa_binding_test_actual_forms','xl-final-script-pass.py')
LOADED=final.load_forms([TRI[:,:,0].min()-2,TRI[:,:,2].min()-2,TRI[:,:,0].max()+2,TRI[:,:,2].max()+2])


class BindingTests(unittest.TestCase):
    def test_all_frozen_reference_hashes(self):self.assertTrue(v.verify_receipt(RECEIPT))
    def test_actual_two_primary_geometry_queries(self):self.assertEqual(len(v.primary_records()),2)
    def test_actual_unique_native_inventory(self):self.assertTrue(verify_native_rows(LOOKUP['rows']))
    def test_actual_complete_current_forms_and_route(self):
        forms,route=v.current_binding(ROW,CONTEXT,TRI,CAPTURE,lambda bounds:LOADED)
        self.assertEqual(forms,CAPTURE['forms']);self.assertTrue(route)
    def test_actual_raw_full_cell_replayed(self):
        forms,route=v.current_binding(ROW,CONTEXT,TRI,CAPTURE,lambda bounds:LOADED)
        p=v.replay_raw(ROW,CONTEXT,TRI,(ROOT/ROW['candidate']['path']).read_bytes(),forms,route)
        self.assertEqual(p['reasons'],['fresh-current-spatial-bound:sourceExcessCoveredByUnrelatedFormsM2','full-source-unrelated-overlap'])
    def test_changed_frozen_evidence_bytes(self):
        ref=RECEIPT['evidenceRefs'][0]['path']
        def altered(p):return p.read_bytes()+b' ' if p.resolve()==(ROOT/ref).resolve() else p.read_bytes()
        with self.assertRaises(AssertionError):v.verify_receipt(RECEIPT,altered)
    def test_duplicate_receipt_reference(self):
        r=copy.deepcopy(RECEIPT);r['evidenceRefs'].append(r['evidenceRefs'][0])
        with self.assertRaises(AssertionError):v.verify_receipt(r)
    def test_foreign_receipt_batch(self):
        r=copy.deepcopy(RECEIPT);r['batch']='unrelated'
        with self.assertRaises(AssertionError):v.verify_receipt(r)
    def test_installed_receipt_credit_forbidden(self):
        r=copy.deepcopy(RECEIPT);r['newlyInstalled']=1
        with self.assertRaises(AssertionError):v.verify_receipt(r)
    def test_primary_wrong_query_table(self):
        def load(p):
            r=copy.deepcopy(read(p));r['url']=v.BASE+'/1002/query';return r
        with self.assertRaises(AssertionError):v.primary_records(load)
    def test_primary_no_geometry_query(self):
        def load(p):
            r=copy.deepcopy(read(p));r['parameters']['returnGeometry']='false';return r
        with self.assertRaises(AssertionError):v.primary_records(load)
    def test_primary_wrong_csuid_query(self):
        def load(p):
            r=copy.deepcopy(read(p));r['parameters']['where']='1=1';return r
        with self.assertRaises(AssertionError):v.primary_records(load)
    def test_primary_changed_decoded_bytes(self):
        def altered(p):return p.read_bytes()+b' ' if p.name=='exact-current-primary.json' else p.read_bytes()
        with self.assertRaises(AssertionError):v.primary_records(read,altered)
    def test_primary_changed_compressed_provider_bytes(self):
        req=read(v.DOC/'exact-current-primary.request.json')
        target='exact-current-primary.provider-original.gz' if req['gzipDecoded'] else 'exact-current-primary.json'
        def altered(p):return p.read_bytes()+b' ' if p.name==target else p.read_bytes()
        with self.assertRaises(AssertionError):v.primary_records(read,altered)
    def test_duplicate_native_source(self):
        with self.assertRaises(AssertionError):verify_native_rows(LOOKUP['rows']+LOOKUP['rows'])
    def test_missing_native_source(self):
        with self.assertRaises(AssertionError):verify_native_rows([])
    def test_wrong_native_model(self):
        r=copy.deepcopy(LOOKUP['rows']);r[0]['model']['modelId']='B216223338401063C0'
        with self.assertRaises(AssertionError):verify_native_rows(r)
    def test_wrong_native_sha(self):
        r=copy.deepcopy(LOOKUP['rows']);r[0]['model']['asset']['sha256']='0'*64
        with self.assertRaises(AssertionError):verify_native_rows(r)
    def test_missing_native_faces(self):
        r=copy.deepcopy(LOOKUP['rows']);r[0]['model']['triangles']-=1
        with self.assertRaises(AssertionError):verify_native_rows(r)
    def test_wrong_native_key(self):
        r=copy.deepcopy(LOOKUP['rows']);r[0]['sourceKey']='x/other'
        with self.assertRaises(AssertionError):verify_native_rows(r)
    def test_stale_manifest(self):
        cap=copy.deepcopy(CAPTURE);cap['manifestSHA256']='0'*64
        with self.assertRaises(AssertionError):v.current_binding(ROW,CONTEXT,TRI,cap,lambda bounds:LOADED)
    def test_missing_current_foreign_actor(self):
        with self.assertRaises(AssertionError):v.current_binding(ROW,CONTEXT,TRI,CAPTURE,lambda bounds:LOADED[:-1])
    def test_duplicate_current_actor(self):
        with self.assertRaises(AssertionError):v.current_binding(ROW,CONTEXT,TRI,CAPTURE,lambda bounds:LOADED+[LOADED[0]])
    def test_changed_current_form(self):
        loaded=copy.deepcopy(LOADED);loaded[0][0]['height']+=1
        with self.assertRaises(AssertionError):v.current_binding(ROW,CONTEXT,TRI,CAPTURE,lambda bounds:loaded)
    def test_missing_route_tile(self):
        cap=copy.deepcopy(CAPTURE);cap['exactRouteTileHashes']={}
        with self.assertRaises(AssertionError):v.current_binding(ROW,CONTEXT,TRI,cap,lambda bounds:LOADED)


if __name__=='__main__':unittest.main()
