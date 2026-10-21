"""Account for the whole live Central wrapper before adding a bounded terrain child."""
from pathlib import Path
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from heritage_saved_native_bounds_binding_v1_20261014 import closed_disjoint
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-central-piers-current-scope-v1-20261021';DOC=BASE/BATCH
assert not DOC.exists();invdir=BASE/'government-xl-china-merchants-current-inventory-v1-20261021';receipt,pins=authenticate(invdir)
for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
inv=read(invdir/'complete-bounds.json.gz');assert len(inv['rows'])==6818
manifestp=ROOT/'3d-viewer/city/data/manifest.json';manifest=read(manifestp);parentp=ROOT/'3d-viewer/city/data/terrain.json';parent=read(parentp);builder=module('china_scope_current',HERE/'resolve-pass-indexed-parent-clipping.py')
url='city/data/government-native-star-ferry-original-v1-20261019.json';assert any(e['url']==url for e in manifest['terrainPatches']);wp=ROOT/'3d-viewer'/url;wrapper=read(wp);extent=list(builder.extent(wrapper['coarseCells'],parent));records=[]
childDomain=shapely.box(87.5,-22.5,287.5,177.5)
def walk(node,path):
 global extent
 g=node['meta']['georef'];o=parent['meta']['origin'];bounds=[g['bE']-o[0],o[1]-g['bN'],g['bE']+(node['w']-1)*g['aE']-o[0],o[1]-(g['bN']+(node['h']-1)*g['aN'])]
 r=dict(path=path,id=node.get('id'),gridBounds=bounds,coarseCells=node.get('coarseCells'))
 if 'nativeMesh'in node:
  v=np.asarray(node['nativeMesh']['position']).reshape(-1,3);both=np.concatenate([v,v.astype('float32').astype('float64')]);lo=both.min(0);hi=both.max(0);pb=[lo[0],lo[2],hi[0],hi[2]];r.update(packedBounds=pb,packedVertices=len(v),drawnTriangles=len(node['nativeMesh']['index'])//3)
  extent=[min(extent[0],pb[0]),min(extent[1],pb[1]),max(extent[2],pb[2]),max(extent[3],pb[3])]
 if path:
  r['localChildGridOverlapM2']=shapely.box(*bounds).intersection(childDomain).area
  r['localChildPackedOverlapM2']=shapely.box(*r.get('packedBounds',bounds)).intersection(childDomain).area
 records.append(r)
 for i,c in enumerate(node.get('patches',[])):walk(c,path+[i])
walk(wrapper,[])
overlaps=[r for r in records if r['path']and (r['localChildGridOverlapM2']>0 or r['localChildPackedOverlapM2']>0)]
assert [r['path']for r in overlaps]==[[6]], 'unexpected-existing-child-overlap'
assert childDomain.covers(shapely.box(*overlaps[0]['gridBounds']))
assert childDomain.covers(shapely.box(*overlaps[0]['packedBounds']))
native=[r for r in inv['rows']if not closed_disjoint(r['completeFourWorldBounds'],extent)]
refs=[Path(__file__),invdir/'result.json',invdir/'complete-bounds.json.gz',manifestp,parentp,wp]+[ROOT/p for p in pins];forms=[]
for tile in manifest['tiles']:
 p=ROOT/'3d-viewer'/tile['url'];hits=[]
 for b in read(p)['buildings']:
  pts=[v for ring in b.get('rings',[])for v in ring]
  if not pts:continue
  v=np.asarray(pts);lo=v.min(0);hi=v.max(0)
  if not(hi[0]<extent[0]or lo[0]>extent[2]or hi[1]<extent[1]or lo[1]>extent[3]):hits.append(b)
 if hits:forms.extend(hits);refs.append(p)
assert len({b['uid']for b in forms})==len(forms)
summary=dict(uids=['landsd/213352:0','landsd/285475:0'],currentNativeActors=6818,replacedWrapper=dict(url=url,sha256=digest(wp.read_bytes())),regionalCoarseCells=wrapper['coarseCells'],completeParentAndPackedExtent=extent,localChildBounds=list(childDomain.bounds),existingChildrenDisjointFromLocalChild=False,overlappingChildren=overlaps,proposedReplacedChildIndex=6,touchingNativeUids=[r['uid']for r in native],intersectingForms=len(forms),installationApproved=False,qualification='Whole replaced parent domain and every descendant literal/Float32 packed extent. All nominated actors require complete regression; disjoint child domains do not grant acceptance.')
save(DOC/'scope.json',summary);save(DOC/'terrain-hierarchy.json',records);save(DOC/'native-obligations.json.gz',native);save(DOC/'form-obligations.json.gz',forms)
for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
r=module('china_scope_freeze2',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'whole-current-wrapper-regression-obligations',list(dict.fromkeys(refs)),summary)
print(dict(jobId=r['jobId'],native=len(native),forms=len(forms),extent=extent,replacedChildIndex=6),flush=True)
