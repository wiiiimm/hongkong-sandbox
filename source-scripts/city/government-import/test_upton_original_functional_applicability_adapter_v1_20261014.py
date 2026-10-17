import unittest,copy,symtable,builtins
from pathlib import Path
from unittest.mock import patch
import upton_joint_original_functional_private_stage_v1_20261014 as stage
from upton_original_functional_applicability_adapter_v1_20261014 import apply,NARROW
from upton_preserve_replacement_slot_v1_20261014 import preserve_slot

def inputs():
    p,d,i,images,q=stage.reviewed_inputs();r=stage.read(stage.functional.DOC/'ROOT-FUNCTIONAL-REVIEW.json');s=stage.read(stage.physical.DOC/'support-checks.json.gz')['rows'][0]['interface']
    return dict(decision=r,packet=p,descriptor_ref=d,display_ref=i,image_refs=images,packet_ref=q,raw_reasons=list(NARROW),strict=s)

class AdapterTests(unittest.TestCase):
    def test_actual_ROOT_review_resolves_only3_and_keeps_raw_false(self):
        x=inputs();old=copy.deepcopy(x);r=apply(**x);self.assertTrue(r['scriptChecksPassed']);self.assertEqual(set(r['resolvedByExactSourceFunctionalApplicability']),NARROW);self.assertFalse(r['strictInterfacePassed']);self.assertFalse(r['rawStrictInterfaceVerbatim']['passed']);self.assertEqual(len(r['rawStrictInterfaceVerbatim']['unresolved']),41);self.assertEqual(x,old);self.assertFalse(r['publication'])
    def test_nonaccepted_review_rejected(self):
        x=inputs();x['decision']['sourceFunctionalDispositionAccepted']=False
        with self.assertRaises(AssertionError):apply(**x)
    def test_other_genuine_failure_rejected(self):
        x=inputs();x['raw_reasons'].append('native-neighbour-regression:landsd/79882:0')
        with self.assertRaises(AssertionError):apply(**x)
    def test_changed_world_or_image_cannot_reuse_review(self):
        for mutation in ['world','image']:
            x=inputs()
            if mutation=='world':x['decision']['scope']['sourceBindings'][0]['wholeWorldSHA256']='0'*64
            else:x['decision']['imagesActuallyInspected'][0]['sha256']='0'*64
            with self.assertRaises(AssertionError):apply(**x)
    def test_strict_pass_or13_support_credit_relabel_rejected(self):
        for field in ['strictOriginalInterfacePassed','independentSupportFor13UnmatchedPointsProved']:
            x=inputs();x['decision'][field]=True
            with self.assertRaises(AssertionError):apply(**x)
    def test_real_saved_stage_setup_metadata_only(self):
        old=stage.read
        def mocked(p):
            if Path(p)==stage.PROPOSAL/'draft-pins.json':return dict(caller=stage.ref(Path(stage.__file__)),codeRefs=[],inputRefs=[],completedDisplayV2Job='a63f3a97ae19de21251fcc5d1f0a383617b69cd968a67d23d9cb7e926420c749',acceptedROOTReview=stage.ref(stage.functional.DOC/'ROOT-FUNCTIONAL-REVIEW.json'))
            return old(p)
        with patch.object(stage,'read',mocked):self.assertTrue(stage.load()[1]['sourceScopedApplicabilityAccepted'])
    def test_slot_order_only_preserves_other_metadata(self):
        old={'terrainPatches':[dict(url='a',resolution=1),dict(url='old',resolution=2),dict(url='z',resolution=3)]};new={'terrainPatches':[dict(url='a',resolution=1),dict(url='z',resolution=3),dict(url='new',resolution=2)]};before=copy.deepcopy(old);r=preserve_slot(old,new,'old','new');self.assertEqual(r['replacementIndex'],1);self.assertEqual([q['url']for q in new['terrainPatches']],['a','new','z']);self.assertEqual(old,before)
    def test_changed_other_patch_or_duplicate_rejected(self):
        for after in [[dict(url='a',resolution=8),dict(url='new',resolution=2)],[dict(url='new',resolution=2),dict(url='new',resolution=2)]]:
            with self.assertRaises(AssertionError):preserve_slot({'terrainPatches':[dict(url='a',resolution=1),dict(url='old',resolution=2)]},{'terrainPatches':after},'old','new')
    def test_actual_solid_browser_all_existing_guards_byte_equal(self):
        old=(stage.HERE/'xl-terrain-recovery-20261010-multi-native-solid-browser-v5.mjs').read_text();new=stage.BROWSER.read_text()
        a="m.terrainPatches=m.terrainPatches.filter(t=>!replaced.has(t.url));m.terrainPatches.push(...config.terrain.map(t=>({url:t.destination,resolution:t.resolution,area:t.area})));"
        b="assert.equal(config.terrain.length,1);const t=config.terrain[0];assert.equal(t.replaces?.url,'city/data/government-native-79882-0.json');assert.equal(t.sha256,'f367dc82a617357da96ddeb004d4e6aa75329ca237a5f5033ce3f21daf1f7848');const i=m.terrainPatches.findIndex(p=>p.url===t.replaces.url);assert(i>=0);m.terrainPatches.splice(i,1,{...m.terrainPatches[i],url:t.destination,resolution:t.resolution,area:t.area});"
        self.assertEqual(new.replace(b,a),old)
    def test_real_stage_global_bindings(self):
        t=symtable.symtable(Path(stage.__file__).read_text(),str(stage.__file__),'exec');bound={s.get_name()for s in t.get_symbols()if s.is_imported()or s.is_assigned()}|set(dir(builtins))|{'__file__','__name__'}
        def check(t):
            for s in t.get_symbols():
                if s.is_referenced()and s.is_global():self.assertIn(s.get_name(),bound)
            for q in t.get_children():check(q)
        check(t)
if __name__=='__main__':unittest.main()
