import ast
from pathlib import Path
from types import SimpleNamespace
from copy import deepcopy
import unittest


class ScopeTests(unittest.TestCase):
    def config(self, required, staged=('a',), sources=('new',)):
        p = Path(__file__).with_name('selected_original_retained_live_install_v8_20261023.py')
        node = next(n for n in ast.parse(p.read_text()).body if isinstance(n, ast.FunctionDef) and n.name == 'browser_config')
        data = {Path('/repo/stage/live-browser-config.json'): dict(additionalRetainedUids=list(staged)), Path('/repo/stage/plan.json'): dict(areas=[dict(destination='catalogue')], topLevelTerrainPatches=['unchanged']), Path('/repo/review/ROOT-PHYSICAL-REVIEW.json'): dict(retainedNativeRegression=dict(requiredNativeUids=required))}
        ns = dict(ROOT=Path('/repo'), stage=SimpleNamespace(STAGE=Path('/repo/stage'), SOURCES=dict.fromkeys(sources)), guard=SimpleNamespace(REVIEW=Path('/repo/review')), read=lambda p: deepcopy(data[p]))
        exec(compile(ast.Module(body=[node], type_ignores=[]), str(p), 'exec'), ns)
        return ns['browser_config'](390)

    def test_full_physical_scope_replaces_smaller_staged_list(self):
        c = self.config(['c', 'a', 'b'])
        self.assertEqual(c['additionalRetainedUids'], ['a', 'b', 'c'])
        self.assertEqual(c['viewportWidths'], [390])
        self.assertEqual(c['terrain'], ['unchanged'])

    def test_existing_staged_actor_cannot_disappear(self):
        with self.assertRaises(AssertionError): self.config(['b'])

    def test_new_source_cannot_be_its_own_retained_actor(self):
        with self.assertRaises(AssertionError): self.config(['a', 'new'])

    def test_empty_required_scope_rejected(self):
        with self.assertRaises(AssertionError): self.config([], staged=())


if __name__ == '__main__': unittest.main()
