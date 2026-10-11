"""Three-face patch vs complete original host incidence-one boundary loops.

Per-body incidence avoids masking a boundary with a foreign body's coincident
edge. All source faces remain; exact-zero triangles cannot supply host edges.
Reciprocal .1 m perimeter proximity is no hole, mount, function or support role.
"""
from pathlib import Path
from collections import defaultdict
import importlib.util,time,uuid
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shared_edge_component_census_v2_20261011 import exact_nonrendering
from exact_original_closed_boundary_loop_band_diagnostic_v1_20261011 import verify

BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261011-hoi-shing-three-face-patch-original-host-loops-v1';DOC=BASE/BATCH
PRIOR=BASE/'xl-terrain-recovery-20261011-hoi-shing-three-face-original-patch-host-context-v1'
GRAPH=BASE/'xl-terrain-recovery-20261011-hoi-shing-complete-original-edge-contact-graph-v1'
PROBE=BASE/'government-xl-terrain-recovery-hoi-shing-two-original-current-probe-v1-20261011'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();refs=[ref(Path(__file__))];receipts={}
 for folder in [PRIOR,GRAPH,PROBE]:
  r=read(folder/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  receipts[folder.name]=r;refs.append(ref(folder/'result.json'))
 def bound(folder,p):assert ref(p)in receipts[folder.name]['evidenceRefs'];refs.append(ref(p));return read(p)
 prior=bound(PRIOR,PRIOR/'diagnostic.json.gz');graph=bound(GRAPH,GRAPH/'diagnostic.json.gz');sel=bound(PROBE,PROBE/'selection.json.gz');sources=[]
 for r in sel['rows']:
  p=ROOT/r['candidate']['path'];assert ref(p)['sha256']==r['sourceSHA256'];sources.append(decode_original_world_triangles(p.read_bytes()));refs.append(ref(p))
 world=np.concatenate(sources);assert world.shape==(19374,3,3)and digest(world.tobytes())==prior['complete19374OriginalWorldSHA256']==graph['binding']['completeOriginalWorldSHA256']
 assert prior['completeOriginalFaces']==[4083,4084,4085]and prior['originalBody']==10
 source_edges=np.asarray(prior['completeOriginalBoundary'],float);assert source_edges.shape==(3,2,3)
 # Recreate complete original patch boundary independently of the saved list.
 incidences=defaultdict(list)
 for fi in prior['completeOriginalFaces']:
  assert not exact_nonrendering(world[fi])
  for a,b in zip(world[fi],np.roll(world[fi],-1,axis=0)):incidences[tuple(sorted((tuple(a),tuple(b))))].append(fi)
 recreated=sorted(e for e,fs in incidences.items()if len(fs)==1);assert source_edges.tolist()==[[list(v)for v in e]for e in recreated]
 hostbodies=prior['completeConditionalSourceOnlyHostBodies'];assert 10 not in hostbodies and len(hostbodies)==len(set(hostbodies))
 assert sorted(fi for b in hostbodies for fi in graph['components'][b]['globalOriginalFaces'])==prior['completeConditionalOriginalHostFaces']
 helpers=['exact_packed_world_geometry_20261009.py','exact_original_shared_edge_component_census_v2_20261011.py','exact_original_closed_boundary_loop_band_diagnostic_v1_20261011.py','xl-popcorn-source-investigations-checkpoints-20261009.py'];refs.extend(ref(HERE/n)for n in helpers)
 claim=reservations.claim('hoi-three-patch-loop-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];last=time.monotonic();rows=[];matches=[]
 def pulse(force=False):
  nonlocal last
  if force or time.monotonic()-last>=20:assert reservations.heartbeat(lease)['ok'];last=time.monotonic()
 try:
  for body in hostbodies:
   ids=graph['components'][body]['globalOriginalFaces'];edgefaces=defaultdict(list);zero=[]
   for fi in ids:
    if exact_nonrendering(world[fi]):zero.append(fi);continue
    for a,b in zip(world[fi],np.roll(world[fi],-1,axis=0)):
     assert not np.array_equal(a,b);edgefaces[tuple(sorted((tuple(a),tuple(b))))].append(dict(originalHostFace=fi,directedOriginalEdge=[a.tolist(),b.tolist()]))
   boundary={e:fs for e,fs in edgefaces.items()if len(fs)==1};adj=defaultdict(set)
   for a,b in boundary:adj[a].add(b);adj[b].add(a)
   groups=[];remaining=set(adj)
   while remaining:
    seen={min(remaining)};todo=list(seen)
    while todo:
     for n in adj[todo.pop()]:
      if n not in seen:seen.add(n);todo.append(n)
    remaining-=seen;edges=sorted(e for e in boundary if e[0]in seen);closed=all(len(adj[v])==2 for v in seen)
    group=dict(originalBoundaryVertices=sorted(seen),allOriginalHostBoundaryEdges=[dict(originalEdge=e,completeOriginalHostIncidences=boundary[e])for e in edges],closedConnectedDegreeTwoLoop=closed,allOriginalVertexDegrees=[dict(vertex=v,degree=len(adj[v]))for v in sorted(seen)],simpleGeometricHoleCertified=False)
    if closed:
     raw=np.asarray(edges,float);source=source_edges.reshape(-1,3);a=raw.reshape(-1,3)
     candidate=bool(np.all(np.abs(a.min(0)-source.min(0))<=np.nextafter(.1,np.inf))and np.all(np.abs(a.max(0)-source.max(0))<=np.nextafter(.1,np.inf)))
     group['conservativeWholeLoopBoundsCandidate']=candidate
     if candidate:
      proof=verify(source_edges,raw);group['completeReciprocalPerimeterProof']=proof
      if proof['completeReciprocalBoundaryBandProved']:matches.append(dict(originalHostBody=body,originalBoundaryGroup=len(groups)))
    groups.append(group)
   rows.append(dict(originalHostBody=body,completeOriginalHostFaces=ids,exactZeroOriginalHostFacesRetainedWithoutEdgeCredit=zero,allNonzeroOriginalHostEdgeIncidences=[dict(edge=e,incidences=fs)for e,fs in sorted(edgefaces.items())],completeOriginalHostBoundaryGroups=groups));pulse()
  pulse(True);assert all(ref(ROOT/r['path'])==r for r in refs)
  out=dict(uids=[r['uid']for r in sel['rows']],complete19374OriginalWorldSHA256=digest(world.tobytes()),originalBody=10,completeOriginalPatchFaces=prior['completeOriginalFaces'],entireThreeEdgeOriginalPatchBoundary=source_edges.tolist(),completeConditionalOriginalHostBodies=hostbodies,allPerHostBodyIncidenceAndBoundaryGroups=rows,allCompleteReciprocalLoopMatches=matches,priorWholeFacetResultVerbatim=prior['allThreeWholeFiniteFacetProofs'],allOriginalZeroContactAndRimNegativesPreserved=True,sourceOnly=True,hostQualification=False,simpleOriginalHoleCertified=False,roleAssigned=False,currentAcceptance=False,structuralRootOrBridgeCredit=False,newlyInstalled=0,evidenceRefs=refs)
  save(DOC/'diagnostic.json.gz',out);spec=importlib.util.spec_from_file_location('freeze_hoi_patch_loop',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,'whole-original-three-face-patch-reciprocal-host-boundary-loop-diagnostic-v1',[ROOT/r['path']for r in refs]+[DOC/'diagnostic.json.gz'],dict(uids=out['uids'],sourceOnly=True,currentAcceptance=False,hostQualification=False,roleAssigned=False,structuralRootOrBridgeCredit=False,newlyInstalled=0))
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
