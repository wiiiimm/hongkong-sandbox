"""Exhaustive unchanged two-body interface comparison, not support approval.

Every face pair in the two bodies with a failed selected literal witness is
examined independently in the original, literal and both explicit F32 streams.
No epsilon, welding, point-contact credit or universal GPU inference.
"""
from pathlib import Path
import importlib.util, uuid
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_component_contacts_20261009 import exact_component_contacts

BASE=ROOT/'docs/astra-city/government-import'
BATCH='xl-terrain-recovery-20261011-langham-two-literal-negative-full-body-pairs-v1'
DOC=BASE/BATCH
GRAPH=BASE/'xl-terrain-recovery-20261011-langham-complete-original-edge-contact-graph-v1'
PATHS=BASE/'xl-terrain-recovery-20261011-langham-owned-bounded-carrier-paths-v1'
PROBE=BASE/'government-xl-terrain-recovery-langham-upper-complete-original-current-probe-v1-20261011'
ACTUAL=BASE/'xl-terrain-recovery-20261011-langham-two-current-render-attribute-capture-v1'
OWN='landsd/79318:0'

def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))

def main():
 assert not DOC.exists();refs=[ref(Path(__file__))]
 for folder in [GRAPH,PATHS,PROBE,ACTUAL]:
  receipt=read(folder/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY')
   assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  refs.append(ref(folder/'result.json'))
 graph=read(GRAPH/'diagnostic.json.gz');prior=read(PATHS/'diagnostic.json.gz')
 assert prior['literalSelectedContactFailures']==[90,565]
 row=next(r for r in read(PROBE/'selection.json.gz')['rows']if r['uid']==OWN)
 runtimefile=HERE/'local'/PROBE.name/'runtime-geometry.json.gz'
 runtime=next(r for r in read(runtimefile)['rows']if r['uid']==OWN)
 actual=next(r for r in read(ACTUAL/'actual-render-attributes.json.gz')['rows']if r['uid']==OWN)
 assert row['uid']==runtime['uid']==actual['uid']==OWN
 assert row['sourceSHA256']==runtime['sourceSHA256']==actual['sourceSHA256']
 asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256']
 index=np.asarray(runtime['index'],int).reshape(-1,3)
 assert runtime['index']==actual['completeOriginalIndex']
 literal=np.asarray(runtime['position'],float).reshape(-1,3)
 assert np.array_equal(literal,np.asarray(actual['completeLiteralWorldPosition']).reshape(-1,3))
 worlds=[decode_original_world_triangles(asset.read_bytes()),literal[index],
  np.asarray(actual['completeExplicitLeftAssociatedFloat32WorldPosition']).reshape(-1,3)[index],
  np.asarray(actual['completeExplicitBalancedFloat32WorldPosition']).reshape(-1,3)[index]]
 assert all(w.shape==(18086,3,3)and np.isfinite(w).all()for w in worlds)
 names=['providerOriginal','actualLiteral','explicitLeftAssociatedF32ModelMatrix','explicitBalancedF32ModelMatrix']
 refs.extend(ref(p)for p in [GRAPH/'diagnostic.json.gz',PATHS/'diagnostic.json.gz',
  PROBE/'selection.json.gz',PROBE/'historical-current-manifest.json',runtimefile,
  ACTUAL/'actual-render-attributes.json.gz',asset,HERE/'exact_packed_world_geometry_20261009.py',
  HERE/'exact_original_component_contacts_20261009.py',HERE/'exact_original_shell_intersections_20261009.py',
  HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py'])
 claim=reservations.claim('langham-exhaustive-two-pairs-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600)
 assert claim['ok'];lease=claim['reservation'];records=[]
 try:
  for child,parent in [(90,89),(565,153)]:
   a=graph['components'][child];b=graph['components'][parent]
   assert a['actorUID']==b['actorUID']==OWN
   assert all(0<=f<18086 for f in a['globalOriginalFaces']+b['globalOriginalFaces'])
   modes=[]
   for mode,world in zip(names,worlds):
    result=exact_component_contacts(world,a['globalOriginalFaces'],world,b['globalOriginalFaces'])
    assert result['allPairsExamined']and result['geometryChanges']==0
    positive=[r for r in result['contacts']if r['dimension']>0]
    modes.append(dict(mode=mode,completeWorldSHA256=digest(world.tobytes()),
     fullBodyPairSearch=result,positiveDimensionalContacts=positive,
     pointOnlyContacts=[r for r in result['contacts']if r['dimension']==0]))
    assert reservations.heartbeat(lease)['ok']
   records.append(dict(childOriginalBody=child,parentOriginalBody=parent,
    completeChildOriginalFaces=a['globalOriginalFaces'],completeParentOriginalFaces=b['globalOriginalFaces'],
    independentRepresentations=modes))
  assert all(ref(ROOT/r['path'])==r for r in refs)
  result=dict(uids=[OWN],records=records,rawSelectedLiteralFailuresPreserved=True,
   completeOwnedBodyPartitionUnchanged=True,sourceOnlyFrozenBaseline=True,
   explicitArithmeticNotUniversalGPUCameraGuarantee=True,structuralRootCredit=False,
   currentAcceptance=False,nativeReacceptance=False,sourceGeometryChanges=0,newlyInstalled=0,evidenceRefs=refs)
  save(DOC/'diagnostic.json.gz',result)
  spec=importlib.util.spec_from_file_location('freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py')
  m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
  m.freeze(BATCH,'complete-two-original-body-pair-exact-contact-search-four-independent-streams-v1',
   [ROOT/r['path']for r in refs]+[DOC/'diagnostic.json.gz'],dict(uids=[OWN],
    pairResults=[dict(child=r['childOriginalBody'],parent=r['parentOriginalBody'],
     positivesByMode={m['mode']:len(m['positiveDimensionalContacts'])for m in r['independentRepresentations']})for r in records],
    rawSelectedLiteralFailuresPreserved=True,currentAcceptance=False,newlyInstalled=0))
 finally:assert reservations.release(lease)['ok']

if __name__=='__main__':main()
