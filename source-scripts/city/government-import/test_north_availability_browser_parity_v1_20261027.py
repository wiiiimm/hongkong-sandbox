"""The availability adapter must retain every pre-existing browser check."""
from pathlib import Path
import unittest


class BrowserParity(unittest.TestCase):
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
