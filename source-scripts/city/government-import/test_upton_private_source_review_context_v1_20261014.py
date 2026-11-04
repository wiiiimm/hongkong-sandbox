import unittest,ast,symtable
from pathlib import Path
from upton_private_source_review_context_v1_20261014 import display_point,contact_summary

def world(dim=1,exposed=True):
    p=dict(freshCompleteCurrentGround=dict(selection=dict(completeGroundSHA256='ground',completeGroundFacetCount=11645,everyNoncandidateStrictlyDisjoint=True,touchingAndCollapsedProjectionsRetained=True),rootOrStructuralCredit=False,strictlyExposedWholePositiveInterface=exposed))
    r=dict(originalContactVerbatim=dict(dimension=dim),freshWholeLineOrAreaChordGroundProofs=[]if dim==0 else[p],areaInteriorNotQualified=dim==2,rootRoleOrBridgeAccepted=False)
    return dict(mode='literal',freshMainContactGroundContext=[r],exactSourceOnlyContactsVerbatim=dict(contacts=[{}]),actualWholeSourceWorldHashes={'P':'podium','T':'tower'},oldPacketGroundHashNotRelabelled='old-ground')

class ContextTests(unittest.TestCase):
    def test_fraction_display_preserves_rational_input(self):
        p=['1043081/512','200950823/31447040','-18598132187/9434112'];old=p.copy();r=display_point(p);self.assertEqual(p,old);self.assertEqual(r[0],1043081/512);self.assertEqual(len(r),3)
    def test_source_line_context_does_not_approve_strict(self):
        s=contact_summary([world()],'ground',11645)[0];self.assertEqual(s['strictlyExposedWholeLineContacts'],1);self.assertFalse(s['strictInterfacePassed']);self.assertFalse(s['installationApproved']);self.assertEqual(s['oldPacketGroundHashVerbatim'],'old-ground')
    def test_failed_exposure_retained(self):
        s=contact_summary([world(exposed=False)],'ground',11645)[0];self.assertEqual(s['positiveContactsWithUnprovedChordOrLineExposure'],[0]);self.assertEqual(s['strictlyExposedWholeLineContacts'],0)
    def test_area_chords_never_approve_area_interior(self):
        s=contact_summary([world(dim=2)],'ground',11645)[0];self.assertFalse(s['areaInteriorQualification']);self.assertEqual(s['strictlyExposedWholeLineContacts'],0);self.assertEqual(s['areaBoundaryAndChordProofs'],1)
    def test_point_no_exposure_credit(self):
        s=contact_summary([world(dim=0)],'ground',11645)[0];self.assertEqual(s['strictlyExposedWholeLineContacts'],0)
    def test_different_complete_ground_fails(self):
        with self.assertRaises(AssertionError):contact_summary([world()],'different',11645)
    def test_relabelled_root_credit_fails(self):
        w=world();w['freshMainContactGroundContext'][0]['rootRoleOrBridgeAccepted']=True
        with self.assertRaises(AssertionError):contact_summary([w],'ground',11645)
    def test_caller_real_functions_have_no_unbound_globals(self):
        # Explicit target catches the earlier HISTORY and local refs setup bugs;
        # inspect actual caller functions, not an implementation-mirror helper.
        path=Path(__file__).with_name('upton_joint_original_private_source_review_v1_20261014.py');src=path.read_text();tree=ast.parse(src);table=symtable.symtable(src,str(path),'exec');bound={s.get_name()for s in table.get_symbols()if s.is_assigned()or s.is_imported()}|set(dir(__builtins__))|{'__file__','__name__'}
        import builtins
        bound |= set(dir(builtins))
        def check(t):
            for s in t.get_symbols():
                if s.is_referenced()and s.is_global():self.assertIn(s.get_name(),bound)
            for c in t.get_children():check(c)
        check(table)
        self.assertTrue(any(isinstance(n,ast.FunctionDef)and n.name=='owned'for n in ast.walk(tree)))
if __name__=='__main__':unittest.main()
