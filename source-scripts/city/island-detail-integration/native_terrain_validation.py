"""Validate source TIN publication against its exact rectangular parent replacement."""
import math,json,hashlib,copy
from pathlib import Path

def validate_native_mesh(patch,parent):
 mesh=patch.get('nativeMesh')
 if mesh is None:return
 from shapely.geometry import Polygon,box
 from shapely.ops import unary_union
 assert not patch.get('patches') and not patch.get('hydro'),'Native mesh cannot combine nested/water overrides'
 pos=mesh['position'];idx=mesh['index'];assert pos and len(pos)%3==0 and len(idx)%3==0
 assert all(isinstance(v,(int,float)) and math.isfinite(v) for v in pos),'Non-finite native terrain position'
 assert all(type(i) is int and 0<=i<len(pos)//3 for i in idx),'Invalid native terrain index'
 g=patch['meta']['georef'];x0=g['bE']-834500;z0=816500-g['bN'];x1=x0+(patch['w']-1)*g['aE'];z1=z0-(patch['h']-1)*g['aN'];extent=box(x0,z0,x1,z1)
 faces=[];edge_vertices=[]
 for i in range(0,len(pos),3):
  x,y,z=pos[i:i+3];assert x0-.002<=x<=x1+.002 and z0-.002<=z<=z1+.002,'Native mesh outside replacement extent'
  if min(abs(x-x0),abs(x-x1),abs(z-z0),abs(z-z1))<.002:edge_vertices.append((x,y,z))
 for i in range(0,len(idx),3):
  points=[(pos[j*3],pos[j*3+2]) for j in idx[i:i+3]];face=Polygon(points)
  if face.area>1e-10:faces.append(face)
 assert faces,'No native terrain surface'
 union=unary_union(faces);tolerance=max(.001,extent.area*1e-7)
 assert union.symmetric_difference(extent).area<tolerance,'Native mesh does not cover the exact parent rectangle'
 excess=sum(f.area for f in faces)-union.area
 if excess>=tolerance:
  approval=mesh.get('sourceOverlap');assert approval and approval.get('policy')=='highest-native-surface','Native terrain contains overlapping height surfaces'
  root=Path(__file__).resolve().parents[3];evidence=(root/approval['evidencePath']).resolve();assert evidence.is_relative_to(root)
  raw=evidence.read_bytes();assert hashlib.sha256(raw).hexdigest()==approval['evidenceSHA256'],'Native overlap evidence changed'
  audit=json.loads(raw);original=copy.deepcopy(patch);original['nativeMesh'].pop('sourceOverlap')
  assert hashlib.sha256((json.dumps(original,separators=(',',':'))+'\n').encode()).hexdigest()==audit['stagedGeometrySha256'],'Native overlap geometry changed after source review'
  assert abs(excess-approval['measuredProjectedExcessM2'])<1e-6 and abs(excess-audit['nativeProjectedExcessM2'])<1e-6,'Overlap exceeds verified original source facets'
  proof=audit['float32HighestRayAgreement'];assert proof['samples']>=1 and proof['maxError']<.01,'Native highest-surface ray agreement unverified'
  for source in audit['source']['files']:
   path=(root/source['path']).resolve();assert path.is_relative_to(root) and hashlib.sha256(path.read_bytes()).hexdigest()==source['sha256'],'Native overlap source changed'

 assert edge_vertices,'Native terrain has no parent-edge vertices'
 pg=parent['meta']['georef'];w=parent['w'];h=parent['h']
 def sample(x,z):
  c=(x+834500-pg['bE'])/pg['aE'];r=(816500-z-pg['bN'])/pg['aN'];i=max(0,min(w-2,math.floor(c)));j=max(0,min(h-2,math.floor(r)));u=c-i;v=r-j
  def at(k):
   rendered=parent.get('renderedElev',[]);a=rendered[k] if rendered else None
   return a if a is not None else max(1.2,parent['elev'][k]) if parent['elev'][k]>0 else -4
  a=at(j*w+i);b=at(j*w+i+1);d=at((j+1)*w+i);e=at((j+1)*w+i+1)
  return a+(b-a)*u+(d-a)*v if u+v<=1 else e+(d-e)*(1-u)+(b-e)*(1-v)
 assert max(abs(y-sample(x,z)) for x,y,z in edge_vertices)<.01,'Native terrain boundary does not join parent heights'
