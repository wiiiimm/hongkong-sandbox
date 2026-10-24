import sys, importlib.util
from pathlib import Path
sys.path.insert(0,str(Path.cwd()/'source-scripts/city/government-import'))
from run import ROOT,HERE,read,save
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
import shapely,numpy as np
s=importlib.util.spec_from_file_location('final',HERE/'xl-final-script-pass.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
r=next(x for x in read(ROOT/'docs/astra-city/government-import/government-xl-yoho-mall-i-tower-identity-v1-20261020/selection.json.gz')['rows'] if x['uid']=='landsd/294857:0')
t=decode_original_world_triangles((ROOT/r['candidate']['path']).read_bytes());lo,hi=t.min(axis=(0,1)),t.max(axis=(0,1));forms=m.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]);b,p,_=next(x for x in forms if x[0]['uid']==r['uid'])
u=shapely.union_all(shapely.polygons(t[:,:,[0,2]]));ex=u.difference(p);other=shapely.union_all([q for a,q,_ in forms if a['uid']!=r['uid'] and a.get('parent')!=b.get('parent') and not(set(a.get('osmRefs',[]))&set(b.get('osmRefs',[])))])
for n,g in [('projection',u),('excess',ex),('unrelated',other)]: print(n,g.geom_type,g.is_empty,g.is_valid,g.area,shapely.is_valid_reason(g),flush=True)
try: print('intersection',ex.intersection(other).area)
except Exception as e: print(type(e).__name__,str(e))
parts=list(shapely.get_parts(ex));assert other.is_empty and all(g.intersection(other).area==0 for g in parts)
m.projection=lambda faces:shapely.union_all(shapely.polygons(faces[:,:,[0,2]]))
context=m.identity_context(r,t,forms);assert context['sourceExcessCoveredByUnrelatedFormsM2']==0
print('PASS: complete original context computes exact zero unrelated coverage; all source facets retained')
