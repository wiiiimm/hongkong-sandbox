"""Reproduce every canonical low-rim sample and attribute original bottom-cap flags."""
from pathlib import Path
import numpy as np,subprocess
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-yoho-podium-cap-rim-v1-20261020';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;UID='landsd/301636:0';CAP=BASE/'government-xl-yoho-seven-runtime-capture-v1-20261020';TER=BASE/'government-xl-yoho-seven-private-terrain-v1-20261020'
assert not DOC.exists();pins={};refs=[Path(__file__)]
with connect()as c:
 c.execute('SET TRANSACTION READ ONLY')
 for d in [CAP,TER]:
  r=read(d/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json')
  for e in r['evidenceRefs']:assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
def consume(p):
 assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
row=next(x for x in consume(TER/'selection.json.gz')['rows']if x['uid']==UID);asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];refs.append(asset);worlds={'original':decode_original_world_triangles(asset.read_bytes())}
a=next(x for x in consume(CAP/'attributes.json.gz')['rows']if x['uid']==UID)
for mode,field in [('literal','completeLiteralWorldPosition'),('explicitLeftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('explicitBalancedF32','completeExplicitBalancedFloat32WorldPosition')]:worlds[mode]=np.asarray(a[field],dtype='<f8').reshape(-1,3)[np.asarray(a['completeOriginalIndex']).reshape(-1,3)]
ground=np.asarray(next(x for x in consume(HERE/'local'/TER.name/'runtime-geometry.json.gz')['rows']if x['uid']==UID)['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3)
p=LOCAL/'input.json.gz';save(p,dict(worlds={k:v.tolist()for k,v in worlds.items()},ground=ground.tolist()));refs.append(p);DOC.mkdir(parents=True);tool=HERE/'yoho_podium_cap_rim_v1_20261020.mjs';subprocess.run(['node',str(tool),str(p),str(DOC/'rim.json')],cwd=ROOT,check=True)
refs.extend([tool,HERE/'support-contact.mjs',HERE/'source-face-query.mjs',HERE/'triangle-point-index.mjs',HERE/'exact_packed_world_geometry_20261009.py',ROOT/'3d-viewer/vendor/three.module.js'])
save(DOC/'bindings.json',dict(uid=UID,sourceSHA256=row['sourceSHA256'],worldSHA256ByMode={k:digest(v.tobytes())for k,v in worlds.items()},drawnGroundSHA256=digest(ground.tobytes())))
module('yoho_cap_rim_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'whole-original-podium-canonical-low-rim-attribution',refs,dict(uids=[UID],rows=read(DOC/'rim.json')['rows'],installationApproved=False,geometryChanges=0))
