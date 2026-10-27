"""The availability adapter must retain every pre-existing browser check."""
from pathlib import Path
import unittest


class BrowserParity(unittest.TestCase):
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
