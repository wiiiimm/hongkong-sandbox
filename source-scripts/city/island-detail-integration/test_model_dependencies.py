import unittest,tempfile,json,hashlib
from pathlib import Path
from model_dependencies import stage_dependencies
class DependencyGate(unittest.TestCase):
 def test_new_podium_cannot_invalidate_existing_fallback(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);path=root/'3d-viewer/city/old.json';path.parent.mkdir(parents=True);path.write_text(json.dumps({'models':[{'uid':'tower','supportDependencies':['podium']},{'uid':'podium'}]}))
   with self.assertRaisesRegex(AssertionError,'surveyed fallback'):stage_dependencies(root,{}, {'officialModelCatalogues':['city/old.json']},{},{'podium':{}},{})
 def test_native_cycle_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);path=root/'3d-viewer/city/old.json';path.parent.mkdir(parents=True);path.write_text(json.dumps({'models':[{'uid':'a','supportDependencies':[{'uid':'b','state':'installed'}]},{'uid':'b','supportDependencies':[{'uid':'a','state':'installed'}]}]}))
   with self.assertRaisesRegex(AssertionError,'Cyclic'):stage_dependencies(root,{}, {'officialModelCatalogues':['city/old.json']},{},{'a':{}},{})
 def test_missing_native_support_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);path=root/'3d-viewer/city/old.json';path.parent.mkdir(parents=True);path.write_text(json.dumps({'models':[{'uid':'a','supportDependencies':[{'uid':'missing','state':'installed'}]}]}))
   with self.assertRaisesRegex(AssertionError,'Missing'):stage_dependencies(root,{}, {'officialModelCatalogues':['city/old.json']},{},{'a':{}},{})
if __name__=='__main__':unittest.main()
