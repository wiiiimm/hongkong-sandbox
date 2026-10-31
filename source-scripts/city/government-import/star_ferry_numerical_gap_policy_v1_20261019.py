"""Restore established bounded numerical-gap fallback on private merged terrain."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
import native_patch_resolution as repair
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-star-ferry-numerical-gap-policy-v1-20261019';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
SRC=BASE/'government-xl-star-ferry-retained-children-candidate-v3-20261019'
assert not DOC.exists();r=read(SRC/'result.json');refs=[Path(__file__),SRC/'result.json']
with connect() as c:
    c.execute('SET TRANSACTION READ ONLY')
    assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
for e in r['evidenceRefs']:
    p=ROOT/e['path'];assert digest(p.read_bytes())==e['sha256'],str(p);refs.append(p)
source=HERE/'local'/SRC.name/'terrain-private-child.json';patch=read(source)
bounds=read(SRC/'candidate.json')['changedExtent']
_,_,gap,_=repair.projected_context(patch,bounds)
maximum=max(.25,(bounds[2]-bounds[0])*(bounds[3]-bounds[1])*1e-3)
assert 0<gap.area<=maximum
before=digest(str((patch['nativeMesh']['position'],patch['nativeMesh']['index'])).encode())
patch['nativeMesh']['source']['numericalCoverageGap']=dict(policy='parent-grid-fallback',measuredAreaM2=float(gap.area),maximumAreaM2=maximum,maximumFraction=1e-3)
assert before==digest(str((patch['nativeMesh']['position'],patch['nativeMesh']['index'])).encode())
parentpath=ROOT/'3d-viewer/city/data/government-native-ocean-terminal-original-v1-20261019.json'
builder=module('star_gap_validator',HERE/'resolve-pass-indexed-parent-clipping.py');builder.validate_patch(patch,read(parentpath))
save(LOCAL/'terrain-private-child.json',patch)
save(DOC/'gap-policy.json',dict(measuredAreaM2=float(gap.area),maximumAreaM2=maximum,geometryUnchanged=True,gridUnchanged=True,sourceGeometryChanges=0,freshPlacementNeighbourAndBrowserChecksRequired=True,installationApproved=False))
refs.extend([source,parentpath,LOCAL/'terrain-private-child.json',HERE/'native_patch_resolution.py',HERE/'resolve-pass-indexed-parent-clipping.py'])
module('star_gap_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'star-ferry-private-bounded-numerical-gap-fallback',list(dict.fromkeys(refs)),dict(uids=['landsd/210032:0'],measuredAreaM2=float(gap.area),installationApproved=False))
