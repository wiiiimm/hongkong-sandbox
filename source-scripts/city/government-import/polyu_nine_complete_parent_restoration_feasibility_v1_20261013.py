"""Full nine masks/current-parent feasibility; no restored terrain or model edits."""
from pathlib import Path
from fractions import Fraction as F
import json,sys,subprocess,time,uuid
import numpy as np
import polyu_nine_basic_saved_height_leased_wrapper_v1_20261013 as prior
from polyu_nine_basic_saved_height_context_draft_v1_20261013 import decode_complete_basic
from upton_six_basic_preserved_ground_feasibility_v1_20261012 import polygon_masks,projected_mask,area,masked_current_pair
from exact_original_projection_coverage_v2_20261010 import exact_coverage
from run import ROOT,HERE,read,save,connect,reservations
ref,check=prior.ref,prior.check
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-polyu-nine-complete-parent-restoration-feasibility-v1-20261013'
DOC=BASE/BATCH;PROPOSAL=BASE/(BATCH+'-proposal');LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
CONTEXT=prior.DOC;JOB='87d44b339171b02f93f3c228b4ec29b824f1b40553a948e2e91f36f1cc166f46'
SOURCE_CONTEXT=prior.SOURCE_CONTEXT;FREEZER=prior.FREEZER
TEST='test_upton_six_basic_preserved_ground_feasibility_v1_20261012'
sha=lambda a:prior.digest(np.asarray(a,dtype='<f8').tobytes())

def load():
 pins=read(PROPOSAL/'draft-pins.json');assert pins['caller']==ref(Path(__file__))
 for q in pins['codeRefs']+pins['inputRefs']:check(q)
 producer=prior.module('immutable_polyu_saved_context_input_only',prior.PRODUCER)
 hashes,a,patch,nine,failed,probes,parents=producer.preflight()
 assert len(hashes)==8830 and len(nine)==9 and len(parents)==12 and len(probes)==6701
 receipt=read(CONTEXT/'result.json');assert receipt['jobId']==JOB and len(receipt['evidenceRefs'])==8847
 context=read(CONTEXT/'context.json.gz');assert len(context['allClosedSavedProbeContexts'])==1041 and context['fullNineRawGuardFailuresVerbatim']==failed and context['inputHashes']==hashes
 assert context['allNineWholeActualBasicBuffersAndIndexEvidenceVerbatim']==nine and context['saved6701ProbesAreNotOriginalGuardSampleSet']and context['noRestorationMaskOrFullDomainHeightProof']and context['native59527BeforeAfterStillPending']
 assert sum(r['checks']for r in failed)==3366 and all(r['reasons']==['increased-neighbour-ground-gap']for r in failed)
 account=a['account'];full=account['all25CompleteProductionBasicAndExplicitNativeInputsVerbatim'];assert [r['uid']for r in full['rows']]==prior.UIDS and full['completeScannedForms']==25
 assert all(len(r['currentForm']['rings'])==1 for r in nine)
 assert context['allOriginal752FailuresAndWholeSourceRolesRemain']==account['all752FourModeRawNegativesAnd21BodiesVerbatim']and all(len(r['all752FailureRecordsVerbatim'])==752 for r in context['allOriginal752FailuresAndWholeSourceRolesRemain'])
 source=read(SOURCE_CONTEXT);assert source['sourceSHA256']==prior.SOURCE and len(source['completeOriginalTopologyVerbatim']['sharedEdgeConnectedComponents'])==21
 for mode,stream in source['completeWorldStreams'].items():
  raw=np.asarray(stream['completeWorldTriangles'],dtype='<f8');assert raw.shape==(10536,3,3)and np.isfinite(raw).all()and sha(raw)==stream['completeWorldTriangleSHA256']
 assert len(source['completeWorldStreams'])==4 and not source['currentAcceptance']and not source['physicalAccepted']
 assert not context['currentAcceptance']and not context['physicalAccepted']
 assert sum(r['completeIndexedFaces']for r in account['installedPodiumFalseHoldVerbatim']['actualPositionRecord']['actualRenderMeshes'])==59527 and account['installedPodiumFalseHoldVerbatim']['publicationHoldPreserved']
 assert account['fullOwnedFourStreamAndWholeAffectedActorsPending']and account['sourceBuildingPoseAndGeometryUnchanged']
 resources=sorted(['building:'+u for u in prior.UIDS]+['terrain-patch:'+u for u in prior.UIDS]+['immutable-source-proof:'+BATCH]);assert len(resources)==51
 assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==producer.CURRENT
 return pins,producer,hashes,source,nine,parents,context,account,resources

