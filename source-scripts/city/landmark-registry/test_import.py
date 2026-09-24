import unittest
from import_tallest import Tables,expand
class TableTests(unittest.TestCase):
 def test_rowspan_carries_fields_without_shifting_names(self):
  p=Tables();p.feed('<table><tr><th>Rank</th><th>Name</th><th>Height</th></tr><tr><td rowspan="2">1</td><td>North</td><td rowspan="2">200</td></tr><tr><td>South</td></tr></table>')
  rows=expand(p.tables[0]);self.assertEqual([[c['text'] for c in r] for r in rows[1:]],[['1','North','200'],['1','South','200']])
 def test_citations_and_css_are_not_building_names(self):
  p=Tables();p.feed('<table><tr><td>Tower<sup>[1]</sup><style>.fake {}</style><br>North</td></tr></table>');self.assertEqual(expand(p.tables[0])[0][0]['text'],'Tower North')
if __name__=='__main__':unittest.main()
