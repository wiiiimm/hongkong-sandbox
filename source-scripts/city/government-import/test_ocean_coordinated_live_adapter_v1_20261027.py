"""Preserve rollback/ledger guards and complete lifecycle assertions in adapters."""
import ast,unittest
from pathlib import Path
HERE=Path(__file__).parent

def functions(name):
    return {n.name:n for n in ast.parse((HERE/name).read_text()).body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}

class LiveAdapterGuards(unittest.TestCase):
    def test_shared_installer_guards_unchanged(self):
        old=functions('tung_on_retained_live_install_v1_20261026.py')
        new=functions('ocean_coordinated_live_install_v1_20261027.py')
        for name in ['inventory_part','browser_config','restore','main']:
            with self.subTest(name=name):self.assertEqual(ast.dump(old[name]),ast.dump(new[name]))

    def test_load_only_adds_live_harness_bindings(self):
        old=functions('tung_on_retained_live_install_v1_20261026.py')['load']
        new=functions('ocean_coordinated_live_install_v1_20261027.py')['load']
        additions=[n for n in new.body if isinstance(n,ast.Expr) and isinstance(n.value,ast.Call) and isinstance(n.value.func,ast.Attribute) and isinstance(n.value.func.value,ast.Name) and n.value.func.value.id=='predecessor_refs' and n.value.func.attr=='extend']
        self.assertEqual(len(additions),1)
        new.body.remove(additions[0]);self.assertEqual(ast.dump(old),ast.dump(new))

    def test_all_lifecycle_checks_preserved_after_http_setup(self):
        old=(HERE/'model_atomic_lifecycle_browser_v1_20261027.mjs').read_text()
        new=(HERE/'model_atomic_lifecycle_live_browser_v1_20261027.mjs').read_text()
        marker="  console.log(name,'initialising');"
        self.assertEqual(old[old.index(marker):],new[new.index(marker):])
        self.assertIn('config.liveInstalled===true',new)
        self.assertIn('assert.deepEqual(installedManifest,',new)
        self.assertIn('assert.deepEqual(await catResponse.json(),catalogue)',new)
        self.assertNotIn('r.fulfill({json:catalogue})',new)
        self.assertNotIn('m.officialModelCatalogues.push(url)',new)
        self.assertIn('r.continue()',new)

    def test_owned_transaction_restoration_and_inventory_assertions_retained(self):
        old=ast.get_source_segment((HERE/'tung_on_retained_live_install_v1_20261026.py').read_text(),functions('tung_on_retained_live_install_v1_20261026.py')['owned'])
        new=ast.get_source_segment((HERE/'ocean_coordinated_live_install_v1_20261027.py').read_text(),functions('ocean_coordinated_live_install_v1_20261027.py')['owned'])
        a=new.index('   from ocean_coordinated_full_browser_v2_20261027 import verify_atomic')
        b=new.index("   report=dict(mode='live'",a);new=new[:a]+new[b:]
        replacements={
            "|set(stage.CONFIG['groundOwnerUids'])":"|set(stage.SOURCES)",
            "failed=[v for v in report['views']if v.get('phase')=='failed-download'];assert failed==[];assert verify_atomic(read(DOC/'atomic-live/report.json'),models)":"failed=[v for v in report['views']if v.get('phase')=='failed-download'];assert len(failed)==len(stage.SOURCES) and {v['uid']for v in failed}==set(stage.SOURCES) and all(v['fallbackRetained']for v in failed)",
            "kind='supported-atomic-original-installed-v1'":"kind='selected-independent-original-installed-v1'",
            "'Unchanged supported atomic original sources with verified bounded terrain, exact-source interpretation, four-mode foundations, complete neighbours and reviewed desktop/mobile exports.'":"'Unchanged independent original sources with verified bounded terrain, exact-source interpretation, four-mode foundations, complete neighbours and reviewed desktop/mobile exports.'"
        }
        for a,b in replacements.items():
            self.assertEqual(new.count(a),1);new=new.replace(a,b,1)
        self.assertEqual(ast.dump(ast.parse(old)),ast.dump(ast.parse(new)))

if __name__=='__main__':unittest.main()
