"""Exact original Star Ferry / installed source projection separation diagnostics."""
from pathlib import Path
import numpy as np,shapely
from shapely.geometry import box
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-star-ferry-retained-projection-v1-20261019';DOC=BASE/BATCH;SCOPE=BASE/'government-xl-remaining-two-current-scope-v1-20261019'
assert not DOC.exists();receipt=read(SCOPE/'result.json');refs=[Path(__file__),SCOPE/'result.json'];pins={e['path']:e['sha256']for e in receipt['evidenceRefs']}
with connect()as c:
 c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
scope=next(r for r in read(SCOPE/'scope.json')['rows']if r['uid']=='landsd/210032:0');parent_info=scope['overlappingInstalledTerrain'][0];parent=read(ROOT/'3d-viewer'/parent_info['url']);cells=scope['overlappingInstalledTerrain'][0]['nestedReplacementCells']
retained=[c for c in parent['patches']if c['id']in {'government-native-205767-0','government-native-central-hullett-house'}];assert len(retained)==2
for c in retained:cells=[min(cells[0],c['coarseCells'][0]),min(cells[1],c['coarseCells'][1]),max(cells[2],c['coarseCells'][2]),max(cells[3],c['coarseCells'][3])]
builder=module('star_retained_builder',HERE/'resolve-pass-indexed-parent-clipping.py');bounds=builder.extent(cells,parent)
row=next(r for r in read(BASE/'government-xl-next-five-current-terrain-v1-20261018/selection.json.gz')['rows']if r['uid']=='landsd/210032:0')
def projection(raw):
 t=decode_original_world_triangles(raw);xz=t[:,:,[0,2]]
 return shapely.union_all([shapely.union_all(shapely.polygons(xz)),shapely.union_all(shapely.linestrings(np.concatenate([xz,xz[:,:1]],axis=1))),shapely.union_all(shapely.points(xz.reshape(-1,2)))])
p=ROOT/row['candidate']['path'];assert digest(p.read_bytes())==row['sourceSHA256'];source=projection(p.read_bytes());refs.append(p);actors=[]
from heritage_saved_native_bounds_binding_v1_20261014 import closed_disjoint
wanted={r['uid']for r in read(SCOPE/'complete-bounds.json.gz')['rows']if not closed_disjoint(r['completeFourWorldBounds'],bounds)}
for url in read(ROOT/'3d-viewer/city/data/manifest.json')['officialModelCatalogues']:
 p=ROOT/'3d-viewer'/url
 for m in read(p)['models']:
  if m['uid']not in wanted:continue
  asset=p.parent/m['asset'];raw=asset.read_bytes();assert digest(raw)==m['sha256'];other=projection(raw);actors.append(dict(uid=m['uid'],sourceSHA256=m['sha256'],sourceProjectionIntersectionM2=source.intersection(other).area,sourceProjectionDistanceM=source.distance(other),sourceMarginIntersectionM2=source.buffer(1,join_style='mitre').intersection(other).area));refs.extend([p,asset])
assert {r['uid']for r in actors}==wanted
others=[c['id']for c in parent['patches']if c not in retained and min(cells[2],c['coarseCells'][2])>max(cells[0],c['coarseCells'][0])and min(cells[3],c['coarseCells'][3])>max(cells[1],c['coarseCells'][1])]
save(DOC/'projection-checks.json',dict(uid=row['uid'],sourceSHA256=row['sourceSHA256'],mergedCells=cells,mergedExtent=bounds,retainedChildIds=[c['id']for c in retained],otherOverlappingChildIds=others,actors=actors,installationApproved=False))
refs.extend([HERE/'exact_packed_world_geometry_20261009.py',HERE/'heritage_saved_native_bounds_binding_v1_20261014.py',HERE/'resolve-pass-indexed-parent-clipping.py'])
module('star_projection_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'star-ferry-retained-exact-source-projection-separation',list(dict.fromkeys(refs)),dict(uids=[row['uid']],actors=actors,otherOverlappingChildIds=others,installationApproved=False))
print(dict(actors=actors,otherChildren=others),flush=True)
