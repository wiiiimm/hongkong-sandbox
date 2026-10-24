"""Byte-identical clipping on actual terrain and complete near-edge counterexamples."""
import importlib.util,unittest,numpy as np,sys
from run import ROOT,HERE,read,digest
from parent_cell_clip_broad_phase_20261010 import ParentCellClipIndex
sys.path.insert(0,str(HERE.parent/'assembly-support-review'));import exact_tin as exact
def fixture():
 g=read(ROOT/'3d-viewer/city/data/government-native-163705-0.json')['meta']['georef'];cells=[]
 for r in range(10,16):
  for c in range(55,61):
   a=np.array([g['bE']+c*g['aE']-834500,816500-g['bN']+r*abs(g['aN'])]);b=a+[g['aE'],0];d=a+[0,abs(g['aN'])];e=a+[g['aE'],abs(g['aN'])];cells.extend([np.array([a,b,d]),np.array([b,e,d])])
 return cells
def bytes_for(polys):return [np.asarray(p,dtype='<f8').tobytes() for p in polys if len(p)>=3]
class BroadPhase(unittest.TestCase):
 def check(self,poly,cells=None):
  cells=fixture() if cells is None else cells;index=ParentCellClipIndex(cells);allp=[exact.parent_clip(poly,t) for t in cells];fast=index.clip(poly,exact.parent_clip);self.assertEqual(bytes_for(allp),bytes_for(fast));self.assertEqual(index.candidate_ids(poly),sorted(index.candidate_ids(poly)))
 def test_actual_original_finite_terrain_polygons(self):
  p=ROOT/'source-scripts/city/government-import/local/government-xl-tung-sing-two-nested-original-physical-v3-20261010/government-native-53800-0.json';o=read(p);v=np.asarray(o['nativeMesh']['position'],float).reshape(-1,3);faces=v[np.asarray(o['nativeMesh']['index']).reshape(-1,3)];cells=fixture();box=np.asarray(cells).reshape(-1,2);lo,hi=box.min(axis=0)-1,box.max(axis=0)+1;selected=faces[(faces[:,:,0].max(axis=1)>=lo[0])&(faces[:,:,0].min(axis=1)<=hi[0])&(faces[:,:,2].max(axis=1)>=lo[1])&(faces[:,:,2].min(axis=1)<=hi[1])];self.assertGreater(len(selected),100)
  for face in selected[::max(1,len(selected)//100)]:self.check(list(face),cells)
 def test_exact_cell_boundary(self):
  a=fixture()[0];self.check([np.array([a[0,0],3,a[0,1]]),np.array([a[1,0],4,a[1,1]]),np.array([a[2,0],5,a[2,1]])])
 def test_epsilon_near_external_edge(self):
  a=fixture()[0];x,z=a[0];self.check([np.array([x-1e-10,3,z]),np.array([x-1e-10,4,z+1]),np.array([x-1e-10,5,z+2])])
 def test_far_external_polygon(self):self.check([np.array([1000.,3,2000]),np.array([1001.,4,2000]),np.array([1000.,5,2001])])
 def test_degenerate_vertical_polygon(self):
  a=fixture()[0];x,z=a[0];self.check([np.array([x,3,z]),np.array([x,4,z]),np.array([x,5,z+1])])
 def test_disjoint_corner(self):
  a=fixture()[0];x,z=a[0];self.check([np.array([x-2,3,z-2]),np.array([x-1,4,z-2]),np.array([x-2,5,z-1])])
 def test_non_axis_cell_rejected(self):
  a=np.asarray(fixture());a[0,1,1]+=.2
  with self.assertRaises(AssertionError):ParentCellClipIndex(a)
 def test_bad_nonfinite_cell_rejected(self):
  a=np.asarray(fixture());a[0,0,0]=np.nan
  with self.assertRaises(AssertionError):ParentCellClipIndex(a)
if __name__=='__main__':unittest.main()
