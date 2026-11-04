"""Bounded original/literal Langham native963 grade-to-upper contact paths.

Only selected strictly exposed paths are examined; no complete native body or
upper component is accepted. Whole native failures and original contact failures
in either representation remain explicit. All geometry stays unchanged.
"""
from pathlib import Path
from collections import defaultdict,deque
from fractions import Fraction as F
import importlib.util,time,uuid
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shared_edge_component_census_v2_20261011 import exact_nonrendering
from exact_original_shell_intersections_20261009 import intersection_points,rational_face
from exact_original_component_contacts_20261009 import contact_measure
from exact_original_rational_interface_segment_clearance_20261011 import verify as segment_verify
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261011-langham-native963-bounded-exposed-paths-v1';DOC=BASE/BATCH
PROBE=BASE/'government-xl-terrain-recovery-langham-upper-complete-original-current-probe-v1-20261011';GRAPH=BASE/'xl-terrain-recovery-20261011-langham-complete-original-edge-contact-graph-v1';FINITE=BASE/'xl-terrain-recovery-20261011-langham-original-literal-complete-current-finite-v1';GRADE=BASE/'xl-terrain-recovery-20261011-langham-native963-current-grade-diagnostic-v1'
OWN='landsd/79318:0';NATIVE='landsd/224399:0'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();refs=[ref(Path(__file__))]
 for folder in [PROBE,GRAPH,FINITE,GRADE]:
  receipt=read(folder/'result.json')
  with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  refs.extend(ref(folder/p)for p in ['result.json','diagnostic.json.gz']if(folder/p).is_file())
 geometry=HERE/'local'/PROBE.name/'runtime-geometry.json.gz';runtime={r['uid']:r for r in read(geometry)['rows']};selection={r['uid']:r for r in read(PROBE/'selection.json.gz')['rows']};original={};literal={}
 for uid,count in [(OWN,18086),(NATIVE,20260)]:
  r=runtime[uid];row=selection[uid];assert r['uid']==row['uid']==uid;asset=ROOT/row['candidate']['path'];assert ref(asset)['sha256']==row['sourceSHA256']==r['sourceSHA256'];original[uid]=decode_original_world_triangles(asset.read_bytes());literal[uid]=np.asarray(r['position'],float).reshape(-1,3)[np.asarray(r['index'],int).reshape(-1,3)];assert original[uid].shape==literal[uid].shape==(count,3,3);refs.append(ref(asset))
 ground=np.asarray(runtime[NATIVE]['drawnGroundGeometry'],float).reshape(-1,3,3);graph=read(GRAPH/'diagnostic.json.gz');body=[i-18086 for i in graph['components'][963]['globalOriginalFaces']];assert graph['components'][963]['actorUID']==NATIVE and len(body)==2385
 targets=[]
 for c in graph['oneExactPositiveWitnessPerContactingBodyPair']:
  if 963 in c['components']and min(c['components'])<961:
   a,b=c['globalOriginalFaces'];assert a<18086<=b;targets.append(dict(ownedBody=min(c['components']),ownedFace=a,nativeFace=b-18086,originalWitness=c))
 assert len(targets)==7
 finite=next(r for r in read(FINITE/'diagnostic.json.gz')['rows']if r['uid']==NATIVE);grade=read(GRADE/'diagnostic.json.gz');refs.extend(ref(p)for p in [geometry,PROBE/'selection.json.gz',PROBE/'historical-current-manifest.json',HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_shared_edge_component_census_v2_20261011.py',HERE/'exact_original_shell_intersections_20261009.py',HERE/'exact_original_component_contacts_20261009.py',HERE/'exact_original_rational_interface_segment_clearance_20261011.py',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py']);claim=reservations.claim('langham-native963-paths-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];last=time.monotonic()
 def pulse(force=False):
  nonlocal last
  if force or time.monotonic()-last>=20:assert reservations.heartbeat(lease)['ok'];last=time.monotonic()
 try:
  rows=[]
  for mode,worlds,field in [('providerOriginal',original,'completeOriginal'),('actualLiteral',literal,'actualRendered')]:
   world=worlds[NATIVE];assert digest(world.tobytes())==finite['completeOriginalWorldSHA256'if field=='completeOriginal'else'completeActualRenderedWorldSHA256'];assert digest(ground.tobytes())==finite['completeGroundSHA256'];proofs={r['sourceFace']:r[field]for r in finite['allFaces']};strict={i for i in body if proofs[i]['groundProjectionCovered']is True and F(proofs[i]['exactCertifiedLowerClearanceM'])>0};g=next(r for r in grade['rows']if r['mode']==mode);assert digest(world.tobytes())==g['completeNativeWorldSHA256'];roots=g['positiveDimensionalGradeFaces'];edges=defaultdict(list)
   for i in body:
    if exact_nonrendering(world[i]):continue
    for a,b in zip(world[i],np.roll(world[i],-1,axis=0)):
     if tuple(a)!=tuple(b):edges[tuple(sorted([tuple(a),tuple(b)]))].append(i)
   neighbours=defaultdict(list);first=[]
   for edge,ids in sorted(edges.items()):
    for i in ids:
     for j in ids:
      if i==j:continue
      if i in strict and j in strict:neighbours[i].append((j,edge))
      elif i in roots and j in strict:first.append((i,j,edge))
   parents={};seeds=[];firstproofs=[]
   for i,j,edge in first:
    if j in parents:continue
    exactedge=[[str(F(float(v)))for v in p]for p in edge];proof=segment_verify(exactedge,ground);pulse()
    if proof['strictlyExposedWholePositiveInterface']:
     parents[j]=(i,edge);seeds.append(j);firstproofs.append(dict(gradeFace=i,strictFace=j,exactSharedEdge=exactedge,completeExposedEdgeProof=proof))
   q=deque(seeds)
   while q:
    i=q.popleft()
    for j,e in sorted(neighbours[i]):
     if j not in parents:parents[j]=(i,e);q.append(j)
   paths=[]
   for target in targets:
    n=target['nativeFace'];a=target['ownedFace'];path=[];cur=n
    if cur in parents:
     while cur in parents:
      prev,edge=parents[cur];path.append(dict(fromFace=prev,toFace=cur,exactSharedEdge=[[str(F(float(v)))for v in p]for p in edge],strictCompleteFacetProof=proofs[cur],wholeEdgeExposureFromWholeStrictFacet=True));cur=prev
     path.reverse();assert cur in roots
    contact=contact_measure(intersection_points(rational_face(worlds[OWN][a]),rational_face(world[n])));pulse();positive=contact['dimension']>0;record=dict(**target,boundedGradeFace=cur if path else None,exactSharedEdgePath=path,allPathFacesHaveStrictWholeFacetExposure=bool(path),recomputedExactOwnedContact=contact,actualContactPositiveDimensional=positive,nativeParticipatingWholeFacetProof=proofs[n],ownedParticipatingFacet=worlds[OWN][a].tolist(),pathDoesNotCertifyOtherNativeFaces=True);paths.append(record);print(dict(mode=mode,ownedBody=target['ownedBody'],nativeFace=n,pathFaces=len(path),contactDimension=contact['dimension']),flush=True)
   rows.append(dict(mode=mode,completeNativeWorldSHA256=digest(world.tobytes()),completeOwnedWorldSHA256=digest(worlds[OWN].tobytes()),completeGroundSHA256=digest(ground.tobytes()),originalBodyFaceInventory=body,strictCompleteExposedBodyFaces=len(strict),selectedFirstGradeEdges=firstproofs,boundedParticipatingPaths=paths,allSevenPathsAndContactsPositive=all(p['allPathFacesHaveStrictWholeFacetExposure']and p['actualContactPositiveDimensional']for p in paths),allOtherNativeFailuresPreserved=ref(FINITE/'diagnostic.json.gz'),completeNativeReacceptance=False,rootOrStructuralCredit=False));pulse(True)
  pulse(True);assert all(ref(ROOT/r['path'])==r for r in refs);out=dict(uids=[OWN,NATIVE],rows=rows,frozenBaselineManifest=ref(PROBE/'historical-current-manifest.json'),sourceOnlyFrozenCurrentBaseline=True,noFreshCurrentReacceptance=True,diagnosticOnly=True,nativeReacceptance=False,currentAcceptance=False,structuralRootCredit=False,sourceGeometryChanges=0,newlyInstalled=0,evidenceRefs=refs);save(DOC/'diagnostic.json.gz',out);spec=importlib.util.spec_from_file_location('freeze_langham_paths',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,'bounded-langham-native963-original-literal-exposed-grade-to-original-upper-contact-path-diagnostic-v1',[ROOT/r['path']for r in refs]+[DOC/'diagnostic.json.gz'],dict(uids=[OWN,NATIVE],diagnosticOnly=True,allSevenPathsAndContactsPositive=all(r['allSevenPathsAndContactsPositive']for r in rows),nativeReacceptance=False,currentAcceptance=False,newlyInstalled=0))
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
