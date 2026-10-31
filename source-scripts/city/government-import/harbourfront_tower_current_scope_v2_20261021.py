"""Nominate every actor/form touching the complete expanded terrain replacement."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from heritage_saved_native_bounds_binding_v1_20261014 import closed_disjoint
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-harbourfront-tower-current-scope-v2-20261021';DOC=BASE/BATCH
assert not DOC.exists();refs=[Path(__file__)];pins={}
def take(name,p):
 _,ps=authenticate(BASE/name);k=str(p.relative_to(ROOT));assert digest(p.read_bytes())==ps[k];pins[k]=ps[k];refs.extend([BASE/name/'result.json',p]);return read(p)
iv='government-xl-harbourfront-current-inventory-v1-20261021';inventory=take(iv,BASE/iv/'complete-bounds.json.gz');assert len(inventory['rows'])==6820
manifestp=ROOT/'3d-viewer/city/data/manifest.json';manifest=take(iv,manifestp)
cn='government-xl-harbourfront-tower-private-wrapper-v3-20261021';assert take(cn,BASE/cn/'summary.json')['terrainValidationPassed'];candidates=take(cn,BASE/cn/'terrain-candidates.json');candidate=candidates[0];p=ROOT/candidate['path'];assert digest(p.read_bytes())==candidate['sha256'];refs.append(p);pins[candidate['path']]=candidate['sha256'];wrapper=read(p)
rootp=ROOT/'3d-viewer/city/data/terrain.json';root=read(rootp);refs.append(rootp);builder=module('harbourfront_scope_builder',HERE/'resolve-pass-indexed-parent-clipping.py');extent=list(builder.extent(wrapper['coarseCells'],root));records=[]
def walk(node,path):
 global extent
 g=node['meta']['georef'];bb=[g['bE']-834500,816500-g['bN'],g['bE']+(node['w']-1)*g['aE']-834500,816500-g['bN']-(node['h']-1)*g['aN']];r=dict(path=path,gridBounds=bb)
 if 'nativeMesh'in node:
  v=np.asarray(node['nativeMesh']['position']).reshape(-1,3);both=np.concatenate([v,v.astype('float32').astype('float64')]);lo=both.min(0);hi=both.max(0);pb=[lo[0],lo[2],hi[0],hi[2]];r['packedBounds']=pb;r['allPackedVertices']=len(v);extent=[min(extent[0],pb[0]),min(extent[1],pb[1]),max(extent[2],pb[2]),max(extent[3],pb[3])]
 records.append(r)
 for i,c in enumerate(node.get('patches',[])):walk(c,path+[i])
walk(wrapper,[]);native=[r for r in inventory['rows']if not closed_disjoint(r['completeFourWorldBounds'],extent)];forms=[]
for tile in manifest['tiles']:
 p=ROOT/'3d-viewer'/tile['url'];hits=[]
 for b in read(p)['buildings']:
  pts=[v for ring in b.get('rings',[])for v in ring]
  if not pts:continue
  v=np.asarray(pts);lo=v.min(0);hi=v.max(0)
  if not(hi[0]<extent[0]or lo[0]>extent[2]or hi[1]<extent[1]or lo[1]>extent[3]):hits.append(b)
 if hits:forms.extend(hits);refs.append(p)
assert len({b['uid']for b in forms})==len(forms)
candidates[0]['replaces']['retainedUids']=[r['uid']for r in native];candidates[0]['bounds']=extent
summary=dict(uids=['landsd/118230:0'],currentNativeActors=6820,replacedWrapper=candidate['replaces'],completeParentAndPackedExtent=extent,touchingNativeUids=[r['uid']for r in native],intersectingForms=len(forms),installationApproved=False,qualification='Full expanded parent coarse domain and every descendant literal/Float32 packed vertex, including unused vertices. Every touching installed actor retains whole-source regression obligations.')
save(DOC/'scope.json',summary);save(DOC/'terrain-hierarchy.json',records);save(DOC/'native-obligations.json.gz',native);save(DOC/'form-obligations.json.gz',forms);save(DOC/'terrain-candidates.json',candidates)
for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
r=module('harbourfront_scope_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'whole-expanded-whampoa-current-neighbour-scope',list(dict.fromkeys(refs)),summary);print(dict(jobId=r['jobId'],native=len(native),forms=len(forms),bounds=extent),flush=True)
