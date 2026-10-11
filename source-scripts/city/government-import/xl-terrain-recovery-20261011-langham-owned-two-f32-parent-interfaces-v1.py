"""Every866 selected original parent interface, both explicit renderer F32 orders.

Original/literal prior contact results remain unchanged and hash-bound; every
new F32 interface is independently recomputed with raw negatives retained.
No camera/GPU guarantee, point-glue, native or structural root acceptance.
"""
from pathlib import Path
import importlib.util,time,uuid
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_original_shell_intersections_20261009 import rational_face,intersection_points
from exact_original_component_contacts_20261009 import contact_measure
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261011-langham-owned-two-f32-parent-interfaces-v1';DOC=BASE/BATCH
PATHS=BASE/'xl-terrain-recovery-20261011-langham-owned-bounded-carrier-paths-v1'
ACTUAL=BASE/'xl-terrain-recovery-20261011-langham-two-current-render-attribute-capture-v1'
GRAPH=BASE/'xl-terrain-recovery-20261011-langham-complete-original-edge-contact-graph-v1'
UIDS=['landsd/79318:0','landsd/224399:0']
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();refs=[ref(Path(__file__))]
 for folder in [PATHS,ACTUAL,GRAPH]:
  receipt=read(folder/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  refs.extend(ref(folder/p)for p in ['result.json','diagnostic.json.gz']if(folder/p).exists())
 g=read(GRAPH/'diagnostic.json.gz');prior=read(PATHS/'diagnostic.json.gz');actual={r['uid']:r for r in read(ACTUAL/'actual-render-attributes.json.gz')['rows']}
 keys=['completeExplicitLeftAssociatedFloat32WorldPosition','completeExplicitBalancedFloat32WorldPosition']
 worlds=[]
 for key in keys:
  pieces=[]
  for uid,count in zip(UIDS,[18086,20260]):
   r=actual[uid];assert r['uid']==uid;w=np.asarray(r[key]).reshape(-1,3)[np.asarray(r['completeOriginalIndex'],int).reshape(-1,3)];assert w.shape==(count,3,3)and np.isfinite(w).all();pieces.append(w)
  worlds.append(np.concatenate(pieces))
 literal=np.concatenate([np.asarray(actual[uid]['completeLiteralWorldPosition']).reshape(-1,3)[np.asarray(actual[uid]['completeOriginalIndex'],int).reshape(-1,3)]for uid in UIDS])
 assert digest(literal.tobytes())==prior['completeActualLiteralWorldSHA256']
 assert len(prior['allSelectedOwnedParentInterfaces'])==866
 refs.extend(ref(p)for p in [ACTUAL/'actual-render-attributes.json.gz',
  HERE/'exact_original_shell_intersections_20261009.py',HERE/'exact_original_component_contacts_20261009.py',
  HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py'])
 claim=reservations.claim('langham866-f32-parent-interfaces-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];records=[];last=time.monotonic()
 try:
  for old in prior['allSelectedOwnedParentInterfaces']:
   c=old['selectedOriginalWitness'];a,b=c['globalOriginalFaces']
   assert a in g['components'][c['components'][0]]['globalOriginalFaces']and b in g['components'][c['components'][1]]['globalOriginalFaces']
   new=[]
   for key,w in zip(keys,worlds):
    points=intersection_points(rational_face(w[a]),rational_face(w[b]));contact=contact_measure(points)if points else dict(dimension=-1,exactPoints=[],maximumSpanM=0,bounds=None)
    new.append(dict(mode=key,exactContact=contact,positiveDimensionalContact=contact['dimension']>0))
   records.append(dict(childOriginalBody=old['childOriginalBody'],parentOriginalBody=old['parentOriginalBody'],originalWitness=c,
    rawOriginalAndLiteralInterfaceResultsVerbatim=old['independentRepresentationContacts'],completeTwoActualF32InterfaceResults=new))
   if time.monotonic()-last>=20:assert reservations.heartbeat(lease)['ok'];print(dict(parentInterfaces=len(records),total=866),flush=True);last=time.monotonic()
  assert reservations.heartbeat(lease)['ok'];assert all(ref(ROOT/r['path'])==r for r in refs)
  out=dict(uids=UIDS,all866OriginalParentInterfacesAndTwoExplicitF32Results=records,
   completeExplicitF32WorldSHA256={k:digest(w.tobytes())for k,w in zip(keys,worlds)},
   allOriginalBodyCensusAnd95UnresolvedPreserved=ref(GRAPH/'diagnostic.json.gz'),
   failuresByExplicitArithmetic={key:[r['childOriginalBody']for r in records if not next(p for p in r['completeTwoActualF32InterfaceResults']if p['mode']==key)['positiveDimensionalContact']]for key in keys},
   rawOriginalAndLiteralFailuresPreserved=True,sourceOnlyFrozenBaseline=True,
   explicitArithmeticNotUniversalGPUCameraGuarantee=True,structuralRootCredit=False,
   structuralBridgeCredit=False,nativeReacceptance=False,currentAcceptance=False,newlyInstalled=0,evidenceRefs=refs)
  save(DOC/'diagnostic.json.gz',out);spec=importlib.util.spec_from_file_location('freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
  m.freeze(BATCH,'complete-langham866-selected-parent-interfaces-two-explicit-render-f32-orders-v1',
   [ROOT/r['path']for r in refs]+[DOC/'diagnostic.json.gz'],dict(uids=UIDS,completeOwnedInterfaces=866,
    failuresByExplicitArithmetic=out['failuresByExplicitArithmetic'],sourceOnly=True,currentAcceptance=False,newlyInstalled=0))
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
