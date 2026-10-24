"""Bounded genuine finite grade interfaces of original native Langham body963.

Complete original/literal candidate wall inventory on frozen current ground.
No whole-native certification, exposed-cap path, grounding or import approval.
"""
import importlib.util,json,time,uuid
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_upper_ground_interfaces_20261009 import exact_upper_ground_interfaces
from original_bound_facet_wall_context_v3_20261010 import best_original_vertex_exposure
from exact_original_face_conservative_clearance_v5_20261010 import verify
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261011-langham-native963-current-grade-diagnostic-v1';DOC=BASE/BATCH
PROBE=BASE/'government-xl-terrain-recovery-langham-upper-complete-original-current-probe-v1-20261011';GRAPH=BASE/'xl-terrain-recovery-20261011-langham-complete-original-edge-contact-graph-v1';UID='landsd/224399:0'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();refs=[ref(Path(__file__))]
 for folder in [PROBE,GRAPH]:
  receipt=read(folder/'result.json')
  with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  refs.append(ref(folder/'result.json'))
 geometry=HERE/'local'/PROBE.name/'runtime-geometry.json.gz';rt=next(r for r in read(geometry)['rows']if r['uid']==UID);row=next(r for r in read(PROBE/'selection.json.gz')['rows']if r['uid']==UID);asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256']==rt['sourceSHA256'];original=decode_original_world_triangles(asset.read_bytes());literal=np.asarray(rt['position'],float).reshape(-1,3)[np.asarray(rt['index'],int).reshape(-1,3)];ground=np.asarray(rt['drawnGroundGeometry'],float).reshape(-1,3,3);assert original.shape==literal.shape==(20260,3,3)
 g=read(GRAPH/'diagnostic.json.gz');component=g['components'][963];assert component['actorUID']==UID;body=[i-18086 for i in component['globalOriginalFaces']];assert len(body)==2385 and all(0<=i<20260 for i in body)
 refs.extend(ref(p)for p in [asset,geometry,PROBE/'selection.json.gz',PROBE/'historical-current-manifest.json',GRAPH/'diagnostic.json.gz',HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_upper_ground_interfaces_20261009.py',HERE/'original_bound_facet_wall_context_v3_20261010.py',HERE/'original_bound_facet_wall_context_v2_20261010.py',HERE/'exact_original_face_conservative_clearance_v5_20261010.py',HERE/'exact_original_projection_coverage_v2_20261010.py',HERE/'exact_original_component_contacts_20261009.py',HERE/'exact_original_shell_intersections_20261009.py'])
 claim=reservations.claim('langham-native963-grade-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];last=time.monotonic()
 def pulse(force=False):
  nonlocal last
  if force or time.monotonic()-last>=20:assert reservations.heartbeat(lease)['ok'];last=time.monotonic()
 try:
  rows=[]
  for mode,world in [('providerOriginal',original),('actualLiteral',literal)]:
   normal=np.cross(world[:,1]-world[:,0],world[:,2]-world[:,0]);norm=(normal*normal).sum(1);ids=[int(i)for i in body if norm[i]>0 and normal[i,1]**2<=norm[i]/16 and world[i,:,1].min()<=ground[:,:,1].max()and world[i,:,1].max()>=ground[:,:,1].min()];records=[]
   for i in ids:
    interfaces=exact_upper_ground_interfaces(world,[i],ground);exposure=best_original_vertex_exposure(world[i],ground);finite=verify(world[i],ground);records.append(dict(sourceFace=i,originalCompleteVertices=world[i].tolist(),exactPositiveUpperGroundInterfaces=interfaces,completeOriginalVertexExposure=exposure,rawWholeFacetFiniteProof=finite));pulse()
   rows.append(dict(mode=mode,completeNativeFaces=20260,completeNativeWorldSHA256=digest(world.tobytes()),completeDrawnGroundSHA256=digest(ground.tobytes()),completeDrawnGroundFaces=len(ground),completeOriginal963BodyFaces=body,completeConservativeVerticalGradeCandidateFaces=ids,allCandidateFacesAccounted=records,positiveDimensionalGradeFaces=[r['sourceFace']for r in records if r['exactPositiveUpperGroundInterfaces']],gradeIsNotRootOrExposedCapPath=True));print(dict(mode=mode,gradeCandidates=len(ids),positiveDimensionalGradeFaces=rows[-1]['positiveDimensionalGradeFaces']),flush=True)
  pulse(True);assert all(ref(ROOT/r['path'])==r for r in refs);result=dict(uids=[UID],rows=rows,completeOriginalBodyOnly=True,frozenBaselineManifest=ref(PROBE/'historical-current-manifest.json'),sourceOnlyFrozenCurrentBaseline=True,noFreshCurrentReacceptance=True,rawAllOtherNativeFacesRetainedInCompleteSource=True,nativeReacceptance=False,exposedCapPathProved=False,structuralRootCredit=False,currentAcceptance=False,sourceGeometryChanges=0,newlyInstalled=0,evidenceRefs=refs);save(DOC/'diagnostic.json.gz',result)
  spec=importlib.util.spec_from_file_location('langham_grade_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,'bounded-langham-native963-original-literal-current-finite-upper-grade-diagnostic-v1',[ROOT/r['path']for r in refs]+[DOC/'diagnostic.json.gz'],dict(uids=[UID],sourceOnlyFrozenCurrentBaseline=True,nativeReacceptance=False,currentAcceptance=False,completeOriginalNativeFaces=20260,boundedBodyFaces=2385,newlyInstalled=0))
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
