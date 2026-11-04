"""Complete eight original body565/153 interfaces and separate literal images.

The actual literal full-body pair has no exact contacts. This diagnostic keeps
that negative and tests unchanged affine correspondence of original interfaces.
No authored-role, root/bridge, current acceptance or native reapproval.
"""
from pathlib import Path
import importlib.util,uuid
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_interface_literal_affine_association_v1_20261011 import verify
BASE=ROOT/'docs/astra-city/government-import'
BATCH='xl-terrain-recovery-20261011-langham-565-original-literal-interface-association-v1';DOC=BASE/BATCH
PRIOR=BASE/'xl-terrain-recovery-20261011-langham-two-literal-negative-full-body-pairs-v1'
PROBE=BASE/'government-xl-terrain-recovery-langham-upper-complete-original-current-probe-v1-20261011'
GRAPH=BASE/'xl-terrain-recovery-20261011-langham-complete-original-edge-contact-graph-v1'
ACTUAL=BASE/'xl-terrain-recovery-20261011-langham-two-current-render-attribute-capture-v1'
NEGATIVE=BASE/'xl-terrain-recovery-20261011-langham-565-complete-literal-rooted-host-search-v1'
UID='landsd/79318:0'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();refs=[ref(Path(__file__))]
 for folder in [PRIOR,PROBE,GRAPH,ACTUAL,NEGATIVE]:
  r=read(folder/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  refs.extend(ref(folder/p)for p in ['result.json','diagnostic.json.gz']if(folder/p).exists())
 row=next(r for r in read(PROBE/'selection.json.gz')['rows']if r['uid']==UID)
 asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256']=='1be9a6399ce7e447ae734182f278bef08e7bbb58aa97cb8a468b133d175c00e4'
 original=decode_original_world_triangles(asset.read_bytes());runtimefile=HERE/'local'/PROBE.name/'runtime-geometry.json.gz'
 r=next(r for r in read(runtimefile)['rows']if r['uid']==UID);index=np.asarray(r['index'],int).reshape(-1,3);literal=np.asarray(r['position']).reshape(-1,3)[index]
 assert original.shape==literal.shape==(18086,3,3)
 prior=next(r for r in read(PRIOR/'diagnostic.json.gz')['records']if r['childOriginalBody']==565)
 modes={r['mode']:r for r in prior['independentRepresentations']}
 assert len(modes['providerOriginal']['positiveDimensionalContacts'])==8 and not modes['actualLiteral']['fullBodyPairSearch']['contacts']
 assert all(len(modes[n]['positiveDimensionalContacts'])==8 for n in ['explicitLeftAssociatedF32ModelMatrix','explicitBalancedF32ModelMatrix'])
 g=read(GRAPH/'diagnostic.json.gz');assert prior['completeChildOriginalFaces']==g['components'][565]['globalOriginalFaces']and prior['completeParentOriginalFaces']==g['components'][153]['globalOriginalFaces']
 assert not read(NEGATIVE/'diagnostic.json.gz')['allPositiveDimensionalContacts']
 refs.extend(ref(p)for p in [asset,runtimefile,PROBE/'selection.json.gz',PROBE/'historical-current-manifest.json',ACTUAL/'actual-render-attributes.json.gz',
  HERE/'exact_original_interface_literal_affine_association_v1_20261011.py',HERE/'test_exact_original_interface_literal_affine_association_v1_20261011.py',
  HERE/'exact_original_component_contacts_20261009.py',HERE/'exact_original_shell_intersections_20261009.py',HERE/'exact_packed_world_geometry_20261009.py',
  HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py'])
 claim=reservations.claim('langham565-source-literal-affine-association-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];records=[]
 try:
  for p in modes['providerOriginal']['positiveDimensionalContacts']:
   a,b=p['sourceFaceA'],p['sourceFaceB'];assert a in prior['completeChildOriginalFaces']and b in prior['completeParentOriginalFaces']
   binding={n:digest(t.tobytes())for n,t in zip(['originalFaceASHA256','originalFaceBSHA256','actualLiteralFaceASHA256','actualLiteralFaceBSHA256'],[original[a],original[b],literal[a],literal[b]])}
   proof=verify(original[a],original[b],literal[a],literal[b],expected_binding=binding)
   assert proof['completeOriginalExactInterface']=={k:p[k]for k in ['dimension','maximumSpanM','bounds','exactPoints']}
   assert not proof['actualLiteralPositiveDimensionalContact']and proof['actualLiteralExactContact']['dimension']==-1
   records.append(dict(sourceFaceA=a,sourceFaceB=b,proof=proof));assert reservations.heartbeat(lease)['ok']
  assert all(ref(ROOT/r['path'])==r for r in refs)
  out=dict(uids=[UID],sourceSHA256=row['sourceSHA256'],completeOriginalWorldSHA256=digest(original.tobytes()),completeActualLiteralWorldSHA256=digest(literal.tobytes()),
   completeBody565OriginalFaces=prior['completeChildOriginalFaces'],completeBody153OriginalFaces=prior['completeParentOriginalFaces'],
   allEightOriginalInterfacesAndSeparateLiteralAffineImages=records,
   allEightCompleteAffineAssociationsWithinExistingFixedBand=all(r['proof']['wholeConvexOriginalInterfaceAssociationProved']for r in records),
   actualLiteralFullBodyPairZeroContactsPreserved=True,actualF32BothArithmeticOrdersEightExactContactsPreserved=ref(PRIOR/'diagnostic.json.gz'),
   sourceOnlyFrozenBaseline=True,authoredRoleCertified=False,currentAcceptance=False,structuralRootCredit=False,structuralBridgeCredit=False,
   nativeReacceptance=False,sourceGeometryChanges=0,newlyInstalled=0,evidenceRefs=refs)
  save(DOC/'diagnostic.json.gz',out);spec=importlib.util.spec_from_file_location('freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
  m.freeze(BATCH,'complete-langham565-eight-source-authored-separate-literal-affine-interface-diagnostic-v1',
   [ROOT/r['path']for r in refs]+[DOC/'diagnostic.json.gz'],dict(uids=[UID],completeOriginalInterfaces=8,
    allCompleteAffineAssociationsWithinExistingFixedBand=out['allEightCompleteAffineAssociationsWithinExistingFixedBand'],
    actualLiteralExactContacts=0,structuralRootCredit=False,currentAcceptance=False,newlyInstalled=0))
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