def schema_only():
 p,producer,h,s,nine,parents,c,a,resources=load()
 return dict(passed=True,caller=ref(Path(__file__)),completedContextJob=JOB,fullOriginalInputPins=len(h),completeAffectedActors=25,canonicalResources=resources,nineMaskActors=9,fullBASICProjectionFacesPerMode=sum(r['completeIndexedFaces']for r in nine),completeSportsSourceFacesPerMode=10536,sourceWorldModes=4,sourceBodies=21,negativesPerMode=752,completeParentFacets=12,savedContextRecords=1041,originalGuardSiteCount=3366,originalGuardSitesNotPersisted=True,native59527BeforeAfterPending=True,noMaskProjectionOrFiniteCalculationDBLeaseWorker=True)

def owned():
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists()
 pins,producer,hashes,source,nine,parents,context,account,resources=load();assert lease['resources']==resources
 prep=read(PROPOSAL/'actual-readonly-preparation.json');assert prep['passed']and prep['caller']==ref(Path(__file__))
 refs=pins['codeRefs']+pins['inputRefs']+[ref(PROPOSAL/'draft-pins.json'),ref(PROPOSAL/'METHOD.md'),ref(PROPOSAL/'actual-readonly-preparation.json')]+prep['evidenceRefs']+[dict(path=k,sha256=v)for k,v in hashes.items()]
 receipt=read(CONTEXT/'result.json')
 with connect()as db:db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(JOB,)).fetchone()==('complete',receipt)
 refs+=[ref(CONTEXT/'result.json')]+receipt['evidenceRefs'];last=time.monotonic()
 def pulse(force=False):
  nonlocal last
  if force or time.monotonic()-last>20:assert reservations.heartbeat(lease)['ok']and reservations.owns(lease);last=time.monotonic()
 def fence():
  for q in refs:check(q);pulse()
  assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==producer.CURRENT and reservations.owns(lease)
 fence();DOC.mkdir(parents=True);parent=np.asarray(parents,dtype='<f8');assert parent.shape==(12,3,3)and np.isfinite(parent).all()
 body={f:i for i,component in enumerate(source['completeOriginalTopologyVerbatim']['sharedEdgeConnectedComponents'])for f in component};zeros=source['completeOriginalTopologyVerbatim']['exactNonrenderingOriginalFaces'];results=[]
 for actor in nine:
  uid=actor['uid'];masks=[];decoded=decode_complete_basic(actor)
  for part,mask in enumerate(polygon_masks(actor['currentForm']['rings'][0])):masks.append(dict(kind='exact-current-form-ring-ear',part=part,exactClosedProjection=mask))
  for mode,geometry in decoded.items():
   assert len(geometry['triangles'])==actor['completeIndexedFaces']and len(geometry['completeUnusedPositions'])==actor['completePositionVertices']
   for face,t in enumerate(geometry['triangles']):masks.append(dict(kind='complete-BASIC-projected-facet',arithmetic=mode,actualBasicFace=face,wholeWorldTripletSHA256=sha(t),exactClosedProjection=projected_mask(t)))
   pulse()
  positive=[i for i,r in enumerate(masks)if area(r['exactClosedProjection'])!=0];degenerate=[i for i in range(len(masks))if i not in positive]
  grounds=np.asarray([[[float(x),0.,float(z)]for x,z in masks[i]['exactClosedProjection']]for i in positive],dtype='<f8')
  missing=[]
  for i in degenerate:
   dummy=[[float(x),0.,float(z)]for x,z in masks[i]['exactClosedProjection']];proof=exact_coverage(dummy,grounds)
   masks[i]['completePositiveMaskUnionCoverage']=proof
   if not proof['exactProjectionCovered']:missing.append(i)
   pulse()
  mask_arr=np.asarray([[[float(x),float(z)]for x,z in masks[i]['exactClosedProjection']]for i in positive],dtype='<f8');lo=mask_arr.min(1);hi=mask_arr.max(1)
  maskpath=DOC/'masks'/(uid.replace('/','-').replace(':','-')+'.json.gz');save(maskpath,dict(uid=uid,currentFormVerbatim=actor['currentForm'],wholeBASICSourceVerbatim=actor,rows=[{**r,'mask':i,'exactClosedProjection':[[str(x),str(z)]for x,z in r['exactClosedProjection']]}for i,r in enumerate(masks)],positiveMaskIDs=positive,degenerateMaskIDs=degenerate,degenerateProjectionsNotCoveredByPositiveUnion=missing,completeUnusedPositionsRetainedInSourceEvidence=True,completeClosedUnionNoSampleOrBBoxMask=True));maskref=ref(maskpath)
  worlds=[];conflicting=set()
  for mode,stream in source['completeWorldStreams'].items():
   world=np.asarray(stream['completeWorldTriangles'],dtype='<f8');chunks=[];rows=[];conflicts=[];uncredited=[]
   for face_id,face in enumerate(world):
    xz=face[:,[0,2]];selected=np.flatnonzero(np.all(hi>=xz.min(0),axis=1)&np.all(lo<=xz.max(0),axis=1));pairs=[]
    for pid,ground in enumerate(parent):
     gxz=ground[:,[0,2]]
     # Closed extrema prune only strictly disjoint pairs, never masks themselves.
     if np.any(gxz.max(0)<xz.min(0))or np.any(gxz.min(0)>xz.max(0)):continue
     mids=[int(k)for k in selected if np.all(hi[k]>=gxz.min(0))and np.all(lo[k]<=gxz.max(0))]
     for local in mids:
      mi=positive[local];proof=masked_current_pair(face,ground,masks[mi]['exactClosedProjection'])
      if proof.get('closedMaskedProjectionDisjoint'):continue
      pairs.append(dict(parentFacet=pid,mask=mi,maskEvidence=maskref,unchangedMaskedCurrentPairProof=proof))
      if proof.get('violatesExistingOrdinaryBound'):conflicts.append(face_id);conflicting.add(face_id)
      if proof.get('exactSourceZero')or proof.get('collapsedCurrentGroundProjection'):uncredited.append(face_id)
      pulse()
    rows.append(dict(sourceFace=face_id,originalBody=body.get(face_id),wholeSourceFaceSHA256=sha(face),completeClosedAABBMaskCandidates=[positive[int(k)]for k in selected],allOtherMasksStrictlyClosedAABBDisjoint=True,allIntersectingRetainedParentMaskPairs=pairs,all752OriginalNegativesAnd21BodiesStillHeld=True,noRootRoleOrSourceAcceptance=True))
    if len(rows)==64 or face_id==len(world)-1:
     path=DOC/'chunks'/uid.replace('/','-').replace(':','-')/mode/(str(len(chunks)).zfill(5)+'.json.gz');assert not path.exists();save(path,dict(uid=uid,sourceArithmetic=mode,completeSourceWorldSHA256=sha(world),completeParentSHA256=sha(parent),rows=rows));chunks.append(ref(path));rows=[];pulse(True)
   worlds.append(dict(arithmetic=mode,completeSourceFaces=10536,wholeSourceWorldSHA256=sha(world),chunks=chunks,conflictingSourceFaces=sorted(set(conflicts)),uncreditedSourceOrParentDegeneracies=sorted(set(uncredited)),allSourceFacesAccounted=True));print(json.dumps(dict(uid=uid,mode=mode,completeSourceFaces=10536,conflicts=len(set(conflicts)),noAcceptance=True)),flush=True)
  results.append(dict(uid=uid,completeMask=maskref,sourceWorlds=worlds,allConflictingSourceFaces=sorted(conflicting),unresolvedDegenerateMaskIDs=missing,eligibleCurrentParentMaskNominationOnly=not conflicting and not missing,authenticNeighbourOriginalAcquisitionCandidate=bool(conflicting),currentFormAndExactUID=actor['currentForm'],noSourceCorruptionOrPermanentRejectionCredit=True,noTerrainRestored=True))
 save(DOC/'complete-nine-parent-restoration-feasibility.json.gz',dict(rows=results,all25AffectedActors=prior.UIDS,all51CanonicalResources=resources,completedSavedContext=ref(CONTEXT/'context.json.gz'),all752FourModeNegativesAndWhole21SourceRolesRetained=context['allOriginal752FailuresAndWholeSourceRolesRemain'],exactSourceContext=ref(SOURCE_CONTEXT),allOriginalSourceZerosVerbatim=zeros,retainedNative59527FullBeforeAfterStillPending=True,original3366GuardSitesNotPersisted=True,noSavedContextToOriginalGuardSiteEquivalence=True,eligibleMasksNeedFullDomainPackingCoverageSeamFiniteMAXRuntimeProof=True,complete12CapturedParentFacets=parents,noTerrainOrModelPoseGeometryChanges=True,currentAcceptance=False,physicalAccepted=False,newlyInstalled=0))
 refs+=[ref(p)for p in DOC.rglob('*')if p.is_file()];fence()
 prior.module('polyu_complete_mask_feasibility_freezer',FREEZER).freeze(BATCH,'complete-nine-current-parent-mask-source-clearance-feasibility-only',[check(q)for q in{(q['path'],q['sha256']):q for q in refs}.values()],dict(uids=prior.UIDS,sourceOnly=True,terrainRestored=False,currentAcceptance=False,physicalAccepted=False,newlyInstalled=0))

def main():
 if '--schema-only'in sys.argv:print(json.dumps(schema_only(),sort_keys=True));return
 if '--owned'in sys.argv:return owned()
 assert '--test-complete-nine-current-parent-masks-only'in sys.argv and not DOC.exists()and not LOCAL.exists()
 pins,producer,hashes,source,nine,parents,context,account,resources=load();prep=read(PROPOSAL/'actual-readonly-preparation.json');assert prep['passed']and prep['caller']==ref(Path(__file__))
 claim=reservations.claim('polyu-nine-complete-parent-feasibility-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  save(LEASE,json.loads(json.dumps(lease,default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
