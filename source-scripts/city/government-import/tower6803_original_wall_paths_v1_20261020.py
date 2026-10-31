"""Apply existing endpoint-bounded original-face paths to Parkview; no approval."""
from pathlib import Path
import subprocess,numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from pool_incident_wall_contacts_v1_20261017 import closest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-tower6803-original-wall-paths-v1-20261020';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;SRC=BASE/'government-xl-exact-parent-support-sequence-20261006-6803-0'
assert not DOC.exists();receipt=read(SRC/'result.json');pins={e['path']:e['sha256']for e in receipt['evidenceRefs']};inp=SRC/'selection.json.gz';assert digest(inp.read_bytes())==pins[str(inp.relative_to(ROOT))]
with connect()as c:
 c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
refs=[Path(__file__),SRC/'result.json',inp,HERE/'support-contact.mjs',HERE/'source-face-query.mjs',HERE/'triangle-point-index.mjs',ROOT/'3d-viewer/vendor/three.module.js',HERE/'pool_incident_wall_contacts_v1_20261017.py',HERE/'exact_packed_world_geometry_20261009.py'];tool=HERE/'tower6803_minimum_height_paths_v1_20261020.mjs';refs.append(tool);summary=[];DOC.mkdir()
selection=read(inp)['rows'];worlds={}
for r in selection:
 if r['uid'] not in ['landsd/6803:0','landsd/15047:0']:continue
 asset=ROOT/r['candidate']['path'];assert digest(asset.read_bytes())==r['sourceSHA256'];refs.append(asset);worlds[r['uid']]=decode_original_world_triangles(asset.read_bytes())
assert set(worlds)=={'landsd/6803:0','landsd/15047:0'}
for mode in ['original']:
 p=LOCAL/(mode+'.json.gz');save(p,dict(worlds={u:t.tolist()for u,t in worlds.items()}));refs.append(p);graph=DOC/(mode+'-graph.json.gz');subprocess.run(['node',str(tool),str(p),str(graph)],cwd=ROOT,check=True);rows=[]
 for row in read(graph)['rows']:
  uid=row['uid'];t=worlds[uid];details=[]
  for item in row['paths']:
   if not item['hasPath']:details.append(dict(position=item['position'],verified=False,reason='no-original-shared-edge-path',incidentFaces=item['incidentFaces']));continue
   ids=item['faces'];start=np.asarray(item['position']);end=np.asarray(item['root']['position']);ceiling=max(start[1],end[1]);points=[start];failure=None
   assert -.1<=item['root']['gap']<=1
   for a,b in zip(ids,ids[1:]):
    shared=sorted(set(map(tuple,t[a]))&set(map(tuple,t[b])));assert len(shared)==2;p0,q=map(np.asarray,shared)
    if min(p0[1],q[1])>ceiling:failure='shared-edge-entirely-above-endpoint-height';break
    if max(p0[1],q[1])>ceiling:
     cut=p0+(q-p0)*((ceiling-p0[1])/(q[1]-p0[1]))
     if p0[1]>ceiling:p0=cut
     else:q=cut
    points.append((p0+q)/2)
   if failure:details.append(dict(position=start.tolist(),verified=False,reason=failure,faces=ids,ceiling=float(ceiling)));continue
   points.append(end);assert len(points)==len(ids)+1;errors=[float(np.linalg.norm(closest(p0,t[f])-p0))for j,f in enumerate(ids)for p0 in points[j:j+2]];error=max(errors);valid=error<=.001 and all(p0[1]<=ceiling+1e-9 for p0 in points)
   details.append(dict(position=start.tolist(),verified=valid,faces=ids,continuousPath=[p0.tolist()for p0 in points],endpointHeightCeilingM=float(ceiling),maximumPathHeightM=float(max(p0[1]for p0 in points)),maximumFaceResidualM=error,pathLengthM=float(sum(np.linalg.norm(b-a)for a,b in zip(points,points[1:]))),root=item['root']))
  s=dict(uid=uid,mode=mode,worldSHA256=digest(t.tobytes()),failures=len(details),boundedPaths=sum(x['verified']for x in details),unresolved=sum(not x['verified']for x in details));summary.append(s);rows.append(dict(**s,details=details));print(s,flush=True)
 save(DOC/(mode+'-verified.json.gz'),dict(rows=rows,installationApproved=False,qualification='Existing finite-face residual1mm, strict-contact endpoint gap[-0.1,1]m and own-endpoint height ceiling unchanged. Original-face continuity is diagnostic only; complete physical/source review still required.'))
save(DOC/'summary.json',dict(rows=summary,installationApproved=False))
module('parkview_low_paths_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'existing-endpoint-bounded-original-support-paths',refs,dict(uids=sorted(worlds),rows=summary,scope='Exact original source only; no current terrain or Float32 acceptance.',installationApproved=False,geometryChanges=0))
