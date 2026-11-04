"""UNEXECUTED receipt-only recovery; no projection or contact math rerun.

Preserve full16 numerical rows and failed v2 byte-for-byte. Reconstruct every
bound complete world tuple from exact completed source/actual inputs, then freeze
with the missing required four-UID summary. No acceptance, candidate or repair.
"""
from pathlib import Path
import importlib.util,json,subprocess,sys,uuid
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import'
BATCH='xl-terrain-recovery-20261011-sparkle-retained-market-overlap-receipt-recovery-v3';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
NUMERIC=BASE/'xl-terrain-recovery-20261011-sparkle-retained-market-complete-projection-contact-diagnostic-v2'
FAILURE=BASE/'government-xl-sparkle-retained-market-overlap-v2-freezer-summary-failure-20261011'
OWNED=BASE/'xl-terrain-recovery-20261011-sparkle-tower-podium-two-current-render-attribute-capture-v1'
RETAINED=BASE/'xl-terrain-recovery-20261011-sparkle-retained-market-two-current-render-ground-capture-v2'
UIDS=['landsd/242198:0','landsd/228000:0','landsd/113733:0','landsd/138091:0'];COUNTS=[12875,6806,15641,25224]
MODES=['originalSource','actualLiteral','explicitLeftAssociatedFloat32','explicitBalancedFloat32']
MANIFEST='947f0a3b3a1d7167a9f98074af35d4030ff0245e121ee682eed4f9ab9baedfa6'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def verify(r):
 p=ROOT/r['path'];assert p.is_file()and ref(p)==r;return p
