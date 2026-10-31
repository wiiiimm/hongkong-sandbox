"""Original/literal complete Vancor body rooting on the frozen held candidate.

Existing neighbour failure remains. Root/path diagnostic only, never current
assembly acceptance; actual model-matrix Float32 proofs remain independent.
"""
import importlib.util,json
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shared_edge_component_census_v2_20261011 import census
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
from original_wall_rim_accounting_20261009 import original_samples
from original_ordinary_rim_accounting_20261009 import verify
BATCH='government-xl-vancor-candidate-complete-body-current-ground-diagnostic-v1-20261011';DOC=ROOT/'docs/astra-city/government-import'/BATCH
INPUT=DOC.parent/'government-xl-vancor-authentic-tin-retained-pak-shing-current-inputs-v1-20261011';PHYS=DOC.parent/'government-xl-vancor-authentic-tin-retained-pak-shing-current-physical-v1-20261011';RUNTIME=HERE/'local'/PHYS.name/'runtime-geometry.json.gz'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();receipt=read(PHYS/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 assert ref(RUNTIME)in receipt['evidenceRefs'];runtime=read(RUNTIME)['rows'][0];selected=read(INPUT/'check-selection.json.gz')['rows'][0];assert runtime['uid']==selected['uid']=='landsd/147956:0'and runtime['sourceSHA256']==selected['sourceSHA256']
 rawpath=ROOT/selected['candidate']['path'];raw=rawpath.read_bytes();assert digest(raw)==selected['sourceSHA256'];original=decode_original_world_triangles(raw);position=np.asarray(runtime['position'],dtype='<f8').reshape(-1,3);index=np.asarray(runtime['index'],int).reshape(-1,3);literal=position[index];ground=np.asarray(runtime['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3)
 spec=importlib.util.spec_from_file_location('vancor_current_finite_height',HERE/'xl-lee-kong-two-independent-original-tin-body-graph-diagnostic-v1-20261011.py');old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
 rows=[]
 for mode,world in [('providerOriginal',original),('actualLiteral',literal)]:
  topology=census(world,list(range(len(world))));groups=topology['sharedEdgeConnectedComponents'];parts=[];roots=[];edges=[];adj={i:set()for i in range(len(groups))}
  for i,ids in enumerate(groups):
   p,inv=np.unique(world[ids].reshape(-1,3),axis=0,return_inverse=True);ix=inv.reshape(-1,3);assert np.array_equal(p[ix],world[ids]);bottom=float(p[:,1].min());samples=original_samples(p,ix,bottom)
   for s in samples:s['ground']=old.height(s['point'],ground);s['gap']=s['point'][1]-s['ground']
   low=[s for s in samples if s['point'][1]<=bottom+.35];metric=dict(checks=len(samples),lowRimChecks=len(low),minSurfaceGap=min(s['gap']for s in samples),minLowGap=min(s['gap']for s in low),maxLowGap=max(s['gap']for s in low));proof=None;error=None
   try:proof=verify(p,ix,bottom,samples,expected_metric=metric);roots.append(i)
   except AssertionError as e:error=str(e)
   parts.append(dict(component=i,completeFaceIds=ids,completeSamples=samples,ordinaryMetric=metric,ordinaryRootProof=proof,rawOrdinaryFailure=error))
  for i,a in enumerate(groups):
   pa=world[a]
   for j in range(i+1,len(groups)):
    pb=world[groups[j]]
    if np.any(pa.max((0,1))<pb.min((0,1)))or np.any(pb.max((0,1))<pa.min((0,1))):edges.append(dict(components=[i,j],strictClosedBoundsDisjoint=True));continue
    contact=exact_finite_contacts(world,a,world,groups[j]);assert contact['allPairsExamined'];positive=[p for p in contact['contacts']if p['dimension']>0 and p['sourcePrimitiveDimensionA']==p['sourcePrimitiveDimensionB']==2]
    if positive:adj[i].add(j);adj[j].add(i)
    edges.append(dict(components=[i,j],completeFiniteContactProof=contact,positiveAreaFacetContactCount=len(positive)))
  reached=set(roots);todo=list(roots)
  while todo:
   a=todo.pop()
   for b in sorted(adj[a]):
    if b not in reached:reached.add(b);todo.append(b)
  rows.append(dict(arithmetic=mode,completeFaces=len(world),completeWorldSHA256=digest(world.astype('<f8').tobytes()),completeGroundFaces=len(ground),completeGroundSHA256=digest(ground.tobytes()),completeTopology=topology,components=parts,completeBodyInterfaces=edges,ordinaryRootCandidates=roots,reachableBodyCandidates=sorted(reached),unresolvedBodyCandidates=sorted(set(adj)-reached)))
 out=dict(rows=rows,rawHeldPhysicalReasons=read(PHYS/'current-podium-only-physical-diagnostic.json')['rawReasons'],sourceGeometryChanges=0,terrainGeometryChanges=0,currentAcceptance=False,actualFloat32ModelMatrixProofStillRequired=True,installationApproved=False,qualification='Complete unchanged original/literal nonzero-area/nonzero-edge bodies have independently measured ordinary ground roots and exact positive-dimensional paths on a frozen held terrain proposal. Remaining BASIC neighbour failure is preserved, no source/actor support bridge or installation acceptance.')
 save(DOC/'diagnostic.json.gz',out)
 paths=[Path(__file__),RUNTIME,rawpath,PHYS/'result.json',PHYS/'current-podium-only-physical-diagnostic.json',INPUT/'check-selection.json.gz',HERE/'xl-lee-kong-two-independent-original-tin-body-graph-diagnostic-v1-20261011.py',HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_shared_edge_component_census_v2_20261011.py',HERE/'exact_original_finite_triangle_contacts_20261010.py',HERE/'original_wall_rim_accounting_20261009.py',HERE/'original_ordinary_rim_accounting_20261009.py']
 spec=importlib.util.spec_from_file_location('vancor_body_ground_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,'complete-original-literal-body-current-proposal-ground-diagnostic-no-acceptance-v1',paths,dict(uids=[selected['uid']],rawHeldPhysicalReasons=out['rawHeldPhysicalReasons'],unresolvedBodyCandidates={r['arithmetic']:r['unresolvedBodyCandidates']for r in rows},currentAcceptance=False,newlyInstalled=0))
 print(json.dumps([dict(arithmetic=r['arithmetic'],roots=r['ordinaryRootCandidates'],reachable=r['reachableBodyCandidates'],unresolved=r['unresolvedBodyCandidates'])for r in rows]))
if __name__=='__main__':main()
