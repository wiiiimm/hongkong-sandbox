"""Complete source-bound finite wall/grade investigation; no current acceptance."""
import json,importlib.util,uuid
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_bound_facet_wall_context_20261010 import contexts,canonical
from original_strict_clear_cap_wall_paths_20261009 import verify as cap_paths
from exact_original_upper_ground_interfaces_20261009 import exact_upper_ground_interfaces
BATCH='xl-terrain-recovery-20261010-ching-hin-finite-wall-grade-context-v1'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 base=ROOT/'docs/astra-city/government-import';doc=base/BATCH;assert not doc.exists();physical=base/'government-xl-ching-hin-complete-current-recheck-20261007';gd=base/'xl-terrain-recovery-20261010-ching-hin-complete-original-support-v1';fd=base/'xl-terrain-recovery-20261010-ching-hin-complete-paired-finite-clearance-v1'
 refs=[]
 for folder in [gd,fd]:
  result=read(folder/'result.json')
  with connect() as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(result['jobId'],)).fetchone()==('complete',result)
  for r in result['evidenceRefs']:assert ref(ROOT/r['path'])==r
  refs.extend(ref(folder/n) for n in ['diagnostic.json.gz','result.json'])
 graph=read(gd/'diagnostic.json.gz');finite=read(fd/'diagnostic.json.gz')['rows'][0];source=read(physical/'selection.json.gz')['rows'][0];runtime_path=HERE/'local'/physical.name/'runtime-geometry.json.gz';runtime=read(runtime_path)['rows'][0];asset=ROOT/source['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==source['sourceSHA256']==finite['sourceSHA256']==graph['actors'][0]['sourceSHA256'];tri=decode_original_world_triangles(raw);ground=np.asarray(runtime['drawnGroundGeometry'],float).reshape(-1,3,3)
 assert digest(tri.tobytes())==finite['completeOriginalWorldSHA256']==graph['binding']['completeOriginalWorldTrianglesSHA256'];assert digest(ground.tobytes())==finite['completeGroundSHA256'];assert len(tri)==16555
 binding=dict(completeOriginalWorldTrianglesSHA256=digest(tri.tobytes()),completeDrawnGroundSHA256=digest(ground.tobytes()),completeFiniteFacetProofRowsSHA256=canonical(finite['allFaces']))
 claim=reservations.claim('ching-hin-source-wall-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  ctx=contexts(tri,ground,finite['allFaces'],expected_binding=binding,current_binding=binding);assert reservations.heartbeat(lease)['ok'];pairs=[r['globalOriginalFaces'] for r in graph['exactOriginalContacts']];b={**binding,'completeCurrentFacetContextsSHA256':canonical(ctx),'exactOriginalContactListSHA256':canonical(pairs)};paths=cap_paths(tri,ctx,pairs,expected_binding=b,current_binding=b)
  affected=paths['affectedOriginalWallFaces'];assert affected==[1161,1518,1998];grade=exact_upper_ground_interfaces(tri,affected,ground);byface={f:i for i,c in enumerate(graph['components']) for f in c['globalOriginalFaces']};local_roots=sorted({byface[r['sourceFace']] for r in grade if next(p for p in paths['paths'] if p['sourceFace']==r['sourceFace'])['hasExactOriginalStrictClearCapRoofPath'] and all(byface[f]==byface[r['sourceFace']] for f in next(p for p in paths['paths'] if p['sourceFace']==r['sourceFace'])['originalPath'])});adj={i:set() for i in range(len(graph['components']))}
  for r in graph['exactOriginalContacts']:a,b=r['components'];adj[a].add(b);adj[b].add(a)
  reached=set(local_roots);todo=list(reached)
  while todo:
   a=todo.pop()
   for v in adj[a]-reached:reached.add(v);todo.append(v)
  refs.extend(ref(p) for p in [Path(__file__),runtime_path,physical/'selection.json.gz',asset,HERE/'original_bound_facet_wall_context_20261010.py',HERE/'test_original_bound_facet_wall_context_20261010.py',HERE/'original_strict_clear_cap_wall_paths_20261009.py',HERE/'test_original_strict_clear_cap_wall_paths_20261009.py',HERE/'exact_original_upper_ground_interfaces_20261009.py',HERE/'exact_original_shell_intersections_20261009.py',HERE/'exact_original_component_contacts_20261009.py'])
  result=dict(uids=[source['uid']],binding=b,completeOriginalFaces=len(tri),completeOriginalComponents=len(graph['components']),completeCertifiedLowerBoundContexts=ctx,certifiedBoundsNotClaimedExactMinima=True,originalCapPaths=paths,exactCurrentUpperGroundInterfaces=grade,sourceOnlyGradeRootCandidates=local_roots,sourceOnlyGraphReachable=sorted(reached),unresolvedSourceComponents=sorted(set(adj)-reached),rawPriorDiagnosticChanged=False,currentRegionalRebindRequired=True,fullAcceptance=False,installationApproved=False,sourceGeometryChanges=0,evidenceRefs=refs);save(doc/'diagnostic.json.gz',result)
  spec=importlib.util.spec_from_file_location('f',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,'immutable-original-certified-wall-grade-context-v1',[ROOT/r['path'] for r in refs],dict(uids=result['uids'],completeOriginalFaces=len(tri),affectedOriginalWallFaces=affected,allAffectedHavePaths=paths['allAffectedHavePaths'],exposureFailures=paths['rawExposureFailures'],positiveGradeInterfaces=len(grade),sourceOnlyGradeRootCandidates=local_roots,reachableComponents=len(reached),unresolvedSourceComponents=result['unresolvedSourceComponents'],fullAcceptance=False,currentRegionalRebindRequired=True));print(json.dumps(dict(paths=paths['paths'],gradeCount=len(grade),roots=local_roots,reached=len(reached),unresolved=result['unresolvedSourceComponents'])),flush=True)
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
