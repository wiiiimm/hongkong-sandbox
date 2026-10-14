"""Exact old-prefix pair reuse, appended-pair delta, fresh64 and real validator."""
from pathlib import Path
from fractions import Fraction as F
import json,sys,uuid,time,subprocess,copy,collections,importlib.util,hashlib
import numpy as np
import shapely
from run import ROOT,HERE,read,save,connect,reservations
from exact_distinct_evidence_refs_v1_20261014 import distinct_refs
from polyu_compact_runtime_mesh_projection_v1_draft_20261014 import mesh_binding
from polyu_five_mask_source_plane_partition_v1_20261014 import serial
from polyu_saved64_site_selection_v1_draft_20261014 import select
from polyu_appended_pair_schedule_v1_draft_20261014 import schedule
from native_patch_resolution import finalize_overlap_evidence
from upton_actual_candidate_clearance_audit_v1_20261012 import verify_drawn_multiset
import polyu_saved_append_overlap_ancestry_v1_draft_20261014 as helper
import polyu_four_parent_current_production_caller_v3_draft_20261014 as capture
ref,check=capture.ref,capture.check
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-polyu-refined-candidate-overlap-max-v1-20261014'
DOC=BASE/BATCH;PROPOSAL=BASE/(BATCH+'-proposal');LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
OLD=BASE/'government-xl-polyu-saved-append-overlap-ancestry-v1-20261014';OLD_CAPTURE=BASE/'government-xl-polyu-append-source-region-historical-production-v1-20261014'
FEAS=BASE/'government-xl-polyu-nine-complete-parent-restoration-feasibility-v1-20261013';FIRST=BASE/'government-xl-polyu-four-compatible-parent-region-nomination-v1-20261014'
RUNTIME=HERE/'polyu_refined_candidate_actual_max_runtime_v1_draft_20261014.mjs';PREFIX=148459
OLD_JOB='ab3f9d0264fb5047ff89185cd8dc7b95eb84e29a7f44df17d8f595dd599e3ece';CAP_JOB='8957fe78a3009e63d79de2f1e4b56ee5cb440b5c03392fd14483c5edecace320'
def canonical(p):return hashlib.sha256((json.dumps(p,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode()).hexdigest()
def raw_mesh(p):return np.asarray(p['nativeMesh']['position'],dtype='<f4').astype('<f8').reshape(-1,3)[np.asarray(p['nativeMesh']['index'],dtype=np.int64).reshape(-1,3)]
def load():
 pins=read(PROPOSAL/'draft-pins.json');assert pins['caller']==ref(Path(__file__))and pins['runtime']==ref(RUNTIME)
 for q in distinct_refs(pins['codeRefs']+pins['inputRefs']):check(q)
 for folder,job in [(OLD,OLD_JOB),(capture.DOC,CAP_JOB)]:
  r=read(folder/'result.json');c=read(folder/'ROOT-VERIFIED.json');assert r['jobId']==c['jobId']==job and c['exactNeonReadback']and c['allEvidenceHashesVerified']and c['leaseReleased']
 candidate=read(capture.DOC/'private-native-terrain-candidate.json.gz');old=read(OLD_CAPTURE/'private-native-terrain-candidate.json.gz');a=candidate['nativeMesh'];b=old['nativeMesh']
 assert not a.get('sourceOverlap')and mesh_binding({k:a[k]for k in ['position','index']})==pins['completeMeshBinding']and canonical(candidate)==pins['candidateCanonicalSHA256']
 assert np.asarray(a['position'][:len(b['position'])],dtype='<f8').tobytes()==np.asarray(b['position'],dtype='<f8').tobytes()and a['index'][:PREFIX*3]==b['index']
 assert raw_mesh(candidate)[:PREFIX].tobytes()==raw_mesh(old).tobytes()
 summary=read(OLD/'complete-overlap-summary.json');assert summary['completeCandidateFacets']==PREFIX and summary['positiveAreaPairs']==1571304
 mapping=read(OLD/'complete-source-plane-and-face-map.json.gz');assert len(mapping['descriptors'])==PREFIX
 chunkrefs=pins['completeInheritedPairChunkRefs'];assert [Path(q['path']).name for q in chunkrefs]==[f'{i:06}.json.gz'for i in range(0,148350,128)]and len(chunkrefs)==1159
 receipt_refs={(q['path'],q['sha256'])for q in read(OLD/'result.json')['evidenceRefs']};assert all((q['path'],q['sha256'])in receipt_refs for q in chunkrefs)
 first=read(FIRST/'private-compatible-current-parent-append-nomination.json.gz');inp=read(capture.DOC/'input.json.gz');last=read(check(inp['newNomination']));assert first['newCompleteMeshBinding']==last['previousCompleteMeshBinding']and last['newCompleteMeshBinding']==pins['completeMeshBinding']
 assert [r['candidateFace']for r in first['appendedFaces']]==list(range(PREFIX,184833))and [r['candidateFace']for r in last['appendedFaces']]==list(range(184833,pins['completeMeshBinding']['completeIndexedFaces']))
 failure=read(capture.DOC/'real-validator-outcome.json');assert not failure['passed']and failure['actualFailure']['message']=='Native terrain contains overlapping height surfaces'
 parent=read(check(pins['actualBaseParent']));replay=read(capture.DOC/'actual-production-replay.json.gz');assert replay['startEndAllInputsVerified']and replay['currentExteriorXYZOrderedHashMatched']
 return pins,candidate,old,summary,mapping,first,last,inp,failure,parent,replay

def source_map(mapping,first,last):
 descriptors=copy.deepcopy(mapping['descriptors']);sources=copy.deepcopy(mapping['sources']);parents=read(FEAS/'complete-nine-parent-restoration-feasibility.json.gz')['complete12CapturedParentFacets'];assert len(parents)==12
 for value in sources.values():
  if value['exactOwnPlane']is not None:value['exactOwnPlane']=tuple(F(v)for v in value['exactOwnPlane'])
 def append(face,parent,pointer,kind):
  assert face==len(descriptors)and type(parent)is int and 0<=parent<12;key='parent:'+str(parent);points=parents[parent]
  if key in sources:
   assert sorted(tuple(F(x)for x in p)for p in sources[key]['completeOwnPlanePoints'])==sorted(tuple(F(x)for x in p)for p in points)
  else:sources[key]=dict(kind='captured-current-parent-plane',completeOwnPlanePoints=points,exactOwnPlane=helper.rational_plane(points),fullSourcePointer=dict(reference=ref(FEAS/'complete-nine-parent-restoration-feasibility.json.gz'),field='complete12CapturedParentFacets',parentFacet=parent),sourceIdentityVerbatim=dict(parentFacet=parent),noOriginalTINOrArchitectureClaim=True)
  descriptors.append(dict(candidateFace=face,kind=kind,sourcePlaneKey=key,fullProvenancePointer=pointer))
 first_ref=ref(FIRST/'private-compatible-current-parent-append-nomination.json.gz');last_ref=ref(capture.NOM/'private-refined-rejected-parent-nomination.json.gz')
 for i,row in enumerate(first['appendedFaces']):append(row['candidateFace'],row['parentFacet'],dict(reference=first_ref,field='appendedFaces',ordinal=i),'source-compatible-current-parent-restoration')
 for i,row in enumerate(last['appendedFaces']):
  region=row['completeSelectedRegion'];assert 0<=region<5;parent=last['completeSelectedRegions'][region]['target'][0]
  append(row['candidateFace'],parent,dict(reference=last_ref,field='appendedFaces',ordinal=i,completeSelectedRegion=region),'source-plane-refined-compatible-current-parent-restoration')
 return descriptors,sources

def schema_only():
 p,c,o,s,m,a,b,i,f,parent,r=load();d,src=source_map(m,a,b)
 return dict(passed=True,completeCandidateFacets=len(d),inheritedPrefixFacets=PREFIX,deltaFaces=len(d)-PREFIX,inheritedPositivePairs=s['positiveAreaPairs'],inheritedChunks=len(p['completeInheritedPairChunkRefs']),sourcePlaneCount=len(src),noUnionPairsMAXValidatorDBLease=True)
def module(path,name):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def owned():
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();last_pulse=time.monotonic()
 def pulse():
  nonlocal last_pulse
  if time.monotonic()-last_pulse>20:assert reservations.heartbeat(lease)['ok']and reservations.owns(lease);last_pulse=time.monotonic()
 pins,candidate,old,oldsummary,mapping,first,last,inp,failure,parent,replay=load();prep=read(PROPOSAL/'actual-readonly-preparation.json');assert prep['passed']and prep['caller']==ref(Path(__file__))and prep['runtime']==ref(RUNTIME)
 refs=distinct_refs(pins['codeRefs']+pins['inputRefs']+prep['evidenceRefs']+[ref(PROPOSAL/'draft-pins.json'),ref(PROPOSAL/'actual-readonly-preparation.json')])
 validation=read(check(prep['scheduleValidationRef']));assert validation['passedTests']==4 and validation['failedTests']==0 and validation['exitCode']==0
 assert validation['executedCodeRefs']==[ref(HERE/'polyu_appended_pair_schedule_v1_draft_20261014.py'),ref(HERE/'test_polyu_appended_pair_schedule_v1_draft_20261014.py')]
 refs=distinct_refs(refs+validation['evidenceRefs'])
 for folder,job in [(OLD,OLD_JOB),(capture.DOC,CAP_JOB)]:
  with connect()as db:db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(job,)).fetchone()==('complete',read(folder/'result.json'))
 def fence():
  for q in distinct_refs(refs):check(q);pulse()
  assert reservations.owns(lease)
 fence();DOC.mkdir();raw=raw_mesh(candidate);oldraw=raw_mesh(old);assert raw[:PREFIX].tobytes()==oldraw.tobytes()
 draw=verify_drawn_multiset(raw,np.asarray(replay['after']['closedDomainDrawnTriplets'],dtype='<f8').reshape(-1,3,3));descriptors,sources=source_map(mapping,first,last)
 assert len(descriptors)==len(raw)
 save(DOC/'complete-new-source-plane-and-face-map.json.gz',serial(dict(descriptors=descriptors,sources=sources,exactInheritedPrefix=ref(OLD/'complete-source-plane-and-face-map.json.gz'),newFirstNomination=ref(FIRST/'private-compatible-current-parent-append-nomination.json.gz'),newRefinedNomination=inp['newNomination'])))
 polygons,ids,measurement=helper.measurement(raw,inp['fullParentDomain']);old_ids=[i for i in ids if i<PREFIX];assert len(old_ids)==oldsummary['measurement']['projectedValidatorEligibleFacets']==148350
 excluded=set(oldsummary['measurement']['allOtherDrawnFaceIDs']);assert old_ids==[i for i in range(PREFIX)if i not in excluded]
 save(DOC/'complete-current-candidate-union-measurement.json',dict(**measurement,actualDrawMultiset=draw,rawValidatorFailure=failure));pulse()
 edges=helper.parent_edge_rows(candidate,parent,inp['fullParentDomain']);save(DOC/'complete-new-base-parent-edge-inventory.json.gz',edges)
 eligible=[polygons[i]for i in ids];tree=shapely.STRtree(eligible);new_ids=[i for i in ids if i>=PREFIX];counts=collections.Counter();positive=0;pair_areas=collections.defaultdict(float);plane_cache={};chunkrefs=[]
 for start in range(0,len(new_ids),128):
  query_ids=new_ids[start:start+128];left,right=tree.query([polygons[i]for i in query_ids],predicate='intersects');pairs=schedule(query_ids,ids,left,right,PREFIX);rows=[]
  for i,j in pairs:
   assert j>=PREFIX;region=polygons[i].intersection(polygons[j]);dimension='area'if region.area>0 else'line'if region.length>0 else'empty'if region.is_empty else'point';counts[dimension]+=1
   if dimension=='area':
    row=helper.pair_record(i,j,region,raw,descriptors,sources,plane_cache);row['group']='old-append'if i<PREFIX else'append-append';row['groupMeaning']='148459 immutable inherited prefix versus all new37231 fragments';positive+=1;counts['sameIdealPlane'if row['sameAuthenticatedIdealPlane']else'differentOrNonAffineIdealPlane']+=1;pair_areas[row['group']]+=region.area
   else:row=dict(leftFace=i,rightFace=j,projectedDimension=dimension,measuredLengthM=region.length,noAreaApprovalCredit=True)
   rows.append(row);pulse()
  path=DOC/'new-pair-chunks'/f'{start:06}.json.gz';save(path,dict(eligibleStart=start,eligibleEnd=min(start+128,len(new_ids)),queriedActualNewFaceIDs=query_ids,completeDeterministicIntersectingPairs=rows,everyPairWithNewRightFaceComputedOnce=True,pairwiseAreaNotUnionExcess=True));chunkrefs.append(ref(path));print(json.dumps(dict(newEligibleFacesVisited=min(start+128,len(new_ids)),totalNewEligibleFaces=len(new_ids),newPositivePairs=positive)),flush=True);pulse()
 inherited=pins['completeInheritedPairChunkRefs'];save(DOC/'complete-old-and-new-pair-evidence-manifest.json',dict(inheritedPrefixRawBytesEqual=True,inheritedPrefixRawFacetCount=PREFIX,inheritedPairSummary=ref(OLD/'complete-overlap-summary.json'),inheritedChunkRefs=inherited,newChunkRefs=chunkrefs,completePositiveAreaPairs=oldsummary['positiveAreaPairs']+positive,noOldPairMathOrApprovalTransferred=True))
 summary=dict(measurement=measurement,newPairCounts=dict(counts),newPairwiseAreaByGroup=dict(pair_areas),inheritedPairSummaryVerbatim=oldsummary,completeCandidateFacets=len(raw),completePositiveAreaPairs=oldsummary['positiveAreaPairs']+positive,newPositiveAreaPairs=positive,allDeltaPairsSourceBound=True,sampleAgreementNotContinuousMAXProof=True,noOldApprovalTransferred=True)
 save(DOC/'complete-new-overlap-summary.json',summary)
 # Existing bounded selector; no old pair replay. Read only fixed head/tail chunks.
 def selected():
  for q in chunkrefs[:8]+chunkrefs[-8:]+inherited[:8]+inherited[-8:]:yield q,read(check(q))
 sites=select(selected(),faces=len(raw));save(DOC/'saved64-new-candidate-sites.json.gz',sites)
 closure=read(check(prep['literalClosureRef']));runtime_refs=distinct_refs([ref(capture.DOC/'private-native-terrain-candidate.json.gz'),ref(DOC/'saved64-new-candidate-sites.json.gz')]+[dict(path=p,sha256=h)for p,h in closure['inputHashes'].items()])
 save(DOC/'input.json.gz',dict(schema='polyu-saved64-candidate-only-max-v1',candidateOnly=True,historicalSourceContext=True,currentAcceptance=False,candidate=ref(capture.DOC/'private-native-terrain-candidate.json.gz'),sites=ref(DOC/'saved64-new-candidate-sites.json.gz'),runtimeInputRefs=runtime_refs,completeMeshBinding=pins['completeMeshBinding'],actualCurrentCaptureContext=ref(capture.DOC/'input.json.gz'),noHistoricalManifestRestore=True))
 command=['node',str(RUNTIME),str(DOC.relative_to(ROOT))]
 with(DOC/'actual-new64-runtime.log').open('xb')as log:proc=subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
 save(DOC/'actual-runtime-command.json',dict(command=command,exitCode=proc.returncode));outcome=dict(executed=False,runtimeExitCode=proc.returncode,rawPreviousValidatorFailure=failure,noOldApprovalTransferred=True)
 if proc.returncode==0:
  rays=read(DOC/'actual-saved64-full-candidate-native-max-ray-findings.json.gz');assert rays['samples']==len(rays['rows'])==64 and rays['completeCandidateFacets']==len(raw)and rays['startEndAllInputsVerified']and rays['noGeometryChanges']
  refs=distinct_refs(refs+[dict(path=p,sha256=h)for p,h in rays['inputHashes'].items()])
  if not rays['failedRows']and rays['maxError']<.01:
   # Requires ROOT's explicit geometry/source policy review; --reviewed flag cannot bypass numerical gates.
   if '--reviewed-source-overlap-metadata'in sys.argv:
    terrain=copy.deepcopy(candidate);auditpath=DOC/'fresh-new-geometry-source-overlap-audit.json';source_refs=distinct_refs([ref(capture.DOC/'private-native-terrain-candidate.json.gz'),ref(DOC/'complete-new-source-plane-and-face-map.json.gz'),ref(DOC/'complete-new-overlap-summary.json'),ref(DOC/'complete-old-and-new-pair-evidence-manifest.json'),pins['actualBaseParent'],inp['newNomination'],last['previousNomination']])
    save(auditpath,dict(stagedGeometrySha256=pins['candidateCanonicalSHA256'],nativeProjectedExcessM2=measurement['nativeProjectedExcessM2'],float32HighestRayAgreement=rays,source=dict(files=source_refs),policy='Fresh highest native surface: preserved recorded source layers plus authenticated current-parent-plane compatible restoration and bounded own-plane refinement.',qualification='64actualproduction samples, not continuousMAX or physical/native/installapproval.',completePairEvidence=ref(DOC/'complete-old-and-new-pair-evidence-manifest.json'),noOldApprovalTransferred=True,noGeometryChanges=True))
    terrain['nativeMesh']['sourceOverlap']=dict(policy='highest-native-surface',measuredProjectedExcessM2=measurement['nativeProjectedExcessM2'],evidencePath=str(auditpath.relative_to(ROOT)),evidenceSHA256=ref(auditpath)['sha256']);finalize_overlap_evidence(terrain,auditpath);stripped=copy.deepcopy(terrain);stripped['nativeMesh'].pop('sourceOverlap');assert stripped==candidate and canonical(stripped)==pins['candidateCanonicalSHA256']
    output=LOCAL/'private-new-source-overlap-reviewed-candidate.json';save(output,terrain);actual_failure=None
    try:module(check(failure['unchangedValidator']),'polyu_new_overlap_real_validator').validate_patch(terrain,parent)
    except (AssertionError,ValueError)as e:actual_failure=dict(type=type(e).__name__,message=str(e))
    outcome=dict(executed=True,passed=actual_failure is None,actualFailure=actual_failure,metadataOnlyCandidate=ref(output),audit=ref(auditpath),allFieldsExceptSourceOverlapExactlyEqual=True,unchangedValidator=failure['unchangedValidator'],actualBaseParent=pins['actualBaseParent'],noThresholdChange=True,noOldApprovalTransferred=True,physicalAccepted=False,installationApproved=False);refs=distinct_refs(refs+[ref(output)])
   else:outcome['freshGeometryMetadataReviewPending']=True
 save(DOC/'unchanged-validator-outcome.json',outcome);refs=distinct_refs(refs+[ref(p)for p in DOC.rglob('*')if p.is_file()]);fence()
 result=module(capture.FREEZER,'polyu_new_overlap_freezer').freeze(BATCH,'byte-exact-old-prefix-pairs-plus-new-source-parent-pairs-and-fresh64-native-MAX',[check(q)for q in refs],dict(uids=[f['uid']for f in inp['exact25CurrentForms']],sourceOnly=True,candidateOnly=True,newlyInstalled=0,physicalAccepted=False,runtimeExitCode=proc.returncode));fence();print(json.dumps(dict(jobId=result['jobId'],result=ref(DOC/'result.json'),validator=outcome)),flush=True)
def main():
 if '--schema-only'in sys.argv:print(json.dumps(schema_only()));return
 if '--owned'in sys.argv:return owned()
 assert '--check-new-overlap-and64-only'in sys.argv and not DOC.exists()and not LOCAL.exists();load();assert reservations.normalise(['immutable-source-proof:'+BATCH])==['immutable-source-proof:'+BATCH]
 claim=reservations.claim('polyu-new-overlap-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  save(LEASE,json.loads(json.dumps(lease,default=str)));args=[sys.executable,__file__,'--owned']+(['--reviewed-source-overlap-metadata']if '--reviewed-source-overlap-metadata'in sys.argv else[]);subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',*args],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
