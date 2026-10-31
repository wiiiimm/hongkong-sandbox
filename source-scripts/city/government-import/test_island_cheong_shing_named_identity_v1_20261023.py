import unittest
from copy import deepcopy
from island_cheong_shing_named_identity_v1_20261023 import EXACT,validate_named_boundary_contract

def fixture():
    sources={u:r[2]for u,r in EXACT.items()};boundary=dict(sourceSHA256ByUid=sources,all774CurrentFormsRetained=True,completeOriginalFaces=13848,foreignOverlapM2=4.431317,foreignFootprintBoundaryDistance=dict(upperM=.358082),familyFootprintBoundaryDistance=dict(upperM=.413410),rows=[dict(uid=u,otherUid='landsd/269430:0',allExactPairsExamined=True)for u in ['landsd/20270:0','landsd/159422:0']]);family=dict(all774CurrentFormsRetained=True,foreignExcessOverlaps=[dict(uid='landsd/269430:0')],familyProjectionQualified=True,wholeFamilyCurrentTargetCoverage=.99999,maximumFullFamilyExtentM=1.86,coInstallationRequired={u:sources[u]for u in ['landsd/20270:0','landsd/159422:0']},exactWholeGeoRefCellProofs=[dict(exactProjectionCovered=True)]*2);return boundary,family,deepcopy(sources)

class BoundaryIdentity(unittest.TestCase):
    def test_exact_bounded_context(self):validate_named_boundary_contract(*fixture())
    def test_missing_counterpart_cannot_pass(self):
        a,b,c=fixture();c.pop('landsd/274231:0')
        with self.assertRaises(AssertionError):validate_named_boundary_contract(a,b,c)
    def test_changed_source_cannot_inherit_review(self):
        a,b,c=fixture();c['landsd/20270:0']='0'*64
        with self.assertRaises(AssertionError):validate_named_boundary_contract(a,b,c)
    def test_additional_foreign_form_is_not_exempt(self):
        a,b,c=fixture();b['foreignExcessOverlaps'].append(dict(uid='landsd/999:0'))
        with self.assertRaises(AssertionError):validate_named_boundary_contract(a,b,c)
    def test_wider_boundary_overlap_needs_new_review(self):
        a,b,c=fixture();a['foreignFootprintBoundaryDistance']['upperM']=.4
        with self.assertRaises(AssertionError):validate_named_boundary_contract(a,b,c)
    def test_omitting_current_forms_fails(self):
        a,b,c=fixture();a['all774CurrentFormsRetained']=False
        with self.assertRaises(AssertionError):validate_named_boundary_contract(a,b,c)
    def test_incomplete_source_cell_stays_failed(self):
        a,b,c=fixture();b['exactWholeGeoRefCellProofs']=[dict(exactProjectionCovered=False)]
        with self.assertRaises(AssertionError):validate_named_boundary_contract(a,b,c)

if __name__=='__main__':unittest.main()
