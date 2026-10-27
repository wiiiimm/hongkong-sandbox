"""The availability adapter must retain every pre-existing browser check."""
from pathlib import Path
import re
import unittest


class BrowserParity(unittest.TestCase):
    def test_v20_keeps_all_existing_assertions_and_uses_actual_selection(self):
        folder = Path(__file__).parent
        before = (folder / 'ronsdale_three_live_browser_v19_20261027.mjs').read_text()
        after = (folder / 'ronsdale_three_live_browser_v20_20261027.mjs').read_text()
        assertions = re.findall(r'assert(?:\.[A-Za-z]+)?\([^;]+?\);', before)
        self.assertGreater(len(assertions), 40)
        for assertion in assertions:
            self.assertIn(assertion, after)
        self.assertIn("window.__city.state.selectedId!==uid", after)
        self.assertIn('else r.closeSelection();', after)
        self.assertIn('report.retainedDeselectionFallbacks.push(fallback)', after)
        self.assertNotRegex(after, r'\.limits\.[A-Za-z]+\s*=(?!=)')
        self.assertNotRegex(after, r'window\.__city\.state\.selectedId\s*=(?!=)')

    def test_v19_adds_observations_without_changing_checks(self):
        folder = Path(__file__).parent
        before = (folder / 'ronsdale_three_live_browser_v18_20261027.mjs').read_text()
        after = (folder / 'ronsdale_three_live_browser_v19_20261027.mjs').read_text()
        lines = after.splitlines(keepends=True)
        self.assertTrue(lines[0].startswith('// V19:'))
        after = ''.join(lines[1:])
        start = after.index('.catch(async error=>{report.retainedActorTimeout=')
        end = after.index('throw error;});', start) + len('throw error;});')
        after = after[:start] + ';' + after[end:]
        observation = 'runtimeBudgetObservation:{selectedId:window.__city.state.selectedId,stats:r.officialModels.stats,wanted:r.officialModels.cache.wanted.includes(uid),camera:r.camera.position.toArray(),target:r.controls.target.toArray()},'
        self.assertEqual(after.count(observation), 1)
        self.assertEqual(after.replace(observation, ''), before)

    def test_v18_retained_only_mode_preserves_all_retained_checks(self):
        folder = Path(__file__).parent
        before = (folder / 'ronsdale_three_live_browser_v17_20261027.mjs').read_text()
        after = (folder / 'ronsdale_three_live_browser_v18_20261027.mjs').read_text()
        lines = after.splitlines(keepends=True)
        self.assertTrue(lines[0].startswith('// V18:'))
        after = ''.join(lines[1:])
        replacements = [
            ("assert((config.retainedOnly===true&&Array.isArray(config.browserUids)&&config.browserUids.length===0)||(browserModels.length>0&&(!config.browserUids||browserModels.length===config.browserUids.length)));",
             "assert(browserModels.length>0&&(!config.browserUids||browserModels.length===config.browserUids.length));"),
            ("if(config.retainedOnly===true)assert(requiredUids.size>0&&Array.isArray(config.failureTestUids)&&config.failureTestUids.length===0);\n", ''),
            ('const report={mode,retainedOnly:config.retainedOnly===true,newSourceAcceptance:false,views:[]', 'const report={mode,views:[]'),
        ]
        for changed, original in replacements:
            self.assertEqual(after.count(changed), 1)
            after = after.replace(changed, original)
        self.assertEqual(after, before)

    def test_v17_retains_v16_checks_and_adds_only_source_visibility(self):
        folder = Path(__file__).parent
        before = (folder / 'ronsdale_three_live_browser_v16_20261027.mjs').read_text()
        after = (folder / 'ronsdale_three_live_browser_v17_20261027.mjs').read_text()
        lines = after.splitlines(keepends=True)
        self.assertTrue(lines[0].startswith('// V17:'))
        self.assertIn('import {installSourcePixelWitness}', lines[1])
        after = ''.join(lines[2:])
        additions = [
            ' await page.evaluate(installSourcePixelWitness);\n',
            '  if(config.autoVisibleCamera)await page.evaluate(uid=>window.__portChooseVisibleCamera(uid),model.uid);\n',
            'if(config.autoVisibleCamera)await page.evaluate(uid=>window.__portChooseVisibleCamera(uid),form.uid);',
            "assert(state.sourcePixelVisibility.visiblePixels>=32,'Original target is occluded in exported view: '+model.uid);",
            "assert(state.sourcePixelVisibility.visiblePixels>=32,'Retained target is occluded in exported view: '+form.uid);",
        ]
        for addition in additions:
            self.assertEqual(after.count(addition), 1)
            after = after.replace(addition, '')
        witness = 'sourcePixelVisibility:window.__portSourceVisibility(uid),'
        self.assertEqual(after.count(witness), 2)
        after = after.replace(witness, '')
        self.assertEqual(after, before)

    def test_v16_retains_v15_verbatim_except_exact_overlay_routes(self):
        folder = Path(__file__).parent
        before = (folder / 'ronsdale_three_live_browser_v15_20261026.mjs').read_text()
        after = (folder / 'ronsdale_three_live_browser_v16_20261027.mjs').read_text()
        lines = after.splitlines(keepends=True)
        self.assertTrue(lines[0].startswith('// V16:'))
        after = ''.join(line for line in lines[1:] if not line.startswith('  for(const overlay of config.availabilityOverlays||[]){const before='))
        inserted = "for(const overlay of config.availabilityOverlays||[]){assert.equal(m.officialModelCatalogues.filter(u=>u===overlay.url).length,1);m.officialModelCatalogues=m.officialModelCatalogues.map(u=>u===overlay.url?overlay.destination:u);}"
        self.assertEqual(after.count(inserted), 1)
        self.assertEqual(after.replace(inserted, ''), before)


if __name__ == '__main__':
    unittest.main()
