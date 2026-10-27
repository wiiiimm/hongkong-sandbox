import importlib.util,json,sys,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from run import save,read,digest
from exact_original_triangle_pair_column_gap_20261010 import verify
HERE=Path(__file__).resolve().parent

class StreamReuse(unittest.TestCase):
 def execute(self,version,distinct):
  with tempfile.TemporaryDirectory() as temp:
   root=Path(temp);base=root/'docs/astra-city/government-import';local=root/'local';asset=root/'asset';asset.write_bytes(b'fixture');sha=digest(asset.read_bytes())
   source=np.array([[[1,2,1],[2,2,1],[1,2,2]],[[2,2,1],[2,2,2],[1,2,2]]],dtype='float64')
   ground=source.copy();ground[:,:,1]=3
   literal=source.copy();literal[0,0,1]+=1e-12
   left=source.copy();balanced=source.copy()
   if distinct:left[0,1,1]+=2e-12;balanced=source[::-1].copy()
   attrs=dict(sourceSHA256=sha,completeOriginalIndex=list(range(6)),completeLiteralWorldPosition=literal.reshape(-1).tolist(),completeExplicitLeftAssociatedFloat32WorldPosition=left.reshape(-1).tolist(),completeExplicitBalancedFloat32WorldPosition=balanced.reshape(-1).tolist(),uid='landsd/1:0')
   save(base/'runtime/selection.json.gz',dict(rows=[dict(uid='landsd/1:0',sourceSHA256=sha,triangles=2,candidate=dict(path='asset'))]))
   save(local/'runtime/runtime-geometry.json.gz',dict(rows=[dict(uid='landsd/1:0',sourceSHA256=sha,drawnGroundGeometry=ground.reshape(-1).tolist())]))
   save(base/'attributes/attributes.json.gz',dict(rows=[attrs]));pins={str(p.relative_to(root)):digest(p.read_bytes()) for p in root.rglob('*') if p.is_file()}
   path=HERE/('selected_original_four_world_low_face_context_'+version+'.py');spec=importlib.util.spec_from_file_location('low_'+version,path);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
   calls=[]
   def counted(*args):calls.append(1);return verify(*args)
   def freeze_module(*args):return SimpleNamespace(freeze=lambda *a:None)
   with patch.multiple(mod,ROOT=root,HERE=root,authenticate=lambda p:({},pins),decode_original_world_triangles=lambda raw:source.copy(),module=freeze_module,verify=counted),patch.object(sys,'argv',['test','--batch','government-xl-test','--runtime','runtime','--attributes','attributes','--uid','landsd/1:0']):mod.main()
   out=base/'government-xl-test';return {p.name:read(p) for p in out.iterdir()},len(calls)
 def test_identical_streams_reuse_exact_complete_evidence(self):
  old,old_calls=self.execute('v1_20261024',False);new,new_calls=self.execute('v2_20261027',False)
  self.assertEqual(old,new);self.assertLess(new_calls,old_calls)
 def test_perturbed_vertices_and_reordered_faces_remain_independent(self):
  old,old_calls=self.execute('v1_20261024',True);new,new_calls=self.execute('v2_20261027',True)
  self.assertEqual(old,new);self.assertEqual(new_calls,old_calls)
if __name__=='__main__':unittest.main()
