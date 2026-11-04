"""Require unchanged legacy transactional, publication and whole-map readback guards."""
import ast,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent

def tree(name):return ast.dump(ast.parse((HERE/name).read_text()),include_attributes=False)
def same(test,old,text):test.assertEqual(tree(old),ast.dump(ast.parse(text),include_attributes=False))

class Parity(unittest.TestCase):
 def test_atomic_installer_only_module_browser_and_label_differ(self):
  s=(HERE/'installed_support_model_only_live_install_v1_20261027.py').read_text().replace('installed_support_model_only_guarded_publish_v1_20261027','supported_model_only_guarded_publish_v1_20261025').replace('ronsdale_three_live_browser_v15_20261026.mjs','ronsdale_three_live_browser_v13_20261025.mjs').replace('Unchanged original sources on exact installed native parents','Unchanged co-imported supported original sources')
  same(self,'supported_model_only_live_install_v2_20261026.py',s)
 def test_publisher_only_stage_type_and_added_native_recheck_differ(self):
  s=(HERE/'installed_support_model_only_guarded_publish_v1_20261027.py').read_text().replace('fully reviewed originals with exact installed native parents','fully reviewed standalone original source(s)').replace('installed_support_model_only_qualified_stage_v1_20261027','independent_model_only_qualified_stage_v1_20261024')
  extra="\n current=stage.current_models()\n assert stage.verify_native_scope(stage.read(BASE/stage.CONFIG['scope']/'summary.json'),stage.read(BASE/stage.CONFIG['nativeContacts']/'summary.json'),current)"
  self.assertIn(extra,s);s=s.replace(extra,'',1);same(self,'independent_model_only_guarded_publish_v1_20261024.py',s)
 def test_all_old_assets_ledger_global_support_and_live_readback_guards_identical(self):
  s=(HERE/'installed_support_model_only_installed_readback_v1_20261027.py').read_text()
  s=s.replace('from original_installed_support_model_only_contract_v1_20261027 import verify_metadata as metadata_contract','from original_supported_catalogue_scope_v1_20261024 import verify as verify_support_scope\nfrom original_independent_model_only_contract_v1_20261024 import verify_metadata as metadata_contract',1)
  addition="    selection=base/cfg['originalSelection'];_,source_pins=authenticate(selection);refs.append(selection/'result.json');sourcepath=selection/'selection.json.gz';assert digest(sourcepath.read_bytes())==source_pins[str(sourcepath.relative_to(ROOT))];refs.append(sourcepath);original_entries={r['uid']:r['candidate']['entry']for r in read(sourcepath)['rows']}\n"
  self.assertIn(addition,s);s=s.replace(addition,'',1)
  newer="sources==SOURCES and metadata_contract(new,SOURCES,cfg['supportByUid'],original_entries,{e['uid']:e for e in oldmodels})"
  older="verify_support_scope(new,sources,cfg['supportByUid'])and sources==SOURCES and metadata_contract(new,SOURCES)"
  self.assertIn(newer,s);s=s.replace(newer,older,1).replace("HERE/'original_installed_support_model_only_contract_v1_20261027.py'","HERE/'original_independent_model_only_contract_v1_20261024.py'",1)
  same(self,'independent_model_only_installed_readback_v1_20261024.py',s)
if __name__=='__main__':unittest.main()
