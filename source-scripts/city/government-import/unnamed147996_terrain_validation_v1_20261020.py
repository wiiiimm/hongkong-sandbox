"""Bind existing highest-native-surface audit to the exact private terrain candidate."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-unnamed147996-terrain-validation-v1-20261020';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;SRC=BASE/'government-xl-unnamed147996-dedup-ground-v2-20261020';CTX=BASE/'government-xl-unnamed147996-overlap-context-v2-20261020';DELTA=BASE/'government-xl-unnamed147996-overlap-delta-v2-20261020';GROUND=BASE/'government-xl-next-twenty-original-ground-v3-20261020'
assert not DOC.exists();refs=[Path(__file__)];pins={};receipts={}
with connect()as db:
 db.execute('SET TRANSACTION READ ONLY')
 for folder in [SRC,CTX,DELTA,GROUND]:
  r=read(folder/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json');receipts[folder.name]={e['path']:e['sha256']for e in r['evidenceRefs']}
def pin(path,folder):
 key=str(path.relative_to(ROOT));sha=receipts[folder.name][key];assert digest(path.read_bytes())==sha;assert key not in pins or pins[key]==sha;pins[key]=sha;refs.append(path)
source=HERE/'local'/SRC.name/'candidate-terrain.json';pin(source,SRC);parent=ROOT/'3d-viewer/city/data/government-park-avenue239350-original-v1-20261018.json';pin(parent,CTX)
for folder,name in [(CTX,'summary.json'),(DELTA,'summary.json'),(DELTA,'changed.json.gz')]:pin(folder/name,folder)
ground=HERE/'local'/GROUND.name/'147996:0-ground.json.gz';pin(ground,GROUND);gltf=ROOT/read(ground)['sourcePath'];pin(gltf,GROUND);sourcefiles=[parent,gltf]
for b in read(gltf)['buffers']:p=gltf.parent/b['uri'];pin(p,GROUND);sourcefiles.append(p)
patch=read(source);before=[patch['nativeMesh']['position'],patch['nativeMesh']['index']];assert len(before[1])//3<=100000
repair=module('candidate_overlap_audit',HERE/'native_patch_resolution.py');builder=module('candidate_validation',HERE/'resolve-pass-indexed-parent-clipping.py')
target=LOCAL/'candidate-terrain.json';save(target,patch);audit=repair.approve_original_overlap(patch,target,DOC/'native-overlap.json',[dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))for p in sourcefiles]);repair.finalize_overlap_evidence(patch,DOC/'native-overlap.json');assert before==[patch['nativeMesh']['position'],patch['nativeMesh']['index']]
save(target,patch);builder.validate_patch(patch,read(ROOT/'3d-viewer/city/data/terrain.json'))
save(DOC/'validation.json',dict(terrainValidatorPassed=True,positionsAndIndicesUnchanged=True,originalDistinctTriangles= len(patch['nativeMesh']['index'])//3,overlapAuditSamples=audit['float32HighestRayAgreement']['samples'],overlapAuditMaximumRayErrorM=audit['float32HighestRayAgreement']['maxError'],completeOverlapContext=str(CTX.relative_to(ROOT)),completeDelta=str(DELTA.relative_to(ROOT)),qualification='Existing terrain-validator highest-native-surface evidence only. Pair-difference warnings remain recorded; retained actors, full renderer modes and browser/publication remain independent obligations.',installationApproved=False))
for key,sha in pins.items():assert digest((ROOT/key).read_bytes())==sha
refs.extend([target,HERE/'native_patch_resolution.py',HERE/'resolve-pass-indexed-parent-clipping.py',ROOT/'3d-viewer/city/data/terrain.json'])
module('candidate_validation_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'native-source-overlap-audit-and-terrain-validator',refs,dict(uids=['landsd/147996:0'],terrainValidatorPassed=True,positionsAndIndicesUnchanged=True,installationApproved=False))
