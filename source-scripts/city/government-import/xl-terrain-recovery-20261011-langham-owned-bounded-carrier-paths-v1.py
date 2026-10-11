"""Complete owned original path census, only bounded qualified native963 leads.

Literal contacts are independently recomputed, including all failures. Geometric
paths and complete owned clearance are not whole-source/current acceptance.
"""
from pathlib import Path
from collections import defaultdict,deque
import importlib.util,time,uuid
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_component_contacts_20261009 import contact_measure
from exact_original_shell_intersections_20261009 import intersection_points,rational_face
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261011-langham-owned-bounded-carrier-paths-v1';DOC=BASE/BATCH
GRAPH=BASE/'xl-terrain-recovery-20261011-langham-complete-original-edge-contact-graph-v1';BOUNDED=BASE/'xl-terrain-recovery-20261011-langham-native963-bounded-exposed-paths-v1';PROBE=BASE/'government-xl-terrain-recovery-langham-upper-complete-original-current-probe-v1-20261011';FINITE=BASE/'xl-terrain-recovery-20261011-langham-original-literal-complete-current-finite-v1';OWN='landsd/79318:0';NATIVE='landsd/224399:0'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();refs=[ref(Path(__file__))]
 for folder in [GRAPH,BOUNDED,PROBE,FINITE]:
  receipt=read(folder/'result.json')
  with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  refs.extend(ref(folder/p)for p in ['result.json','diagnostic.json.gz']if(folder/p).exists())
 runtimepath=HERE/'local'/PROBE.name/'runtime-geometry.json.gz';runtime={r['uid']:r for r in read(runtimepath)['rows']};selection={r['uid']:r for r in read(PROBE/'selection.json.gz')['rows']};original=[];literal=[]
 for uid,count in [(OWN,18086),(NATIVE,20260)]:
  r=runtime[uid];row=selection[uid];assert r['uid']==row['uid']==uid;asset=ROOT/row['candidate']['path'];assert ref(asset)['sha256']==row['sourceSHA256']==r['sourceSHA256'];world=decode_original_world_triangles(asset.read_bytes());current=np.asarray(r['position'],float).reshape(-1,3)[np.asarray(r['index'],int).reshape(-1,3)];assert world.shape==current.shape==(count,3,3);original.append(world);literal.append(current);refs.append(ref(asset))
 original=np.concatenate(original);literal=np.concatenate(literal);g=read(GRAPH/'diagnostic.json.gz');assert len(g['components'])==1856 and all(g['components'][i]['actorUID']==OWN for i in range(961));assert g['components'][963]['actorUID']==NATIVE
 bounded=read(BOUNDED/'diagnostic.json.gz');assert all(r['allSevenPathsAndContactsPositive']for r in bounded['rows']);allowed=set(range(961))|{963};adj=defaultdict(list)
 for c in g['oneExactPositiveWitnessPerContactingBodyPair']:
  a,b=c['components']
  if a in allowed and b in allowed:adj[a].append((b,c));adj[b].append((a,c))
 parents={};reached={963};q=deque([963])
 while q:
  p=q.popleft()
  for child,c in sorted(adj[p],key=lambda r:r[0]):
   if child not in reached:reached.add(child);parents[child]=(p,c);q.append(child)
 missing=sorted(set(range(961))-reached);assert len(parents)==866 and len(missing)==95
 finite=next(r for r in read(FINITE/'diagnostic.json.gz')['rows']if r['uid']==OWN);assert not finite['unprovedOriginalFaceBounds']and not finite['unprovedActualRenderedFaceBounds'];assert digest(original[:18086].tobytes())==finite['completeOriginalWorldSHA256']and digest(literal[:18086].tobytes())==finite['completeActualRenderedWorldSHA256'];refs.extend(ref(p)for p in [runtimepath,PROBE/'selection.json.gz',PROBE/'historical-current-manifest.json',HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_component_contacts_20261009.py',HERE/'exact_original_shell_intersections_20261009.py',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py']);claim=reservations.claim('langham-owned-bounded-paths-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];last=time.monotonic()
 def pulse(force=False):
  nonlocal last
  if force or time.monotonic()-last>=20:assert reservations.heartbeat(lease)['ok'];last=time.monotonic()
 try:
  records=[]
  for child,(parent,c)in sorted(parents.items()):
   a,b=c['globalOriginalFaces'];assert a in g['components'][c['components'][0]]['globalOriginalFaces']and b in g['components'][c['components'][1]]['globalOriginalFaces'];pair=[]
   for mode,world in [('providerOriginal',original),('actualLiteral',literal)]:
    points=intersection_points(rational_face(world[a]),rational_face(world[b]));contact=contact_measure(points)if points else dict(dimension=-1,exactPoints=[],maximumSpanM=0,bounds=None)
    if mode=='providerOriginal':assert contact==c['exactContact']and contact['dimension']>0
    pair.append(dict(mode=mode,recomputedExactFaceContact=contact,positiveDimensionalContact=contact['dimension']>0))
   records.append(dict(childOriginalBody=child,parentOriginalBody=parent,selectedOriginalWitness=c,independentRepresentationContacts=pair));pulse()
   if len(records)%80==0:print(dict(ownedBodiesProcessed=len(records),totalSelectedBodies=len(parents),literalContactFailures=sum(not r['independentRepresentationContacts'][1]['positiveDimensionalContact']for r in records)),flush=True)
  pulse(True);assert all(ref(ROOT/r['path'])==r for r in refs);out=dict(uids=[OWN,NATIVE],completeOriginalWorldSHA256=digest(original.tobytes()),completeActualLiteralWorldSHA256=digest(literal.tobytes()),boundedNativeBodyOnly=963,noOtherNativeBodyUsedAsRootOrBridge=True,allSelectedOwnedParentInterfaces=records,selectedOriginalBodiesReachOnlyBoundedCarrier=866,completeUnreachedOwnedOriginalBodies=missing,completeUnreachedOwnedOriginalFaces=sorted(f for i in missing for f in g['components'][i]['globalOriginalFaces']),allOriginalOwnedBodyPartitionRetained=True,literalSelectedContactFailures=[r['childOriginalBody']for r in records if not r['independentRepresentationContacts'][1]['positiveDimensionalContact']],boundedActualNativePathsReceipt=ref(BOUNDED/'diagnostic.json.gz'),completeOwnedFiniteReceipt=ref(FINITE/'diagnostic.json.gz'),allOtherNativeNegativeFacesUncredited=True,frozenBaselineManifest=ref(PROBE/'historical-current-manifest.json'),sourceOnlyFrozenCurrentBaseline=True,noFreshCurrentReacceptance=True,diagnosticOnly=True,currentAcceptance=False,nativeReacceptance=False,structuralRootCredit=False,sourceGeometryChanges=0,newlyInstalled=0,evidenceRefs=refs);save(DOC/'diagnostic.json.gz',out);s=importlib.util.spec_from_file_location('freeze_langham_owned_paths',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.freeze(BATCH,'complete-langham-owned-original-bounded-carrier-parent-path-and-independent-literal-contact-diagnostic-v1',[ROOT/r['path']for r in refs]+[DOC/'diagnostic.json.gz'],dict(uids=[OWN,NATIVE],selectedOwnBodies=866,unresolvedOwnBodies=95,literalSelectedContactFailures=out['literalSelectedContactFailures'],sourceOnlyFrozenCurrentBaseline=True,currentAcceptance=False,nativeReacceptance=False,newlyInstalled=0))
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
