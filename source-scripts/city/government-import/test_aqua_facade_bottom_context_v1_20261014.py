import unittest,io,numpy as np
from aqua_facade_bottom_context_v1_20261014 import descriptor,shared_edges,draw_2d
class Context(unittest.TestCase):
    def test_exact_dyadic_normal_and_no_role_assignment(self):
        d=descriptor(7,[[0,.5,0],[1,.5,0],[0,.5,1]]);self.assertEqual(d['exactCrossNormal'],['0','-1','0']);self.assertEqual(d['exactYRange'],['1/2','1/2']);self.assertIsNone(d['sourceRoleAssigned'])
    def test_exact_edge_without_near_match(self):
        a=[[0,0,0],[1,0,0],[0,1,0]];b=[[1,0,0],[0,0,0],[0,-1,0]];self.assertEqual(len(shared_edges(a,b)),1);b[0][0]+=1e-12;self.assertEqual(shared_edges(a,b),[])
    def test_nonfinite_rejected(self):
        with self.assertRaises(AssertionError):descriptor(1,np.full((3,3),np.nan))
    def test_actual_2d_agg_no_geometry_recast(self):
        import matplotlib.pyplot as plt
        a=np.array([[[0,5,0],[1,5,0],[0,5,1]],[[0,5,0],[1,20,0],[1,5,0]],[[1,5,0],[1,20,0],[2,5,1]]],dtype='<f8');saved=a.tobytes();fig=draw_2d(a,[0],[2],[1])
        try:
            out=io.BytesIO();fig.savefig(out,format='png');self.assertTrue(out.getvalue().startswith(b'\x89PNG'));self.assertEqual(len(fig.axes),4);self.assertTrue(all(ax.name=='rectilinear'for ax in fig.axes));self.assertEqual(a.tobytes(),saved)
        finally:plt.close(fig)
if __name__=='__main__':unittest.main()
