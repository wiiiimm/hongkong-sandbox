"""Complete actual face search for a new body565 contact, no support credit.

Hosts are reached from the bounded native963 using previously recomputed
positive literal contacts, excluding565 and all95 original unrooted bodies.
No point-only bridge, rounding tolerance, source edit or native reapproval.
"""
from pathlib import Path
from collections import defaultdict,deque
import importlib.util,uuid
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_original_component_contacts_20261009 import exact_component_contacts
BASE=ROOT/'docs/astra-city/government-import'
BATCH='xl-terrain-recovery-20261011-langham-565-complete-literal-rooted-host-search-v1';DOC=BASE/BATCH
GRAPH=BASE/'xl-terrain-recovery-20261011-langham-complete-original-edge-contact-graph-v1'
PATHS=BASE/'xl-terrain-recovery-20261011-langham-owned-bounded-carrier-paths-v1'
ALTERNATE=BASE/'xl-terrain-recovery-20261011-langham-two-literal-negative-full-body-pairs-v1'
PROBE=BASE/'government-xl-terrain-recovery-langham-upper-complete-original-current-probe-v1-20261011'
OWN='landsd/79318:0';NATIVE='landsd/224399:0'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();refs=[ref(Path(__file__))]
 for folder in [GRAPH,PATHS,ALTERNATE,PROBE]:
  r=read(folder/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  refs.extend(ref(folder/p)for p in ['result.json','diagnostic.json.gz']if(folder/p).exists())
 g=read(GRAPH/'diagnostic.json.gz');old=read(PATHS/'diagnostic.json.gz')
 alternate=read(ALTERNATE/'diagnostic.json.gz');adj=defaultdict(set);used=[]
 for record in old['allSelectedOwnedParentInterfaces']:
  a,b=record['childOriginalBody'],record['parentOriginalBody']
  if 565 in [a,b]:continue
  actual=record['independentRepresentationContacts'][1]
  assert actual['mode']=='actualLiteral'
  if actual['positiveDimensionalContact']:adj[a].add(b);adj[b].add(a);used.append(record)
 r=next(r for r in alternate['records']if r['childOriginalBody']==90)
 actual=next(r for r in r['independentRepresentations']if r['mode']=='actualLiteral')
 assert actual['positiveDimensionalContacts'];adj[90].add(89);adj[89].add(90)
 reached={963};todo=deque([963])
 while todo:
  for b in adj[todo.popleft()]-reached:reached.add(b);todo.append(b)
 assert 565 not in reached and not set(old['completeUnreachedOwnedOriginalBodies'])&reached
 assert reached<=set(range(961))|{963}
 runtimefile=HERE/'local'/PROBE.name/'runtime-geometry.json.gz';runtime={r['uid']:r for r in read(runtimefile)['rows']}
 worlds=[]
 for uid,count in [(OWN,18086),(NATIVE,20260)]:
  r=runtime[uid];assert r['uid']==uid
  w=np.asarray(r['position'],float).reshape(-1,3)[np.asarray(r['index'],int).reshape(-1,3)]
  assert w.shape==(count,3,3)and np.isfinite(w).all();worlds.append(w)
 world=np.concatenate(worlds);assert digest(world.tobytes())==old['completeActualLiteralWorldSHA256']
 faces=g['components'][565]['globalOriginalFaces'];assert len(faces)==9
 hostfaces=sorted(f for i in reached for f in g['components'][i]['globalOriginalFaces'])
 refs.extend(ref(p)for p in [runtimefile,HERE/'exact_original_component_contacts_20261009.py',
  HERE/'exact_original_shell_intersections_20261009.py',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py'])
 claim=reservations.claim('langham565-all-rooted-host-faces-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600)
 assert claim['ok'];lease=claim['reservation']
 try:
  contacts=exact_component_contacts(world,faces,world,hostfaces)
  assert contacts['allPairsExamined'];members={f:i for i,c in enumerate(g['components'])for f in c['globalOriginalFaces']}
  positive=[dict(**r,otherOriginalBody=members[r['sourceFaceB']])for r in contacts['contacts']if r['dimension']>0]
  assert all(p['otherOriginalBody']in reached for p in positive)
  assert reservations.heartbeat(lease)['ok'];assert all(ref(ROOT/r['path'])==r for r in refs)
  out=dict(uids=[OWN,NATIVE],targetBody=565,completeTargetOriginalFaces=faces,
   completeAllowedLiteralGeometricHostBodies=sorted(reached),completeAllowedLiteralHostFaces=hostfaces,
   everyOriginalUnrootedBodyExcluded=True,boundedNativeBodyOnly=963,
   completeActualLiteralWorldSHA256=digest(world.tobytes()),allExactLiteralFacePairs=contacts,
   allPositiveDimensionalContacts=positive,rawPriorSelectedWitnessFailuresPreserved=True,
   noPointOnlyStructuralBridge=True,rootAndNativeAcceptanceStillRequired=True,
   structuralRootCredit=False,currentAcceptance=False,nativeReacceptance=False,
   sourceOnlyFrozenBaseline=True,newlyInstalled=0,evidenceRefs=refs)
  save(DOC/'diagnostic.json.gz',out)
  spec=importlib.util.spec_from_file_location('freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
  m.freeze(BATCH,'complete-langham565-actual-literal-contact-search-all-independent-bounded-host-faces-v1',
   [ROOT/r['path']for r in refs]+[DOC/'diagnostic.json.gz'],dict(uids=[OWN,NATIVE],
    completeTargetFaces=9,completeHostBodies=len(reached),completeHostFaces=len(hostfaces),
    positiveDimensionalLiteralContacts=len(positive),allPairsExamined=True,currentAcceptance=False,newlyInstalled=0))
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
