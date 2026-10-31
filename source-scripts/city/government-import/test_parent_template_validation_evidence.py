import unittest
import numpy as np
import resolve_pass_indexed_parent_clipping_v2 as builder


class ParentTemplateEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.parent = dict(w=3,h=3,cell=70,elev=[5.]*9,vegetation=[0]*9,
            meta=dict(georef=dict(aE=70,aN=-70,bE=834500,bN=816500)))
        self.faces = np.array([[[0.,5.,0.],[70.,5.,0.],[0.,5.,70.]],
                               [[70.,5.,0.],[70.,5.,70.],[0.,5.,70.]]])

    def build(self, callback, faces=None):
        return builder.make_patch(dict(cells=[0,0,1,1],uids=['landsd/123:0']),
            self.parent, self.faces if faces is None else faces, [],
            parent_sha256='0'*64, prepare_validation=callback)

    def test_callback_runs_before_ordinary_validated_return(self):
        calls=[]
        patch=self.build(lambda p:calls.append(len(p['nativeMesh']['index'])))
        self.assertEqual(len(calls),1)
        builder.validate_patch(patch,self.parent)

    def test_callback_cannot_change_geometry_or_parent_metadata(self):
        for change in [lambda p:p['nativeMesh']['position'].__setitem__(0,1.),
                       lambda p:p['meta']['georef'].__setitem__('bE',834501)]:
            with self.assertRaisesRegex(AssertionError,'callback changed'):
                self.build(change)

    def test_callback_cannot_skip_overlap_validation(self):
        second=self.faces.copy();second[:,:,1]+=.5
        with self.assertRaisesRegex(AssertionError,'overlapping height surfaces'):
            self.build(lambda p:None,np.concatenate([self.faces,second]))

    def test_below_clamp_rejected_before_callback(self):
        calls=[];faces=self.faces.copy();faces[:,:,1]=.8
        with self.assertRaisesRegex(AssertionError,'near-water-clamp'):
            self.build(lambda p:calls.append(True),faces)
        self.assertEqual(calls,[])
