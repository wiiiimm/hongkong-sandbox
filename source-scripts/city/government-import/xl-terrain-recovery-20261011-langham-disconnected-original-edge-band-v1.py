"""Every original edge of the 95 disconnected Langham bodies, fixed .1m band.

Finite per-edge association is diagnostic only. Every free/failed edge and
nonmanifold incidence remains; no automatic closed-solid/mount/root credit.
"""
import importlib.util,json,time,uuid,collections
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_edge_any_finite_distance_band_v2_20261010 import verify
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261011-langham-disconnected-original-edge-band-v1';DOC=BASE/BATCH;INPUT=BASE/'xl-terrain-recovery-20261011-langham-disconnected-finite-host-diagnostic-v1';GRAPH=BASE/'xl-terrain-recovery-20261011-langham-complete-original-edge-contact-graph-v1';UID='landsd/79318:0'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();prior=read(INPUT/'diagnostic.json.gz');receipt=read(INPUT/'result.json')
 with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 source_sha=prior['binding']['inputRefs'][4]['sha256'];asset=ROOT/prior['binding']['inputRefs'][4]['path'];assert digest(asset.read_bytes())==source_sha;t=decode_original_world_triangles(asset.read_bytes());assert digest(t.tobytes())==prior['binding']['completeOriginalWorldSHA256'];hosts=t[prior['binding']['completeHostOriginalFaceIds']];assert digest(hosts.tobytes())==prior['binding']['completeHostWorldSHA256'];g=read(GRAPH/'diagnostic.json.gz');bodies=[r['body']for r in prior['perBody']];inventories=[]
 for body in bodies:
  ids=g['components'][body]['globalOriginalFaces'];edges=collections.defaultdict(list)
  for f in ids:
   vertices=list(map(tuple,t[f]))
   for a,b in zip(vertices,vertices[1:]+vertices[:1]):
    if a!=b:edges[tuple(sorted([a,b]))].append(dict(sourceFace=f,directedOriginalEdge=[a,b]))
  lowest=float(t[ids,:,1].min());inventory=[dict(originalEdge=edge,allOriginalIncidences=inc,boundary=len(inc)==1,minimumHeightEdge=all(v[1]==lowest for v in edge))for edge,inc in sorted(edges.items())];inventories.append(dict(body=body,completeOriginalFaces=ids,completeOriginalEdges=inventory))
 refs=[ref(p)for p in [Path(__file__),INPUT/'diagnostic.json.gz',INPUT/'result.json',GRAPH/'diagnostic.json.gz',asset,HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_edge_any_finite_distance_band_v2_20261010.py',HERE/'exact_original_edge_any_finite_distance_band_v1_20261010.py']];binding=dict(inputRefs=refs,completeBodyEdgeInventorySHA256=digest(json.dumps(inventories,sort_keys=True,separators=(',',':')).encode()),completeHostWorldSHA256=digest(hosts.tobytes()));flat=[dict(body=p['body'],**e)for p in inventories for e in p['completeOriginalEdges']];progress=HERE/'local'/BATCH/'compute-progress.json.gz';rows=[]
 if progress.exists():
  old=read(progress);assert old['binding']==binding;rows=old['rows'];assert [{k:v for k,v in r.items()if k!='finiteBand'}for r in rows]==json.loads(json.dumps(flat[:len(rows)]))
 claim=reservations.claim('langham-source-edge-band-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];last=time.monotonic();last_output=last
 def pulse(force=False):
  nonlocal last
  if force or time.monotonic()-last>=20:assert reservations.heartbeat(lease)['ok'];last=time.monotonic()
 try:
  pulse(True)
  for e in flat[len(rows):]:
   proof=verify(np.asarray(e['originalEdge']),hosts);rows.append(dict(**e,finiteBand=proof));pulse()
   if len(rows)%24==0 or len(rows)==len(flat):save(progress,dict(binding=binding,rows=rows,completeProof=False,currentAcceptance=False))
   if time.monotonic()-last_output>=20:print(dict(edgesDone=len(rows),totalEdges=len(flat),associatedEdges=sum(r['finiteBand']['verifiedCompleteOriginalEdgeFiniteFacadeBand']for r in rows)),flush=True);last_output=time.monotonic()
  assert all(ref(ROOT/r['path'])==r for r in refs);pulse(True);refs.append(ref(progress));result=dict(uids=[UID],binding=binding,completeOriginalBodyEdgeInventories=inventories,allOriginalEdges=rows,completeAllOriginalEdgesAccounted=True,hostScopeConditionallyGeometricOnly=True,strictBandM=.1,rootedHostProved=False,sourceOnly=True,noFreshCurrentCapture=True,visualRoleAccepted=False,rootOrStructuralContactCredit=False,nativeReacceptance=False,currentAcceptance=False,sourceGeometryChanges=0,newlyInstalled=0,evidenceRefs=refs);save(DOC/'diagnostic.json.gz',result)
  spec=importlib.util.spec_from_file_location('langham_edge_band_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,'complete-langham-disconnected-original-edge-finite-fixed-band-source-only-diagnostic-v1',[ROOT/r['path']for r in refs]+[DOC/'diagnostic.json.gz'],dict(uids=[UID],sourceOnly=True,currentAcceptance=False,completeOriginalBodies=len(inventories),completeOriginalEdges=len(rows),associatedEdges=sum(r['finiteBand']['verifiedCompleteOriginalEdgeFiniteFacadeBand']for r in rows),newlyInstalled=0));print(dict(complete=True,edges=len(rows),associatedEdges=sum(r['finiteBand']['verifiedCompleteOriginalEdgeFiniteFacadeBand']for r in rows)),flush=True)
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
