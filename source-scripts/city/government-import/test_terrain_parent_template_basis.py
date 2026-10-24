import copy,unittest
import numpy as np
import resolve_pass_indexed_parent_clipping_v2 as builder
from terrain_parent_template_basis_v1 import validated_template_faces

class TemplateBasisTests(unittest.TestCase):
    def setUp(self):
        self.parent=dict(w=3,h=3,cell=70,elev=[5.]*9,vegetation=[0]*9,
          meta=dict(georef=dict(aE=70,aN=-70,bE=834500,bN=816500)))
        self.current=np.array([[[0.,4.,0.],[70.,4.,0.],[0.,4.,70.]],
                              [[70.,4.,0.],[70.,4.,70.],[0.,4.,70.]]])
        self.template=builder.make_patch(dict(cells=[0,0,1,1],uids=['landsd/123:0']),
            self.parent,self.current,[],parent_sha256='0'*64)
    def test_keep_validated_return_instead_of_reintroducing_current_edge_mismatch(self):
        before=copy.deepcopy(self.template)
        faces=validated_template_faces(self.template,self.parent)
        self.assertEqual(self.template,before)
        candidate=copy.deepcopy(self.template)
        candidate['nativeMesh']['position']=faces.reshape(-1).tolist()
        candidate['nativeMesh']['index']=list(range(faces.size//3))
        builder.validate_patch(candidate,self.parent)
        candidate['nativeMesh']['position']=self.current.reshape(-1).tolist()
        candidate['nativeMesh']['index']=list(range(self.current.size//3))
        with self.assertRaisesRegex(AssertionError,'boundary does not join'):
            builder.validate_patch(candidate,self.parent)
    def test_changed_boundary_is_not_approved(self):
        values=self.template['nativeMesh']['position']
        edge=next(i for i in range(0,len(values),3) if values[i]==0. or values[i+2]==0.)
        values[edge+1]-=.5
        with self.assertRaisesRegex(AssertionError,'boundary does not join'):
            validated_template_faces(self.template,self.parent)
    def test_returned_geometry_does_not_mutate_template(self):
        before=copy.deepcopy(self.template)
        faces=validated_template_faces(self.template,self.parent)
        faces[0,0,1]=99
        self.assertEqual(self.template,before)
