"""Remove identical terrain facets only; preserve every distinct rendered triangle."""
from pathlib import Path
import numpy as np,traceback
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';OLD=BASE/'government-xl-unnamed147996-private-ground-v4-20261020';BATCH='government-xl-unnamed147996-dedup-ground-v2-20261020';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
assert not DOC.exists();r=read(OLD/'result.json')
with connect() as db:
 db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
pins={e['path']:e['sha256']for e in r['evidenceRefs']}
source=HERE/'local'/OLD.name/'candidate-terrain.json';assert digest(source.read_bytes())==pins[str(source.relative_to(ROOT))]
patch=read(source);v=np.asarray(patch['nativeMesh']['position'],dtype=np.float32).reshape(-1,3);indices=np.asarray(patch['nativeMesh']['index']).reshape(-1,3);faces=v[indices];seen=set();keep=[]
# Keep cyclic orientation, so even normal-facing semantics are unchanged.
def key(t):
 rows=[tuple(float(x)for x in p)for p in t];return min(tuple(rows[i:]+rows[:i])for i in range(3))
for i,t in enumerate(faces):
 k=key(t)
 if k not in seen:seen.add(k);keep.append(i)
assert {key(t)for t in faces[keep]}==seen
patch['nativeMesh']['index']=indices[keep].reshape(-1).tolist()
# Published originals are untouched. This exact existing whole-parent route
# uses 100000 final facets, not the constructor's 25000 small-patch default.
policy=HERE/'xl-routed-source-local-contact-resolution.py';assert "assert final_triangles<=100000,'final-terrain-runtime-budget'" in policy.read_text()
proof=dict(originalTriangles=len(faces),retainedTriangles=len(keep),removedIdenticalOrientedTriangles=len(faces)-len(keep),everyDistinctOrientedFloat32TrianglePreserved=True,positionsUnchanged=True,finalRuntimeCap=100000,capAuthority=str(policy.relative_to(ROOT)),buildingGeometryChanges=0,installationApproved=False)
save(DOC/'dedup-proof.json',proof);target=LOCAL/'candidate-terrain.json';save(target,patch)
builder=module('dedup_native_validator',HERE/'resolve-pass-indexed-parent-clipping.py');error=None
try:
 assert len(keep)<=100000,'final-terrain-runtime-budget'
 builder.validate_patch(patch,read(ROOT/'3d-viewer/city/data/terrain.json'))
except Exception as exc:error=str(exc);save(DOC/'guard-failure.json',dict(error=error,traceback=traceback.format_exc(),installationApproved=False))
refs=[Path(__file__),OLD/'result.json',source,target,policy,HERE/'resolve-pass-indexed-parent-clipping.py',ROOT/'3d-viewer/city/data/terrain.json']
module('dedup_ground_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-oriented-duplicate-terrain-removal',refs,dict(uids=['landsd/147996:0'],guardFailure=error,**proof))
print(proof,error,flush=True)
