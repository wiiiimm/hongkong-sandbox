"""Actual completed metadata/provenance fixtures only; no source geometry calculation."""
import copy,unittest
import heritage165054_two_tin_nearwater_bare_nomination_v1_20261014 as a
class TwoSourceMetadata(unittest.TestCase):
    def context(self):return a.read(a.CONTEXT)
    def test_actual_6906_selected_facets_are_not_6906_plus_north(self):
        c=self.context();slots=a.selected_source_offsets(c,101426,97667)
        self.assertEqual(len(slots),6906);self.assertEqual(sum(i<101426 for i in slots),5223);self.assertEqual(sum(i>=101426 for i in slots),1683);self.assertEqual(len(set(slots)),6906)
    def test_duplicate_source_occurrence_cannot_silently_change_mapping(self):
        c=self.context();c['selectedCompleteOriginalFacets'][1]=copy.deepcopy(c['selectedCompleteOriginalFacets'][0])
        with self.assertRaises(AssertionError):a.selected_source_offsets(c,101426,97667)
    def test_unknown_sheet_or_face_outside_source_rejected(self):
        for kind in ['sheet','face']:
            c=self.context()
            if kind=='sheet':c['selectedCompleteOriginalFacets'][0]['sheet']='unbound-sheet'
            else:c['selectedCompleteOriginalFacets'][0]['originalFaceID']=101426
            with self.subTest(kind=kind),self.assertRaises(AssertionError):a.selected_source_offsets(c,101426,97667)
    def test_actual_22_warnings_and897_nonwater_values_retained(self):
        c=self.context();self.assertIs(a.bind_context(c),c);self.assertEqual(sum(len(f['lowSourceVertices'])for f in c['allSelectedInputClampFacetContexts']),897)
        c['allSelectedInputClampFacetContexts'][0]['lowSourceVertices'][0]['parentRawWater']=True
        with self.assertRaises(AssertionError):a.bind_context(c)
if __name__=='__main__':unittest.main()
