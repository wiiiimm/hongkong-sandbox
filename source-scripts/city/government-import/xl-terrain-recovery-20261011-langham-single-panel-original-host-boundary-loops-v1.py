"""Complete source-only original host boundary-loop diagnosis for 80 panels.

Exact reciprocal perimeter band is not a simple-hole, interior or mounted-role
certificate. Original host incidence, open branches and every panel are kept.
"""
from pathlib import Path
from collections import defaultdict,deque
import importlib.util,json,time,uuid
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shared_edge_component_census_v2_20261011 import exact_nonrendering
from exact_original_closed_boundary_loop_band_diagnostic_v1_20261011 import verify
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261011-langham-single-panel-original-host-boundary-loops-v1';DOC=BASE/BATCH
PRIOR=BASE/'xl-terrain-recovery-20261011-langham-disconnected-finite-host-diagnostic-v1';GRAPH=BASE/'xl-terrain-recovery-20261011-langham-complete-original-edge-contact-graph-v1';UID='landsd/79318:0'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();refs=[ref(Path(__file__))]
 for folder in [PRIOR,GRAPH]:
  receipt=read(folder/'result.json')
  with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  refs.extend(ref(folder/p)for p in ['result.json','diagnostic.json.gz'])
 prior=read(PRIOR/'diagnostic.json.gz');graph=read(GRAPH/'diagnostic.json.gz');asset=ROOT/prior['binding']['inputRefs'][4]['path'];assert ref(asset)==prior['binding']['inputRefs'][4];world=decode_original_world_triangles(asset.read_bytes());assert digest(world.tobytes())==prior['binding']['completeOriginalWorldSHA256'];hosts=prior['binding']['completeHostOriginalFaceIds'];assert digest(world[hosts].tobytes())==prior['binding']['completeHostWorldSHA256'];assert all(not exact_nonrendering(world[i])for i in hosts)
 edgefaces=defaultdict(list)
 for i in hosts:
  v=list(map(tuple,world[i]))
  for a,b in zip(v,v[1:]+v[:1]):
   if a!=b:edgefaces[tuple(sorted([a,b]))].append(dict(originalHostFace=i,directedOriginalEdge=[a,b]))
 boundary={e:r for e,r in edgefaces.items()if len(r)==1};adj=defaultdict(set)
 for a,b in boundary:adj[a].add(b);adj[b].add(a)
 remaining=set(adj);groups=[]
 while remaining:
  start=min(remaining);seen={start};q=[start]
  while q:
   for n in adj[q.pop()]:
    if n not in seen:seen.add(n);q.append(n)
  remaining-=seen;edges=sorted(e for e in boundary if e[0]in seen);groups.append(dict(originalBoundaryVertices=sorted(seen),allOriginalHostBoundaryEdges=[dict(originalEdge=e,completeOriginalHostIncidences=boundary[e])for e in edges],closedConnectedDegreeTwoLoop=all(len(adj[v])==2 for v in seen),originalVertexDegrees=[dict(vertex=v,degree=len(adj[v]))for v in sorted(seen)],simpleGeometricHoleCertified=False))
 loops=[(i,g)for i,g in enumerate(groups)if g['closedConnectedDegreeTwoLoop']];panels=[dict(body=r['body'],sourceFace=graph['components'][r['body']]['globalOriginalFaces'][0])for r in prior['perBody']if len(graph['components'][r['body']]['globalOriginalFaces'])==1];assert len(panels)==80
 refs.extend(ref(p)for p in [asset,HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_shared_edge_component_census_v2_20261011.py',HERE/'exact_original_closed_boundary_loop_band_diagnostic_v1_20261011.py',HERE/'test_exact_original_closed_boundary_loop_band_diagnostic_v1_20261011.py',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py']);claim=reservations.claim('langham-panel-boundary-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];last=time.monotonic()
 def pulse(force=False):
  nonlocal last
  if force or time.monotonic()-last>=20:assert reservations.heartbeat(lease)['ok'];last=time.monotonic()
 try:
  results=[]
  for panel in panels:
   face=world[panel['sourceFace']];source_edges=np.asarray(list(zip(face,np.roll(face,-1,axis=0))));candidates=[];matches=[]
   for group_index,g in loops:
    raw=np.asarray([e['originalEdge']for e in g['allOriginalHostBoundaryEdges']]);# Reciprocal band requires BOTH whole-loop bounding extrema within .1m.
    if not (np.abs(raw.min((0,1))-face.min(0))<=np.nextafter(.1,np.inf)).all()or not(np.abs(raw.max((0,1))-face.max(0))<=np.nextafter(.1,np.inf)).all():continue
    proof=verify(source_edges,raw);record=dict(originalHostBoundaryGroup=group_index,completeReciprocalBoundaryProof=proof);candidates.append(record)
    if proof['completeReciprocalBoundaryBandProved']:matches.append(group_index)
   results.append(dict(**panel,completeOriginalFacetVertices=face.tolist(),completeSourceOriginalEdges=source_edges.tolist(),allClosedHostLoopsEnumerated=len(loops),conservativeWholeLoopBoundsCandidates=candidates,completeReciprocalBoundaryMatches=matches,originalAuthoredOpeningOrMountRoleProved=False,wholeFacetInteriorStillUnproved=True));pulse();print(dict(body=panel['body'],sourceFace=panel['sourceFace'],closedLoopCandidates=len(candidates),completeMatches=matches),flush=True)
  pulse(True);assert all(ref(ROOT/r['path'])==r for r in refs);out=dict(uids=[UID],completeOriginalWorldSHA256=digest(world.tobytes()),completeHostOriginalFaceIds=hosts,completeHostWorldSHA256=digest(world[hosts].tobytes()),completeOriginalHostBoundaryGroups=groups,allDisconnectedSinglePanels=results,completeHostBoundaryEdges=len(boundary),completeHostBoundaryGroups=len(groups),closedConnectedDegreeTwoHostLoops=len(loops),reciprocallyAssociatedPanels=sum(bool(p['completeReciprocalBoundaryMatches'])for p in results),originalSimpleHoleOrCavityCertified=False,authoredMountRoleCertified=False,allWholeFacetInteriorNegativesPreserved=ref(PRIOR/'diagnostic.json.gz'),sourceOnly=True,noFreshCurrentCapture=True,currentAcceptance=False,structuralRootCredit=False,structuralBridgeCredit=False,sourceGeometryChanges=0,newlyInstalled=0,evidenceRefs=refs);save(DOC/'diagnostic.json.gz',out);s=importlib.util.spec_from_file_location('freeze_langham_panel_loops',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.freeze(BATCH,'complete-langham-single-panel-original-host-boundary-loop-incidence-fixed-band-diagnostic-v1',[ROOT/r['path']for r in refs]+[DOC/'diagnostic.json.gz'],dict(uids=[UID],completeSinglePanels=80,closedOriginalHostLoops=len(loops),reciprocallyAssociatedPanels=out['reciprocallyAssociatedPanels'],sourceOnly=True,currentAcceptance=False,newlyInstalled=0))
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