def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease)and not DOC.exists()
 manifest=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifest);assert start['sha256']==MANIFEST
 assert not(NUMERIC/'result.json').exists(),'Do not duplicate an existing complete receipt'
 for name,archive in [('diagnostic.json.gz','complete-numeric-diagnostic.json.gz'),('partial-overlap-diagnostic.json.gz','partial-overlap-diagnostic.json.gz'),('historical-current-manifest.json','historical-current-manifest.json')]:
  assert(NUMERIC/name).read_bytes()==(FAILURE/archive).read_bytes()
 source=HERE/'xl-terrain-recovery-20261011-sparkle-retained-market-complete-projection-contact-diagnostic-v2.py';assert source.read_bytes()==(FAILURE/'executed-source-v2.py').read_bytes()
 failed=read(FAILURE/'failed-execution.json');assert failed['completeNumericalRows']==16 and not failed['completedJobCreated']and failed['supervisorReleased']
 d=read(NUMERIC/'diagnostic.json.gz');assert d['currentManifest']==start and d['wholeOriginalFacets']==60546 and not d['currentAcceptance']and not d['nativeReacceptance']
 assert not d['sourceGeometryChanges']and not d['terrainChanges'];refs=[ref(Path(__file__)),ref(HERE/'exact_packed_world_geometry_20261009.py'),ref(HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py'),ref(source),*[ref(p)for p in sorted(FAILURE.iterdir())if p.is_file()],*[ref(p)for p in sorted(NUMERIC.iterdir())if p.is_file()],*d['evidenceRefs']]
 receipts=[]
 for folder in [OWNED,RETAINED]:
  receipt=read(folder/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  for pin in receipt['evidenceRefs']:verify(pin)
  receipts.append(receipt);refs.extend([ref(folder/'result.json'),*receipt['evidenceRefs']])
 assert receipts[0]['jobId']=='80b48d4b97a689b19e34ace263ab907be1f5ebaa7b7a7be57dda9892d656487c'
 assert receipts[1]['jobId']=='4832a8e05527b49eca61ff04478d7ce4d9a3a8dcc315fdf1756171293ab144b9'
 oi=read(OWNED/'literal-source-inputs.json.gz');ri=read(RETAINED/'native-render-inputs.json.gz');assert oi['currentManifest']==ri['currentManifest']==start
 oa=read(OWNED/'actual-render-attributes.json.gz');ra=read(RETAINED/'native-render-ground.json.gz')
 assert [r['uid']for r in oi['rows']+ri['rows']]==[r['uid']for r in oa['rows']+ra['rows']]==UIDS
 bindings=[]
 for inp,actual,uid,count in zip(oi['rows']+ri['rows'],oa['rows']+ra['rows'],UIDS,COUNTS):
  asset=ROOT/inp['path']if uid in UIDS[:2]else verify(inp['sourceAsset']);assert ref(asset)['sha256']==actual['sourceSHA256'];ids=np.asarray(actual['completeOriginalIndex'],int);assert len(ids)==3*count
  worlds=[decode_original_world_triangles(asset.read_bytes())]
  for key in ['completeLiteralWorldPosition','completeExplicitLeftAssociatedFloat32WorldPosition','completeExplicitBalancedFloat32WorldPosition']:
   pos=np.asarray(actual[key],float).reshape(-1,3);assert np.isfinite(pos).all()and ids.min()>=0 and ids.max()<len(pos);worlds.append(pos[ids].reshape(-1,3,3))
  for mode,world in zip(MODES,worlds):
   assert world.shape==(count,3,3)and np.isfinite(world).all();bindings.append(dict(mode=mode,uid=uid,sourceSHA256=actual['sourceSHA256'],completeFacets=count,completeIndexedWorldSHA256=digest(world.tobytes())))
 assert bindings==d['completeFourStreamWorldBindings'];bound={(b['mode'],b['uid']):b for b in bindings};expected=[(m,a,b)for m in MODES for a in UIDS[:2]for b in UIDS[2:]]
 assert [(r['mode'],r['ownedUID'],r['retainedUID'])for r in d['rows']]==expected;pure={}
 for row in d['rows']:
  mode,a,b=row['mode'],row['ownedUID'],row['retainedUID'];proof=row['proof'];first,second=bound[(mode,a)],bound[(mode,b)];key=(first['completeIndexedWorldSHA256'],second['completeIndexedWorldSHA256'])
  assert proof['ownedWorldSHA256']==key[0]and proof['retainedWorldSHA256']==key[1]
  assert proof['ownedFacets']==first['completeFacets']and proof['retainedFacets']==second['completeFacets']
  assert proof['totalTrianglePairs']==proof['strictlyXZDisjointPairs']==first['completeFacets']*second['completeFacets']
  assert proof['exactInclusiveXZCandidatePairs']==proof['strictly3DDisjointAmongXZCandidates']==0
  assert proof['allClosedProjectedIntersections']==proof['allActual3DContacts']==proof['exactZero3DFacetPairsRetainedUncredited']==[]
  assert proof['completeProjectedAndContactPairCensus']and proof['projectedTrianglePairAreasAreNotUnionArea']and proof['noCollisionExemption']and proof['noSupportOrTerrainRetentionCredit']
  if row['reusedExactWorldTuple']:assert key in pure and pure[key]==proof
  else:assert key not in pure;pure[key]=proof
 for pin in refs:verify(pin)
 assert ref(manifest)==start and reservations.owns(lease)
 DOC.mkdir(parents=True);save(DOC/'receipt-recovery.json',dict(uids=UIDS,completedNumericOutput=ref(NUMERIC/'diagnostic.json.gz'),executedNumericProducer=ref(source),failedV2=ref(FAILURE/'failed-execution.json'),completeWorldTupleReplayBindings=bindings,completeLabelledWorldPairs=16,exactProjectedCandidatePairsByRow=[0]*16,actual3DContactCountsByRow=[0]*16,noProjectionOrContactRerun=True,currentAcceptance=False,nativeReacceptance=False,newlyInstalled=0))
 refs.append(ref(DOC/'receipt-recovery.json'));spec=importlib.util.spec_from_file_location('sparkle_overlap_receipt_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 m.freeze(BATCH,'complete-numeric-sparkle-market-overlap-uid-summary-receipt-recovery-v3',[verify(r)for r in {r['path']:r for r in refs}.values()],dict(uids=UIDS,currentManifest=start,completeOriginalFacets=60546,completeLabelledWorldPairs=16,exactProjectedCandidatePairs=0,actual3DContacts=0,noProjectionOrContactRerun=True,currentAcceptance=False,nativeReacceptance=False,sourceGeometryChanges=0,terrainChanges=0,newlyInstalled=0))
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists()and not LOCAL.exists();claim=reservations.claim('sparkle-market-overlap-receipt-'+str(uuid.uuid4()),['building:'+u for u in UIDS]+['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)))
 subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
