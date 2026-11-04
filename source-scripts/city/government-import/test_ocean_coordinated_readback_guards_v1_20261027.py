"""Keep whole-map, image, ledger and rollback-history readback guards intact."""
import ast,unittest
from pathlib import Path
HERE=Path(__file__).parent

class ReadbackGuards(unittest.TestCase):
    def test_old_guards_preserved_except_explicit_assembly_extensions(self):
        old=(HERE/'tung_on_retained_installed_readback_v1_20261026.py').read_text()
        new=(HERE/'ocean_coordinated_installed_readback_v1_20261027.py').read_text()
        replacements={
            "inventory=base/cfg['physical'];_,oldpins=authenticate(inventory);refs.append(inventory/'result.json');":"inventory=base/'government-xl-after-tuen-mun-current-inventory-v1-20261026';_,oldpins=authenticate(inventory);refs.append(inventory/'result.json');",
            "cfg['prefix']+'-qualified-stage-v2-'+cfg['date']":"cfg['prefix']+'-retained-qualified-stage-v2-'+cfg['date']",
            "==set(replacement['retainedUids'])|set(cfg['groundOwnerUids'])":"==set(replacement['retainedUids'])|set(sources)"
        }
        for a,b in replacements.items():
            self.assertEqual(new.count(a),1);new=new.replace(a,b,1)
        a=new.index('    from original_coordinated_retained_contract_v1_20261027 import verify_metadata,verify_terrain')
        b=new.index("    assert {e['uid']:e for e in models if e['uid']not in sources}",a)
        new=new[:a]+"    assert all(not e.get('supportDependencies')and not e.get('retainedBasicSupportDependencies')for e in new)\n"+new[b:]
        a=new.index("    mobile=read(installed/'viewport-390/live-browser.json')")
        b=new.index("    pointer=ROOT/",a)
        new=new[:a]+"    mobile=read(installed/'viewport-390/live-browser.json');failed=[v for v in mobile['views']if v.get('phase')=='failed-download'];assert len(failed)==len(sources)and {v['uid']for v in failed}==set(sources)and all(v['fallbackRetained']for v in failed)\n"+new[b:]
        a=new.index("    patchpath=base/cfg['patch']/'summary.json'")
        b=new.index("    result['terrainReplacementVerified']=terrain",a);new=new[:a]+new[b:]
        self.assertEqual(ast.dump(ast.parse(old)),ast.dump(ast.parse(new)))

    def test_positive_support_and_real_http_failure_proofs_required(self):
        source=(HERE/'ocean_coordinated_installed_readback_v1_20261027.py').read_text()
        for fragment in ['verify_metadata(new,sources',"atomic['liveInstalledHTTP']","atomic['catalogueAndTerrainSubstitution'] is False",'verify_atomic(atomic,new)','verify_terrain(read(',"cfg['groundOwnerUids']"]:
            with self.subTest(fragment=fragment):self.assertIn(fragment,source)

if __name__=='__main__':unittest.main()
