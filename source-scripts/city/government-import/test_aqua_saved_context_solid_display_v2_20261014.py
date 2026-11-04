import io,unittest,numpy as np
from test_aqua_saved_context_display_v1_20261014 import Display
from aqua_saved_context_solid_display_v2_20261014 import solid_collection
class ActualAggSmoke(unittest.TestCase):
    def test_exact_solid_no_edge_and_transparent_edge_draw(self):
        import matplotlib;matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        tri=np.array([[[0.,0.,0.],[1.,0.,0.],[0.,1.,1.]],[[0.,0.,0.],[0.,1.,1.],[-1.,0.,0.]]]);saved=tri.tobytes()
        fig=plt.figure(figsize=(3,2),dpi=100)
        try:
            ax=fig.add_subplot(111,projection='3d');ax.add_collection3d(solid_collection(tri,'#b9bec2'))
            ax.add_collection3d(solid_collection(tri,'#c7b78c',.12,'#988766',.12));ax.set_xlim(-1,1);ax.set_ylim(0,1);ax.set_zlim(0,1)
            out=io.BytesIO();fig.savefig(out,format='png',dpi=100);self.assertTrue(out.getvalue().startswith(b'\x89PNG\r\n\x1a\n'));self.assertEqual(fig.canvas.get_width_height(),(300,200));self.assertEqual(tri.tobytes(),saved)
        finally:plt.close(fig)
if __name__=='__main__':unittest.main()
