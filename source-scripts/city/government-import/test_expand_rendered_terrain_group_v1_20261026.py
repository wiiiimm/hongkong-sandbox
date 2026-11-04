import unittest
from copy import deepcopy
from expand_rendered_terrain_group_v1_20261026 import extend_right,root_sample


def fixtures():
    root=dict(cell=10,w=4,h=3,elev=[2.]*12,renderedElev=[2.,5.,7.,9.,3.,10.,4.,5.,3.,6.,8.,9.],vegetation=[0]*12,meta=dict(georef=dict(aE=10,aN=-10,bE=834500,bN=816500,W=4,H=3)))
    group=dict(cell=5,w=3,h=3,coarseCells=[0,0,1,1],elev=[8.]*9,renderedElev=[8.]*9,vegetation=[1]*9,meta=dict(georef=dict(aE=5,aN=-5,bE=834500,bN=816500,W=3,H=3)),patches=[dict(id='exact-existing-child',coarseCells=[0,0,1,1])])
    return group,root


class ExpandTests(unittest.TestCase):
    def test_old_data_and_children_unchanged(self):
        group,root=fixtures();original=deepcopy(group)
        out,proof=extend_right(group,root,root_cells=[0,0,2,1])
        self.assertEqual(group,original);self.assertEqual(out['patches'],group['patches'])
        self.assertEqual(out['w'],5);self.assertEqual(proof['unchangedOldGridNodes'],9)
        for row in range(3):self.assertEqual(out['renderedElev'][row*5:row*5+3],[8.]*3)

    def test_existing_root_diagonal(self):
        _,root=fixtures()
        self.assertEqual(root_sample(root,12.5,2.5)[0],6.75)
        self.assertEqual(root_sample(root,17.5,7.5)[0],6.25)

    def test_other_patch_is_excluded(self):
        group,root=fixtures();out,proof=extend_right(group,root,root_cells=[0,0,2,1],other_root_cells=[[1,0,2,1]])
        self.assertEqual(proof['newMaskedCells'],4)
        self.assertEqual(out['patchExclusions'],[[2,0,4,1],[2,1,4,2]])

    def test_water_cells_are_excluded(self):
        group,root=fixtures();root['elev']=[0.]*12;root.pop('renderedElev')
        out,proof=extend_right(group,root,root_cells=[0,0,2,1])
        self.assertEqual(proof['newMaskedCells'],4)
        self.assertTrue(all(out['renderedElev'][r*5+3]==-4 for r in range(3)))

    def test_invalid_left_shift_refused(self):
        group,root=fixtures()
        with self.assertRaises(AssertionError):extend_right(group,root,root_cells=[-1,0,2,1])


if __name__=='__main__':unittest.main()
