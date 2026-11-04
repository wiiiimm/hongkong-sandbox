"""UNEXECUTED actual saved64 MAX/ray + ROOT-reviewed geometry metadata replay.
No constructor, all-pairs/actor replay or source/terrain numeric edits.
"""
from pathlib import Path
import json,copy,sys,time,uuid,subprocess,ast
from run import ROOT,HERE,read,save,connect,reservations
import upton_two_original_complete_mask_current_nam_enclosure_draft_v6_20261013 as prior
from native_patch_resolution import finalize_overlap_evidence
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-upton-v6-saved64-actual-max-geometry-bound-validator-v1-20261013'
DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;PROPOSAL=BASE/(BATCH+'-proposal');LEASE=LOCAL/'reservation.json'
RUNTIME=HERE/'upton_v6_saved64_actual_max_full_ray_runtime_draft_v1_20261013.mjs';METHOD=PROPOSAL/'METHOD.md'
ANCESTOR=BASE/'government-xl-upton-v6-saved-positive-area-source-ancestor-audit-v1-20261013';V6=prior.DOC
VALIDATOR=HERE.parent/'island-detail-integration/native_terrain_validation.py';ref,check=prior.ref,prior.check
GEOMETRY='04550a2df291612b5f37c2920f7ec0077f4efd1ae9860eec96b8b0dd692291aa';EXCESS=2.2535033273961744
RECEIPTS=[(V6,'e1644ed54461d7004245bafb5efd6c9c1c270a38a704a03d9bd426a4b97ed8a8','4bcc511ea099f169402a0dd0d6e97a34705839882650dd7fc6bad17fb4898145'),(ANCESTOR,'9fa949d029e3c40b6bca3a24883b908ada421bd5fba48734eab9a8a6222805ae','95817007d1d9340d743d07d577f83e4d7aba9f1cd0cd9c7cb95a87cf596d13f7')]
def canonical(patch):return prior.digest((json.dumps(patch,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode())
def code_paths():
 roots=[HERE,HERE.parent/'shared-modelling',HERE.parent/'citywide-native',HERE.parent/'island-detail-integration',ROOT/'docs/astra-city/mui-wo-buildings/review',HERE.parent/'assembly-support-review'];todo=[Path(__file__),VALIDATOR,prior.FREEZER];seen=set()
 while todo:
  p=todo.pop().resolve()
  if p in seen:continue
  seen.add(p)
  for n in ast.walk(ast.parse(p.read_text())):
   names=[n.module]if isinstance(n,ast.ImportFrom)and n.module else[x.name for x in n.names]if isinstance(n,ast.Import)else[]
   for name in names:
    for root in roots:
     q=root/(name.replace('.','/')+'.py')
     if q.is_file():todo.append(q)
 return sorted(seen)
def schema_only():
 pins=read(PROPOSAL/'draft-pins.json');assert pins['caller']==ref(Path(__file__)) and pins['runtime']==ref(RUNTIME)
 for q in pins['codeRefs']+pins['inputRefs']:check(q)
 for folder,jid,h in RECEIPTS:assert read(folder/'result.json')['jobId']==jid and ref(folder/'result.json')['sha256']==h
 patch=read(V6/'private-native-terrain-candidate.json.gz');assert not patch['nativeMesh'].get('sourceOverlap') and canonical(patch)==GEOMETRY
 overlap=read(V6/'new-geometry-measured-overlap-and-exact-height-attribution.json.gz');m=overlap['measured'];assert m['candidateGeometryCanonicalSHA256']==GEOMETRY and m['nativeProjectedExcessM2']==EXCESS and m['completeCandidateFaces']==11575
 assert m['float32HighestRayAgreement']['samples']==len(m['float32HighestRayAgreement']['rows'])==64
 cls=read(ANCESTOR/'complete-2128-saved-area-pair-source-ancestor-classification.json.gz');assert cls['completeSavedPositiveAreaPairs']==len(cls['rows'])==2128 and cls['allRowsExactlyPreserved']and cls['noApprovalWritten']
 assert all(q['fullSavedCandidatePairProof']==p for q,p in zip(cls['rows'],[p for p in overlap['exactMeasuredPairNominations']if p['proof']['exactProjectedDimension']=='area']))
 assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==prior.CURRENT
 return dict(passed=True,caller=ref(Path(__file__)),runtime=ref(RUNTIME),geometryCanonicalSHA256=GEOMETRY,measuredProjectedExcessM2=EXCESS,completeSavedAreaRows=2128,actualProductionSampleSites=64,noDBLeaseMAXRayValidatorOrApproval=True)
def owned():
 lease=read(LEASE);assert reservations.owns(lease) and not DOC.exists();last=time.monotonic()
 def pulse(force=False):
  nonlocal last
  if force or time.monotonic()-last>20:assert reservations.heartbeat(lease)['ok']and reservations.owns(lease);last=time.monotonic()
 schema_only();prep=read(PROPOSAL/'schema-preflight.json');assert prep['passed']and prep['caller']==ref(Path(__file__))
 closure=read(PROPOSAL/'literal-runtime-closure-preflight.json');assert closure['schema']=='exact-literal-static-dynamic-resource-closure-v1'and closure['computedImportsRejected']and closure['unsupportedDynamicImports']==0 and closure['entryPath']==str(RUNTIME.relative_to(ROOT))
 pins=read(PROPOSAL/'draft-pins.json');refs=[ref(p)for p in code_paths()]+pins['codeRefs']+pins['inputRefs']+[ref(RUNTIME),ref(METHOD),ref(PROPOSAL/'draft-pins.json'),ref(PROPOSAL/'schema-preflight.json'),ref(PROPOSAL/'literal-runtime-closure-preflight.json')]
 refs +=[dict(path=p,sha256=h)for p,h in closure['inputHashes'].items()]
 for folder,jid,h in RECEIPTS:
  r=read(folder/'result.json')
  with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',r)
  for q in r['evidenceRefs']+[ref(folder/'result.json')]:check(q);refs.append(q);pulse()
 def fence():
  for q in refs:check(q);pulse()
  assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==prior.CURRENT;pulse(True)
 fence();DOC.mkdir(parents=True);candidate=V6/'private-native-terrain-candidate.json.gz';measure=V6/'new-geometry-measured-overlap-and-exact-height-attribution.json.gz'
 save(DOC/'input.json.gz',dict(currentManifest=ref(ROOT/'3d-viewer/city/data/manifest.json'),candidate=ref(candidate),measuredOverlap=ref(measure),geometryCanonicalSHA256=GEOMETRY,runtimeInputRefs=pins['inputRefs']+[dict(path=p,sha256=h)for p,h in closure['inputHashes'].items()]))
 log=DOC/'actual-saved64-runtime.log'
 with log.open('wb')as out:subprocess.run(['node',str(RUNTIME),str(DOC.relative_to(ROOT))],cwd=ROOT,stdout=out,stderr=subprocess.STDOUT,check=True)
 rays=read(DOC/'actual-saved64-full-candidate-native-max-ray-findings.json.gz');assert rays['samples']==len(rays['rows'])==64 and rays['completeCandidateFacets']==11575 and rays['startEndAllInputsVerified']and rays['noGeometryChanges']
 for path,h in rays['inputHashes'].items():refs.append(dict(path=path,sha256=h))
 for path,h in rays['completeRecursiveProductionModuleClosure']['inputHashes'].items():refs.append(dict(path=path,sha256=h))
 original=read(candidate);assert canonical(original)==GEOMETRY;outcome=dict(executed=False,reason='Actual saved-site MAX/ray disagreement',priorRawFailure=ref(V6/'real-validator-outcome.json'),actualBaseParent=ref(ROOT/'3d-viewer/city/data/terrain.json'),noPhysicalOrInstallationApproval=True)
 if not rays['failedRows']and rays['maxError']<.01:
  nom=read(V6/'complete-nominations-before-guards.json.gz');terrain=copy.deepcopy(original)
  sources=[ref(candidate),ref(V6/'complete-nominations-before-guards.json.gz'),nom['allSourceOriginalTriplets'],nom['allCurrentTriplets'],ref(measure),ref(ANCESTOR/'complete-2128-saved-area-pair-source-ancestor-classification.json.gz'),ref(ROOT/'3d-viewer/city/data/terrain.json'),ref(ROOT/'3d-viewer/city/data/government-native-79882-0.json')]
  for q in sources:check(q)
  audit=dict(stagedGeometrySha256=GEOMETRY,nativeProjectedExcessM2=EXCESS,float32HighestRayAgreement=rays,source=dict(files=sources),policy='Exact ROOT-reviewed mixed original-TIN/current terrain nomination; highest native surface, with all packed and newly mixed intersections explicit.',qualification='Geometry-bound metadata only, not untouched source-TIN, complete continuous MAX, source role, physical or installation approval.',complete2128SourceAncestorClassification=ref(ANCESTOR/'complete-2128-saved-area-pair-source-ancestor-classification.json.gz'),all124IntroducedMixedPairsRetained=True,all1868Contained43Expanded28SameAncestor65NewPackedPairsRetained=True,idealHeightsAreNotBitwiseJSEquality=True,savedRetained79882GridComparisonNotActualBaseParentSeamProof=True,sourceGeometryOrPoseChanges=0,noHistoricalApprovalTransferred=True)
  auditpath=DOC/'geometry-bound-mixed-source-overlap-audit.json';save(auditpath,audit)
  terrain['nativeMesh']['sourceOverlap']=dict(policy='highest-native-surface',measuredProjectedExcessM2=EXCESS,evidencePath=str(auditpath.relative_to(ROOT)),evidenceSHA256=ref(auditpath)['sha256'])
  final=finalize_overlap_evidence(terrain,auditpath);assert final['stagedGeometrySha256']==GEOMETRY
  without=copy.deepcopy(terrain);without['nativeMesh'].pop('sourceOverlap');assert without==original and canonical(without)==GEOMETRY
  path=LOCAL/'private-upton-v6-geometry-bound-overlap-reviewed.json';save(path,terrain);assert read(path)==terrain
  failure=None
  try:prior.load_module(VALIDATOR,'upton_v6_same_native_validator').validate_native_mesh(terrain,read(ROOT/'3d-viewer/city/data/terrain.json'))
  except AssertionError as e:failure=str(e)
  outcome=dict(executed=True,passed=failure is None,actualAssertion=failure,unchangedValidator=ref(VALIDATOR),actualBaseParent=ref(ROOT/'3d-viewer/city/data/terrain.json'),priorRawFailure=ref(V6/'real-validator-outcome.json'),metadataOnlyCandidate=ref(path),audit=ref(auditpath),allFieldsExceptSourceOverlapExactlyEqual=True,noToleranceOrSamplerChanges=True,noPhysicalOrInstallationApproval=True);refs.append(ref(path))
 save(DOC/'unchanged-base-parent-validator-outcome.json',outcome)
 save(DOC/'diagnostic.json.gz',dict(candidate=ref(candidate),actualSaved64MaxRay=ref(DOC/'actual-saved64-full-candidate-native-max-ray-findings.json.gz'),validator=outcome,completeCandidateCanonicalSHA256=GEOMETRY,measuredProjectedExcessM2=EXCESS,noConstructorPairOrActorReplay=True,samplesNotWholeSurfaceProof=True,allCandidateWholeActorAndForeignGatesRemain=True,physicalAccepted=False,installationApproved=False,newlyInstalled=0))
 refs +=[ref(p)for p in DOC.iterdir()if p.is_file()];fence()
 prior.load_module(prior.FREEZER,'upton_v6_max_overlap_freezer').freeze(BATCH,'private-saved64-production-MAX-geometry-bound-metadata-validator-diagnostic',[check(q)for q in{(q['path'],q['sha256']):q for q in refs}.values()],dict(uids=prior.UIDS+[prior.NATIVE],sourceOnly=True,candidateOnly=True,geometryChanges=0,validatorOutcome=outcome,physicalAccepted=False,newlyInstalled=0,currentManifest=ref(ROOT/'3d-viewer/city/data/manifest.json')))
def main():
 if '--schema-only'in sys.argv:print(json.dumps(schema_only(),sort_keys=True));return
 if '--owned'in sys.argv:return owned()
 assert '--check-saved64-max-and-reviewed-validator-only'in sys.argv and not DOC.exists()and not LOCAL.exists()
 uids=prior.UIDS+[prior.SECONDARY,prior.NATIVE,prior.FOREIGN];resources=['building:'+u for u in uids]+['terrain-patch:'+u for u in uids]+['immutable-source-proof:'+BATCH]
 claim=reservations.claim('upton-v6-max-metadata-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'];save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
 subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
