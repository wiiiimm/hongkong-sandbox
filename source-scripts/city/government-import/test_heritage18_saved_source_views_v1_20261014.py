"""Exact saved18 grouping and tiny synthetic Agg projection smoke only."""
import copy,gzip,json,tempfile,unittest
from pathlib import Path
import heritage18_saved_orthographic_visuals_v1_20261014 as v
import heritage165054_two_tin_nearwater_bare_nomination_v1_20261014 as source

class SourceViews(unittest.TestCase):
    def packet(self):return source.read(source.DOC/'exact18-four-world-source-context.json.gz')
    def test_actual_saved18_and_all22_partition_without_role_credit(self):
        p=self.packet();groups=v.bind_groups(p);self.assertEqual(sum(len(ids)for _,ids in groups),18);self.assertEqual(len(p['all22SavedBelowMinus05WitnessesVerbatim']),22)
    def test_missing_or_role_relabelled_source_packet_fails_closed(self):
        for key,value in [('sourceFaceIDs',self.packet()['sourceFaceIDs'][:-1]),('sourceRoleAssigned',True),('warningResolved',True)]:
            p=self.packet();p[key]=value
            with self.assertRaises(AssertionError):v.bind_groups(p)
    def test_actual_agg_solid_edge_projection_emits_png(self):
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import numpy as np
        tri=np.asarray([[[0,0,0],[1,0,0],[0,1,1]]],dtype=float)
        with tempfile.TemporaryDirectory()as tmp:
            fig,ax=plt.subplots(figsize=(2,2),dpi=64);v.emit_projection(ax,tri,tri,tri,[[0,0,0]],(0,1));p=Path(tmp)/'synthetic.png';fig.savefig(p);plt.close(fig)
            self.assertTrue(p.read_bytes().startswith(b'\x89PNG\r\n\x1a\n'));self.assertGreater(p.stat().st_size,500)
if __name__=='__main__':unittest.main()
