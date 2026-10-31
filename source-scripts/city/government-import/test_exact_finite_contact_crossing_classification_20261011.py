from exact_finite_contact_crossing_classification_20261011 import classify
import unittest
A=[[0,0,0],[2,0,0],[0,2,0]]
CASES=[
 ([[.5,0,-1],[.5,0,1],[.5,2,0]],dict(dimension=1,exactPoints=[['1/2','0','0'],['1/2','3/2','0']]),'proper-noncoplanar-triangle-relative-interior-crossing'),
 ([[0,0,0],[2,0,0],[0,0,1]],dict(dimension=1,exactPoints=[['0','0','0'],['2','0','0']]),'noncoplanar-boundary-contact'),
 (A,dict(dimension=2,exactPoints=[['0','0','0'],['2','0','0'],['0','2','0']]),'coplanar-positive-area-overlap'),
 ([[0,0,0],[2,0,0],[1,-1,0]],dict(dimension=1,exactPoints=[['0','0','0'],['2','0','0']]),'coplanar-line-or-point-contact'),
 ([[0,0,0],[0,0,0],[1,0,0]],dict(dimension=1,exactPoints=[['0','0','0'],['1','0','0']]),'degenerate-primitive-contact-no-structural-credit'),
]
def test_actual_roles_and_reversed_winding(b,c,kind):
 for aa,bb in [(A,b),(A[::-1],b),(A,b[::-1])]:
  p=classify(aa,bb,c);assert p['classification']==kind and not p['volumetricCollisionProved']and not p['structuralSupportCredit']
def test_tiny_real_triangle_not_degenerate():
 tiny=[[0,0,0],[2**-100,0,0],[0,2**-100,0]]
 p=classify(tiny,tiny,dict(dimension=2,exactPoints=[['0','0','0'],[str(2**-100),'0','0'],['0',str(2**-100),'0']]))
 assert p['classification']=='coplanar-positive-area-overlap'

class ContactTests(unittest.TestCase):
 def test_actual_roles(self):
  for b,c,kind in CASES:
   with self.subTest(kind=kind):test_actual_roles_and_reversed_winding(b,c,kind)
 def test_tiny_real_triangle(self):test_tiny_real_triangle_not_degenerate()

if __name__=="__main__":unittest.main()
