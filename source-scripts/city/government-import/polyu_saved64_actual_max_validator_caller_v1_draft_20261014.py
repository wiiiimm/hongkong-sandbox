"""UNEXECUTED saved candidate MAX64 + fresh geometry-bound metadata validator."""
from pathlib import Path
import json,sys,time,uuid,subprocess,hashlib,copy,importlib.util
from run import ROOT,HERE,read,save,connect,reservations
from exact_distinct_evidence_refs_v1_20261014 import distinct_refs
from polyu_compact_runtime_mesh_projection_v1_draft_20261014 import mesh_binding
from polyu_saved64_site_selection_v1_draft_20261014 import select
from native_patch_resolution import finalize_overlap_evidence
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-polyu-saved64-actual-max-reviewed-validator-v1-20261014'
DOC=BASE/BATCH;PROPOSAL=BASE/(BATCH+'-proposal');LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
RUNTIME=HERE/'polyu_saved64_actual_max_full_ray_runtime_v1_draft_20261014.mjs'
OVERLAP=BASE/'government-xl-polyu-saved-append-overlap-ancestry-v1-20261014'
CAPTURE=BASE/'government-xl-polyu-append-source-region-historical-production-v1-20261014'
APPEND=BASE/'government-xl-polyu-append-source-region-residual-repair-v1-20261014'
RECEIPTS=[(OVERLAP,'ab3f9d0264fb5047ff89185cd8dc7b95eb84e29a7f44df17d8f595dd599e3ece'),
 (CAPTURE,'62d0bea3f201479354bd87fff2ef10b7a1aa14757019f1f4439e6a7d28cf8a37'),
 (APPEND,'22f69c119f28eb85478f89feb6f1b6d8f1fd5ba2d90148052d11ca55dc09dd2e')]
FREEZER=HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py'
def ref(path):return dict(path=str(Path(path).resolve().relative_to(ROOT)),sha256=hashlib.sha256(Path(path).read_bytes()).hexdigest())
def check(q):
 p=(ROOT/q['path']).resolve();assert p.is_relative_to(ROOT)and ref(p)==q,q;return p
