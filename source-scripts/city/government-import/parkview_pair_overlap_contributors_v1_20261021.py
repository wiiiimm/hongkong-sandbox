from pathlib import Path
from run import ROOT,HERE,read,save,digest
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
import shapely
from shapely.geometry import Polygon
base=ROOT/'docs/astra-city/government-import'
from china_ferry_current_foundations_v1_20261020 import authenticate
folder=base/'government-xl-parkview-four-raw-identity-v1-20261021'
_,pins=authenticate(folder)
selection=folder/'selection.json.gz'
assert digest(selection.read_bytes())==pins[str(selection.relative_to(ROOT))]
refs=[Path(__file__),selection,folder/'result.json']
s=read(selection)
rows=[r for r in s['rows'] if r['uid'] in {'landsd/253980:0','landsd/255260:0'}]
forms={};projections=[];targets=[]
f=module('audit_forms',HERE/'xl-final-script-pass.py')
for r in rows:
 p=ROOT/r['candidate']['path'];assert digest(p.read_bytes())==r['sourceSHA256']
 refs.append(p)
 t=decode_original_world_triangles(p.read_bytes());projections.append(shapely.union_all(shapely.polygons(t[:,:,[0,2]])))
 b=r['source']['building'];targets.append(Polygon(b['rings'][0],b['rings'][1:]))
 lo,hi=t.min((0,1)),t.max((0,1))
 for b,_,url in f.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]):forms[b['uid']]=b;refs.append(ROOT/'3d-viewer'/url)
excess=shapely.union_all(projections).difference(shapely.union_all(targets)); parents={r['source']['building'].get('parent') for r in rows};uids={r['uid'] for r in rows}
out=[]
for b in forms.values():
 if b['uid'] in uids or b.get('parent') in parents:continue
 a=excess.intersection(Polygon(b['rings'][0],b['rings'][1:])).area
 if a>0:out.append(dict(uid=b['uid'],area=a,parent=b.get('parent'),structureType=b.get('structureType'),buildingCSUID=b.get('buildingCSUID'),name=b.get('name')))
print(out,flush=True)
batch='government-xl-parkview-pair-overlap-contributors-v1-20261021'
assert not (base/batch).exists()
result=dict(uids=sorted(uids),contributors=out,identityApproved=False,installationApproved=False,qualification='Read-only attribution of the unchanged raw unrelated-footprint diagnostic. Shared podium relation differs from tower OSM parent; no threshold waiver or approval.')
save(base/batch/'contributors.json',result)
refs.extend([HERE/'xl-final-script-pass.py',HERE/'exact_packed_world_geometry_20261009.py'])
module('overlap_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'original-pair-overlap-attribution',list(dict.fromkeys(refs)),result)
