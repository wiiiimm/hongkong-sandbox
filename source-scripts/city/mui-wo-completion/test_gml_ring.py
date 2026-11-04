import unittest,xml.etree.ElementTree as ET
import pathlib,sys
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent.parent/'tai-o-completion'))
from hydro_prepare import polygon_ring,G
def positions(node):
 values=[float(x) for x in node.text.split()]
 return [values[i:i+2] for i in range(0,len(values),2)]
def boundary(parts):
 b=ET.Element(G+'exterior');ring=ET.SubElement(b,G+'Ring')
 for values in parts:ET.SubElement(ET.SubElement(ET.SubElement(ring,G+'curveMember'),G+'LineString'),G+'posList').text=values
 return b
class RingTests(unittest.TestCase):
 def test_original_closed_list_unchanged(self):self.assertEqual(polygon_ring(boundary(['0 0 1 0 1 1 0 0']),positions),[[0,0],[1,0],[1,1],[0,0]])
 def test_multipart_ring_preserves_order_without_duplicate_join(self):self.assertEqual(polygon_ring(boundary(['0 0 1 0','1 0 1 1 0 0']),positions),[[0,0],[1,0],[1,1],[0,0]])
 def test_disconnected_parts_are_never_joined(self):
  with self.assertRaisesRegex(ValueError,'Disconnected'):polygon_ring(boundary(['0 0 1 0','9 9 1 1 0 0']),positions)
 def test_unclosed_ring_is_not_implicitly_closed(self):
  with self.assertRaisesRegex(ValueError,'explicitly closed'):polygon_ring(boundary(['0 0 1 0 1 1']),positions)
if __name__=='__main__':unittest.main()
