"""All585 original cross-actor contacts replayed in literal and both F32 streams.

Searches alternatives among the complete authenticated original-contact
inventory; no invented/welded contacts, unchecked carrier or structural credit.
"""
from pathlib import Path
import importlib.util,time,uuid
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shell_intersections_20261009 import rational_face,intersection_points
from exact_original_component_contacts_20261009 import contact_measure
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261011-langham-complete-original-cross-contacts-render-replay-v1';DOC=BASE/BATCH
ORIGINAL=BASE/'xl-terrain-recovery-20261011-langham-upper-current-native-original-interfaces-v2'
ACTUAL=BASE/'xl-terrain-recovery-20261011-langham-two-current-render-attribute-capture-v1'
GRAPH=BASE/'xl-terrain-recovery-20261011-langham-complete-original-edge-contact-graph-v1'
PARENTS=BASE/'xl-terrain-recovery-20261011-langham-owned-two-f32-parent-interfaces-v1'
UIDS=['landsd/79318:0','landsd/224399:0']
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();refs=[ref(Path(__file__))]
 for folder in [ORIGINAL,ACTUAL,GRAPH,PARENTS]:
  receipt=read(folder/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  refs.extend(ref(folder/p)for p in ['result.json','diagnostic.json.gz']if(folder/p).exists())
 original=read(ORIGINAL/'diagnostic.json.gz');actual={r['uid']:r for r in read(ACTUAL/'actual-render-attributes.json.gz')['rows']};graph=read(GRAPH/'diagnostic.json.gz')
 assets=[next(ROOT/r['path']for r in original['evidenceRefs']if r['sha256']==original['completeSourceSHA256'][uid])for uid in UIDS]
 source=np.concatenate([decode_original_world_triangles(p.read_bytes())for p in assets]);assert source.shape==(38346,3,3)
 modes=['actualLiteral','explicitLeftAssociatedF32ModelMatrix','explicitBalancedF32ModelMatrix'];keys=['completeLiteralWorldPosition','completeExplicitLeftAssociatedFloat32WorldPosition','completeExplicitBalancedFloat32WorldPosition']
 worlds=[]
 for key in keys:
  world=np.concatenate([np.asarray(actual[uid][key]).reshape(-1,3)[np.asarray(actual[uid]['completeOriginalIndex'],int).reshape(-1,3)]for uid in UIDS]);assert world.shape==source.shape and np.isfinite(world).all();worlds.append(world)
 members={f:i for i,c in enumerate(graph['components'])for f in c['globalOriginalFaces']}
 originalcontacts=original['completeEveryRenderableOriginalFacePairContactInventory'];assert originalcontacts['allPairsExamined']and len(originalcontacts['contacts'])==585
 refs.extend(ref(p)for p in [*assets,ACTUAL/'actual-render-attributes.json.gz',HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_shell_intersections_20261009.py',HERE/'exact_original_component_contacts_20261009.py',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py'])
 claim=reservations.claim('langham-all-original-cross-contact-render-replay-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];records=[];last=time.monotonic()
 try:
  for p in originalcontacts['contacts']:
   a,b=p['sourceFaceA'],18086+p['sourceFaceB'];points=intersection_points(rational_face(source[a]),rational_face(source[b]));assert points
   assert contact_measure(points)=={k:p[k]for k in ['dimension','maximumSpanM','bounds','exactPoints']}and p['dimension']>0
   rendered=[]
   for mode,w in zip(modes,worlds):
    points=intersection_points(rational_face(w[a]),rational_face(w[b]));c=contact_measure(points)if points else dict(dimension=-1,maximumSpanM=0,exactPoints=[],bounds=None)
    rendered.append(dict(mode=mode,recomputedExactContact=c,positiveDimensionalContact=c['dimension']>0))
   records.append(dict(ownedSourceFace=a,nativeSourceFace=b-18086,ownedOriginalBody=members[a],nativeOriginalBody=members[b],originalExactContact=p,independentRenderContacts=rendered))
   if time.monotonic()-last>=20:assert reservations.heartbeat(lease)['ok'];print(dict(originalContactsProcessed=len(records),total=585),flush=True);last=time.monotonic()
  assert reservations.heartbeat(lease)['ok'];assert all(ref(ROOT/r['path'])==r for r in refs)
  alternatives={mode:{str(body):[dict(ownedSourceFace=r['ownedSourceFace'],nativeSourceFace=r['nativeSourceFace'])for r in records if r['ownedOriginalBody']==body and r['nativeOriginalBody']==963 and next(c for c in r['independentRenderContacts']if c['mode']==mode)['positiveDimensionalContact']]for body in [34,781,790,947]}for mode in modes}
  out=dict(uids=UIDS,completeOriginalContactInventoryReplayed=records,completeWorldSHA256ByMode={m:digest(w.tobytes())for m,w in zip(modes,worlds)},
   completeSourceWorldSHA256=digest(source.tobytes()),complete585OriginalContactInventoryPreserved=True,
   capturedRenderAlternativeContactsToOnlyNative963=alternatives,allSelectedParentFailuresPreserved=ref(PARENTS/'diagnostic.json.gz'),
   actualAlternativeCarrierFacetExposureStillRequired=True,sourceOnlyFrozenBaseline=True,
   explicitArithmeticNotUniversalGPUCameraGuarantee=True,currentAcceptance=False,nativeReacceptance=False,structuralRootCredit=False,newlyInstalled=0,evidenceRefs=refs)
  save(DOC/'diagnostic.json.gz',out);spec=importlib.util.spec_from_file_location('freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
  m.freeze(BATCH,'complete585-langham-original-cross-actor-contact-render-replay-v1',[ROOT/r['path']for r in refs]+[DOC/'diagnostic.json.gz'],dict(uids=UIDS,completeOriginalContactPairs=585,
   boundedNative963AlternativeCounts={mode:{body:len(rows)for body,rows in groups.items()}for mode,groups in alternatives.items()},currentAcceptance=False,newlyInstalled=0))
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
