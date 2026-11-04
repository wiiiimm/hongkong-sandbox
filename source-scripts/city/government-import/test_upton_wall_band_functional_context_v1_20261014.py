import unittest,symtable,builtins
from pathlib import Path
from fractions import Fraction as F
from upton_wall_band_functional_context_v1_20261014 import face_descriptor,proposal,NARROW
S=dict(passed=False,samples=138,strictContacts=97,wallIntersections=0)
UNMATCHED=[11,12,15,16,17,18,19,20,21,22,23,24,25]
class FunctionalContextTests(unittest.TestCase):
    def test_exact_vertical_face_descriptor_not_acceptance(self):
        d=face_descriptor(12,[[0,17,0],[0,25,0],[0,17,3]])
        self.assertTrue(d['exactNormalYIsZero']);self.assertEqual(d['exactHeightIntervalM'],['17','25']);self.assertTrue(d['noContactOrRootCredit'])
    def test_tiny_projected_area_is_not_snapped_vertical(self):
        d=face_descriptor(3,[[0,17,0],[F(1,2**50),25,0],[0,17,3]])
        self.assertFalse(d['exactNormalYIsZero']);self.assertNotEqual(F(d['exactProjectedSignedDoubleAreaXZ']),0)
    def test_fraction_source_points_exact_and_unchanged(self):
        p=[['1043081/512','200950823/31447040','-18598132187/9434112'],['2','21','5'],['3','17','9']];before=[q[:]for q in p];d=face_descriptor(4993,p);self.assertEqual(p,before);self.assertEqual(d['exactBinary64InputPoints'][0],p[0])
    def test_raw_strict_failure_and13_unmatched_never_become_pass(self):
        d=proposal(list(NARROW),S,UNMATCHED,True);self.assertEqual(set(d['proposedSourceApplicabilityDisposition']),NARROW);self.assertFalse(d['strictOriginalInterfacePassed']);self.assertFalse(d['physicalAccepted']);self.assertFalse(d['independentSupportFor13UnmatchedPointsProved']);self.assertEqual(d['strictOriginalInterfaceVerbatim'],S)
    def test_unknown_and_other_source_reason_retained(self):
        extra=['native-neighbour-regression:landsd/79882:0','landsd/12728:0:ground-contact-unresolved'];d=proposal(list(NARROW)+extra,S,UNMATCHED,True);self.assertEqual(d['otherReasonsNeverResolved'],sorted(extra))
    def test_incomplete_context_cannot_propose_clearance(self):
        d=proposal(list(NARROW),S,UNMATCHED,False);self.assertEqual(d['proposedSourceApplicabilityDisposition'],[]);self.assertEqual(d['otherReasonsNeverResolved'],sorted(NARROW))
    def test_relabelled_strict_success_or_missing_point_fails(self):
        with self.assertRaises(AssertionError):proposal(list(NARROW),{**S,'passed':True},UNMATCHED,True)
        with self.assertRaises(AssertionError):proposal(list(NARROW),S,UNMATCHED[:-1],True)
    def test_actual_both_new_caller_function_global_bindings(self):
        for name in ['upton_joint_original_wall_band_functional_packet_v1_20261014.py','upton_joint_original_private_source_review_v2_20261014.py']:
            p=Path(__file__).with_name(name);t=symtable.symtable(p.read_text(),str(p),'exec');bound={s.get_name()for s in t.get_symbols()if s.is_imported()or s.is_assigned()}|set(dir(builtins))|{'__file__','__name__'}
            def check(t):
                for s in t.get_symbols():
                    if s.is_referenced()and s.is_global():self.assertIn(s.get_name(),bound,(name,s.get_name()))
                for q in t.get_children():check(q)
            check(t)
    def test_actual_completed_saved_metadata_setup_without_worker(self):
        # Exercise the real setup loaders against ROOT-verified saved receipts.
        # Only the not-yet-created new preparation collector is mocked; this
        # fixture deliberately grants no complete closure/preparation credit.
        from unittest.mock import patch
        import upton_joint_original_wall_band_functional_packet_v1_20261014 as f
        import upton_joint_original_private_source_review_v2_20261014 as v
        for a in [f,v]:
            old=a.read
            def fixture_read(p):
                if Path(p)==a.PROPOSAL/'draft-pins.json':return dict(caller=a.ref(Path(a.__file__)),codeRefs=[],inputRefs=[])
                return old(p)
            with patch.object(a,'read',fixture_read):self.assertTrue(a.load())
if __name__=='__main__':unittest.main()