def canonical(patch):return hashlib.sha256((json.dumps(patch,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode()).hexdigest()
def module(path):
 s=importlib.util.spec_from_file_location('polyu_saved64_'+Path(path).stem.replace('-','_'),path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def load():
 pins=read(PROPOSAL/'draft-pins.json');assert pins['caller']==ref(Path(__file__))and pins['runtime']==ref(RUNTIME)
 for q in distinct_refs(pins['codeRefs']+pins['inputRefs']):check(q)
 for folder,jid in RECEIPTS:
  receipt=read(folder/'result.json');cert=read(folder/'ROOT-VERIFIED.json')
  assert receipt['jobId']==cert['jobId']==jid and cert['exactNeonReadback']and cert['allEvidenceHashesVerified']and cert['leaseReleased']
 summary=read(OVERLAP/'complete-overlap-summary.json');m=summary['measurement']
 assert summary['completeCandidateFacets']==148459 and summary['positiveAreaPairs']==1571304 and summary['sourcePlaneCount']==3197
 assert m==pins['completeSavedMeasurement']and m['nativeProjectedExcessM2']==3370.637870296836
 candidate=read(CAPTURE/'private-native-terrain-candidate.json.gz');assert not candidate['nativeMesh'].get('sourceOverlap')
 inp=read(CAPTURE/'input.json.gz');assert inp['historicalReplay']and not inp['currentAcceptance']
 assert mesh_binding({k:candidate['nativeMesh'][k]for k in ['position','index']})==inp['completeMeshBinding']==pins['completeMeshBinding']
 assert canonical(candidate)==pins['candidateCanonicalSHA256']and len(candidate['nativeMesh']['index'])==148459*3 and len(candidate['nativeMesh']['position'])==587502*3
 chunkrefs=pins['completePairChunkRefs'];assert [Path(q['path']).name for q in chunkrefs]==[f'{i:06}.json.gz'for i in range(0,148350,128)]
 receipt_refs={(q['path'],q['sha256'])for q in read(OVERLAP/'result.json')['evidenceRefs']}
 assert len(chunkrefs)==1159 and all((q['path'],q['sha256'])in receipt_refs for q in chunkrefs)
 failure=read(CAPTURE/'real-validator-outcome.json');assert not failure['passed']and failure['actualFailure']['message']=='Native terrain contains overlapping height surfaces'
 parent_ref=pins['actualBaseParent'];check(parent_ref);assert parent_ref['path']=='3d-viewer/city/data/terrain.json'and parent_ref['sha256']=='add1264387b8db2900e9121bc29d3bd0f71a325eb200fb4ea059ab0cbee6711a'
 return pins,candidate,summary,inp,failure
def schema_only():
 pins,_,summary,_,failure=load()
 return dict(passed=True,caller=ref(Path(__file__)),runtime=ref(RUNTIME),candidateCanonicalSHA256=pins['candidateCanonicalSHA256'],
  completeCandidateFacets=148459,completeUnusedPositions=587502,completeChunks=1159,completePositiveAreaPairs=1571304,
  measuredProjectedExcessM2=summary['measurement']['nativeProjectedExcessM2'],rawValidatorFailure=failure,
  candidateOnly=True,historicalSourceContext=True,currentAcceptance=False,noMAXRayValidatorDBLease=True)
def owned():
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();last=time.monotonic()
 def pulse():
  nonlocal last
  if time.monotonic()-last>20:assert reservations.heartbeat(lease)['ok']and reservations.owns(lease);last=time.monotonic()
 pins,candidate,summary,inp,failure=load();assert lease['resources']==['immutable-source-proof:'+BATCH]
 prep=read(PROPOSAL/'actual-readonly-preparation.json');assert prep['passed']and prep['caller']==ref(Path(__file__))and prep['runtime']==ref(RUNTIME)
 validation=read(check(prep['helperValidationRef']));assert validation['passedTests']==3 and validation['failedTests']==0 and validation['exitCode']==0
 assert validation['executedCodeRefs']==[ref(HERE/'polyu_saved64_site_selection_v1_draft_20261014.py'),ref(HERE/'test_polyu_saved64_site_selection_v1_draft_20261014.py')]
 closure=read(check(prep['literalClosureRef']));assert closure['entryPath']==str(RUNTIME.relative_to(ROOT))and closure['schema']=='exact-literal-static-dynamic-resource-closure-v1'
 assert closure['computedImportsRejected']and closure['unsupportedDynamicImports']==0 and closure['completeAuditedLiteralImportClosure']
 refs=distinct_refs(pins['codeRefs']+pins['inputRefs']+prep['evidenceRefs']+validation['evidenceRefs']+[ref(PROPOSAL/'draft-pins.json'),ref(PROPOSAL/'actual-readonly-preparation.json')])
 for folder,jid in RECEIPTS:
  with connect()as db:db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',read(folder/'result.json'))
 def fence():
  for q in distinct_refs(refs):check(q);pulse()
  assert reservations.owns(lease)
 fence();DOC.mkdir();chunkrefs=pins['completePairChunkRefs']
 # Bounded saved-row selection: first/tail sixteen chunks, no all-pair scan/math.
 selected_chunks=chunkrefs[:16]+chunkrefs[-16:];sites=select((q,read(check(q)))for q in selected_chunks);pulse()
 save(DOC/'saved64-selected-sites.json.gz',sites);save(DOC/'complete-measured-pair-chunk-manifest.json',dict(receipt=ref(OVERLAP/'result.json'),completeChunkRefs=chunkrefs,completePairs=1571304,selectedChunkRefs=selected_chunks,noPairMathReplay=True))
 runtime_refs=distinct_refs([ref(CAPTURE/'private-native-terrain-candidate.json.gz'),ref(DOC/'saved64-selected-sites.json.gz')]+[dict(path=p,sha256=h)for p,h in closure['inputHashes'].items()])
 save(DOC/'input.json.gz',dict(schema='polyu-saved64-candidate-only-max-v1',candidateOnly=True,historicalSourceContext=True,currentAcceptance=False,
  candidate=ref(CAPTURE/'private-native-terrain-candidate.json.gz'),sites=ref(DOC/'saved64-selected-sites.json.gz'),runtimeInputRefs=runtime_refs,
  geometryCanonicalSHA256=pins['candidateCanonicalSHA256'],completeMeshBinding=pins['completeMeshBinding'],actualBaseParent=pins['actualBaseParent'],
  completedMeasurement=ref(OVERLAP/'complete-overlap-summary.json'),completedSourcePlanes=ref(OVERLAP/'complete-source-plane-and-face-map.json.gz'),completeMeasuredPairChunks=ref(DOC/'complete-measured-pair-chunk-manifest.json')))
 command=['node',str(RUNTIME),str(DOC.relative_to(ROOT))]
 with(DOC/'actual-saved64-runtime.log').open('xb')as log:proc=subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
 save(DOC/'actual-runtime-command.json',dict(command=command,exitCode=proc.returncode))
 outcome=dict(executed=False,runtimeExitCode=proc.returncode,rawPreviousValidatorFailure=failure,noPhysicalOrInstallationApproval=True)
 if proc.returncode==0:
  rays=read(DOC/'actual-saved64-full-candidate-native-max-ray-findings.json.gz')
  assert rays['samples']==len(rays['rows'])==64 and rays['completeCandidateFacets']==148459 and rays['completeUnusedPositionVertices']==587502 and rays['startEndAllInputsVerified']and rays['noGeometryChanges']
  refs=distinct_refs(refs+[dict(path=p,sha256=h)for p,h in rays['inputHashes'].items()]+[dict(path=p,sha256=h)for p,h in rays['completeRecursiveProductionModuleClosure']['inputHashes'].items()])
  if not rays['failedRows']and rays['maxError']<.01:
   terrain=copy.deepcopy(candidate);auditpath=DOC/'fresh-geometry-bound-mixed-source-overlap-audit.json'
   sources=distinct_refs([ref(CAPTURE/'private-native-terrain-candidate.json.gz'),inp['newNomination'],inp['previousFullNomination'],
    ref(OVERLAP/'complete-source-plane-and-face-map.json.gz'),ref(OVERLAP/'complete-overlap-summary.json'),ref(DOC/'complete-measured-pair-chunk-manifest.json'),pins['actualBaseParent']])
   for q in sources:check(q)
   save(auditpath,dict(stagedGeometrySha256=pins['candidateCanonicalSHA256'],nativeProjectedExcessM2=summary['measurement']['nativeProjectedExcessM2'],
    float32HighestRayAgreement=rays,source=dict(files=sources),policy='Fresh geometry-bound highest native surface: original recorded source planes, inherited current parents and explicitly computed own-plane enclosure/append fragments.',
    qualification='64 actual production samples only; not complete continuous MAX, untouched TIN, architecture, physical, native reacceptance or installation approval.',
    completedPairClassifications=dict(sameIdeal=1544368,differentOrNonAffine=26936),allIntroducedIntersectionsRetained=True,noOldApprovalTransferred=True,noGeometryChanges=True))
   terrain['nativeMesh']['sourceOverlap']=dict(policy='highest-native-surface',measuredProjectedExcessM2=summary['measurement']['nativeProjectedExcessM2'],evidencePath=str(auditpath.relative_to(ROOT)),evidenceSHA256=ref(auditpath)['sha256'])
   final=finalize_overlap_evidence(terrain,auditpath);assert final['stagedGeometrySha256']==pins['candidateCanonicalSHA256']
   stripped=copy.deepcopy(terrain);stripped['nativeMesh'].pop('sourceOverlap');assert stripped==candidate and canonical(stripped)==pins['candidateCanonicalSHA256']
   path=LOCAL/'private-fresh-overlap-reviewed-candidate.json';save(path,terrain);actual_failure=None
   try:module(check(failure['unchangedValidator'])).validate_patch(terrain,read(check(pins['actualBaseParent'])))
   except (AssertionError,ValueError)as e:actual_failure=dict(type=type(e).__name__,message=str(e))
   outcome=dict(executed=True,passed=actual_failure is None,actualFailure=actual_failure,unchangedValidator=failure['unchangedValidator'],actualBaseParent=pins['actualBaseParent'],
    metadataOnlyCandidate=ref(path),audit=ref(auditpath),underlyingCandidateCanonicalSHA256=canonical(stripped),allFieldsExceptSourceOverlapExactlyEqual=True,
    noToleranceChange=True,noOldApprovalTransferred=True,currentAcceptance=False,physicalAccepted=False,installationApproved=False);refs.append(ref(path))
 save(DOC/'unchanged-validator-outcome.json',outcome)
 save(DOC/'diagnostic.json',dict(runtimeExitCode=proc.returncode,validator=outcome,noConstructorPairsOrActorReplay=True,
  fourIndependentGroundGapActors=['landsd/72322:0','landsd/89540:0','landsd/258852:0','landsd/305600:0'],wholeNative59527AndOwned10536FiniteStillRequired=True,
  historicalSourceContext=True,currentAcceptance=False,physicalAccepted=False,installationApproved=False,newlyInstalled=0))
 refs=distinct_refs(refs+[ref(p)for p in DOC.rglob('*')if p.is_file()]);fence()
 result=module(FREEZER).freeze(BATCH,'saved-full-candidate64-actual-MAX-fresh-geometry-bound-metadata-validator-only',[check(q)for q in refs],
  dict(uids=[q['uid']for q in inp['complete25SourceEvidence']['rows']],sourceOnly=True,candidateOnly=True,currentAcceptance=False,physicalAccepted=False,installationApproved=False,newlyInstalled=0,runtimeExitCode=proc.returncode))
 fence();print(json.dumps(dict(jobId=result['jobId'],result=ref(DOC/'result.json'),validator=outcome)),flush=True)
def main():
 if '--schema-only'in sys.argv:print(json.dumps(schema_only(),sort_keys=True));return
 if '--owned'in sys.argv:return owned()
 assert '--check-saved64-max-and-reviewed-validator-only'in sys.argv and not DOC.exists()and not LOCAL.exists();load()
 prep=read(PROPOSAL/'actual-readonly-preparation.json');assert prep['passed']and prep['caller']==ref(Path(__file__))
 claim=reservations.claim('polyu-saved64-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  save(LEASE,json.loads(json.dumps(lease,default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
