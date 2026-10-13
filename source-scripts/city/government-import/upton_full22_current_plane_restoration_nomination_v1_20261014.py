"""ROOT-only append-only exact saved full22 current-plane terrain nomination.

Completed ideal feasibility supplies exact polygons, not packed acceptance.
No new source clipping/search or building geometry. All old raw/index data stays.
"""
from pathlib import Path
import json,sys,time,uuid,subprocess
import numpy as np
import upton_full22_original_current_restoration_feasibility_v1_20261014 as feasibility
from polyu_five_mask_source_plane_partition_v1_20261014 import packed_pieces,points,serial
from upton_append_current_plane_nomination_binding_v1_20261014 import append_bound_pieces,digest
from run import ROOT,HERE,read,save,connect,reservations
baseline=feasibility.baseline;capture=feasibility.finite.capture
ref,check=feasibility.ref,feasibility.check
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-upton-full22-current-plane-restoration-nomination-v1-20261014'
DOC=BASE/BATCH;PROPOSAL=BASE/(BATCH+'-proposal');LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
JOB='276fd5d4a8ef8367b99b0e5e1597ea7801dc6bbce9600f48cdad998eae63065e'
RECEIPTS=[(feasibility.DOC,JOB),(capture.DOC,'e75d2f586b7a86fa6b4094fbfb53d70951b45c3f9420bcad0abd228b7111bbd2'),(capture.NOM_DOC,'85fed77eb03056242d5211b1a2c255e36e41b8fceb7de56a8cbb25b252a211aa')]
TEST='test_upton_append_current_plane_nomination_binding_v1_20261014'

def load():
 pins=read(PROPOSAL/'draft-pins.json');assert pins['caller']==ref(Path(__file__))
 for q in pins['codeRefs']+pins['inputRefs']:check(q)
 for folder,job in RECEIPTS:assert read(folder/'result.json')['jobId']==job
 verified=read(feasibility.DOC/'ROOT-VERIFIED.json');assert verified['jobId']==JOB and verified['exactNeonReadback'] and verified['allEvidenceHashesVerified'] and verified['leaseReleased']
 _,saved,original,latest,scope,current,attribution,representation=feasibility.load()
 whole=read(feasibility.DOC/'complete-full22-original-current-restoration-feasibility.json.gz')
 assert whole['wholeCurrentMaskOrdinaryCompatibilityWithoutUncredited'] and whole['allWholeClosedResidualsCoveredByAuthenticCurrent'] and whole['all52AffectedWholeBasicStreamsRetained'] and whole['allZero23CrossingRootSupportForeignObligationsRetained']
 assert not whole['physicalAccepted'] and not whole['installationApproved'] and whole['latestFullFiniteNegativesVerbatim']==latest
 assert len(whole['complete1911BasicRows'])==1911 and len(whole['actors'])==4
 for a in whole['actors']:
  assert len(a['worlds'])==4
  for w in a['worlds']:assert not w['conflictingCurrentMaskSourceFaces'] and not w['uncreditedCurrentMaskSourceFaces'] and w['allSourceFacesAccounted']
 affected=[r for r in whole['complete1911BasicRows']if 'wholeCurrentMaskFeasibility'in r];assert len(affected)==52
 for r in affected:assert not r['wholeCurrentMaskFeasibility']['conflictingCurrentMaskSourceFaces'] and not r['wholeCurrentMaskFeasibility']['uncreditedCurrentMaskSourceFaces']
 coverage=read(check(whole['whole22PolygonCoverage']));assert len(coverage['rows'])==22 and coverage['all80ClosedBoundariesChecked'] and coverage['source122721InventoryUnchanged']
 assert all(r['wholeCurrentCoverage']['wholeClosedResidualCovered']for r in coverage['rows'])
 planes=coverage['completeCurrentCounterpartPlanes'];assert len(planes)==4 and len({p['originalCurrentFace']for p in planes})==4
 for p in planes:
  i=p['originalCurrentFace'];assert digest(p['wholeOriginalCurrentTriplet'])==digest(current[i])==p['wholeOriginalCurrentTripletSHA256']
  assert p['completeCurrentAttribution']==attribution[i] and p['noOtherLayerYOrSourceGeometryChange']
  part=p['completeOwnCurrentPlaneMaskPartition'];assert part['inside'] and part['completeOwnPlanePartition'] and part['maskFirstOwnershipPreventsDuplicateArea'] and part['closedBoundariesRetained'] and part['noGEOSToleranceOrBuffer']
  for row in part['inside']:
   assert type(row['mask'])is int and len(row['polygon'])>=3
   assert all(len(v)==3 for v in row['polygon']);points(row['polygon']) # parse rational schema only
 nom=read(capture.NOM_DOC/'private-own-layer-projected-edge-subdivision-nomination.json.gz');raw=np.asarray(nom['candidateRawPositionTriplets'],dtype='<f8');pv=nom['candidateFaceProvenance']
 assert raw.shape==(11580,3,3) and len(pv)==11580 and len(nom['protectedWholeCurrentTripletsUnchanged'])==68
 patch=read(capture.DOC/'private-native-terrain-candidate.json.gz');mesh=patch['nativeMesh']
 pos=np.asarray(mesh['position'],dtype='<f8').reshape(-1,3);idx=np.asarray(mesh['index'],dtype=np.int64).reshape(-1,3)
 assert idx.shape==(11580,3) and pos[idx].tobytes()==raw.astype('<f4').astype('<f8').tobytes()
 for r in nom['protectedWholeCurrentTripletsUnchanged']:assert digest(raw[r['newCandidate']])==r['rawTripletSHA256']
 assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==baseline.CURRENT
 return pins,whole,coverage,nom,raw,pv,patch,representation

def schema_only():
 pins,whole,cov,nom,raw,pv,patch,rep=load()
 return dict(passed=True,caller=ref(Path(__file__)),wholeResidualPolygons=22,closedBoundaryEdges=80,authenticatedCurrentCounterpartPlanes=4,savedInsideOwnPlanePolygons=sum(len(p['completeOwnCurrentPlaneMaskPartition']['inside'])for p in cov['completeCurrentCounterpartPlanes']),oldCandidateFacets=11580,protectedLiteralFacets=68,fullCurrentFacets=9214,originalTINFacets=122721,completeActorScope=6650,completeBasicRecords=1911,wholeAffectedBasicActors=52,wholeOwnedFacesPerMode=13312,secondary392Native616AllFourModes=True,allPriorNegativesRetained=True,noPackingClippingSourceCalculationDBLeaseOrWorker=True)

def owned():
 lease=read(LEASE);assert reservations.owns(lease) and not DOC.exists();last=time.monotonic()
 def pulse():
  nonlocal last
  if time.monotonic()-last>20:assert reservations.heartbeat(lease)['ok'] and reservations.owns(lease);last=time.monotonic()
 pins,whole,coverage,nom,raw,pv,patch,rep=load();prep=read(PROPOSAL/'actual-readonly-preparation.json');assert prep['passed'] and prep['caller']==ref(Path(__file__))
 refs=pins['codeRefs']+pins['inputRefs']+[ref(PROPOSAL/'draft-pins.json'),ref(PROPOSAL/'METHOD.md'),ref(PROPOSAL/'actual-readonly-preparation.json')]+prep['evidenceRefs']
 for folder,job in RECEIPTS:
  receipt=read(folder/'result.json')
  with connect()as db:db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(job,)).fetchone()==('complete',receipt)
  refs+=[ref(folder/'result.json')]+receipt['evidenceRefs']
 refs=list({(q['path'],q['sha256']):q for q in refs}.values())
 def fence():
  for q in refs:check(q);pulse()
  assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==baseline.CURRENT and reservations.owns(lease)
 fence();DOC.mkdir();additions=[];parent_map=[];packing=[]
 for parent in coverage['completeCurrentCounterpartPlanes']:
  ids=[];rows=[]
  for ordinal,saved in enumerate(parent['completeOwnCurrentPlaneMaskPartition']['inside']):
   # Exact Fraction input is mandatory; never float('numerator/denominator').
   pieces=packed_pieces([points(saved['polygon'])],parent['wholeOriginalCurrentTriplet'])
   for part,piece in enumerate(pieces):
    j=11580+len(additions);ids.append(j)
    provenance=dict(candidateFace=j,kind='capturedCurrentRing',originalFace=parent['originalCurrentFace'],completeCurrentSourceAttribution=parent['completeCurrentAttribution'],computedFragment=True,savedInputByteExact=False,region='exact-saved-full22-residual-current-restoration',rawNominationFaceSHA256=digest(piece['packedPieceTriplet']),exactOriginalPlanePoints=serial(piece['exactOwnPlanePoints']),currentRestoration=dict(completedFeasibilityJob=JOB,ownPlaneInsidePolygonOrdinal=ordinal,savedCompiledMaskOrdinal=saved['mask'],fanPart=part,exactSavedInsidePolygonVerbatim=saved,originalCurrentTripletSHA256=parent['wholeOriginalCurrentTripletSHA256'],noOtherLayerYUsed=True))
    additions.append(dict(packedPieceTriplet=piece['packedPieceTriplet'],provenance=provenance));rows.append(dict(newCandidateFace=j,packingProof=serial(piece)))
   pulse()
  parent_map.append(dict(originalCurrentFace=parent['originalCurrentFace'],addedCandidateFaces=ids,completeCurrentCounterpartVerbatim=parent));packing.extend(rows)
 assert additions
 bound=append_bound_pieces(raw,pv,patch['nativeMesh'],additions,nom['protectedWholeCurrentTripletsUnchanged'],nom['completeOldNewIndexMapping'])
 # Old source metadata is historical, not an approval of this new geometry.
 bound['historicalPreviousNativeMeshSourceVerbatim']=bound['newNativeMesh'].get('source')
 bound['newNativeMesh']['source']=dict(kind='private-full22-authentic-current-plane-restoration',completedFeasibilityJob=JOB,originalCandidate=ref(capture.DOC/'private-native-terrain-candidate.json.gz'),physicalAccepted=False)
 output=dict(schema='upton-full22-current-plane-restoration-nomination-v1',**bound,previousOwnLayerNomination=ref(capture.NOM_DOC/'private-own-layer-projected-edge-subdivision-nomination.json.gz'),previousActualCaptureCandidate=ref(capture.DOC/'private-native-terrain-candidate.json.gz'),wholeCurrentRestorationFeasibility=ref(feasibility.DOC/'complete-full22-original-current-restoration-feasibility.json.gz'),whole22GapCoverage=ref(feasibility.DOC/'complete22-whole-gap-current-counterpart-plane-coverage.json.gz'),completeRestoredCurrentCounterpartMapping=parent_map,allOldNominationProofsCountsAndAliasMappingsHistoricalOnly=True,all11580ExistingFacetsPreserved=True,all68ProtectedLiteralTripletsUnchanged=True,all122721SourceAnd9214CurrentInputInventoriesRetainedViaPreviousNomination=True,allPriorFiniteAndFullScopeNegativesVerbatim=whole['latestFullFiniteNegativesVerbatim'],allFourActorFourWorldAnd1911Basic52WholeAffectedObligationsRetained=True,allZeros23CrossingsRootSupportForeignObligationsRetained=True,fullParentCells=[457,449,460,451],fullParentDomain=[-2477.5,-37.5,-2267.5,102.5],freshPackedCoverageFiniteOverlapMAXSeamRuntimeBrowserRequired=True,noOverlapApprovalTransferred=True,originalBuildingGeometryPoseChanges=0,physicalAccepted=False,installationApproved=False,newlyInstalled=0)
 candidate=np.asarray(output['candidateRawPositionTriplets'],dtype='<f8');output['completeNewCandidateFacets']=len(candidate);output['completeNewRawCandidateSHA256']=digest(candidate)
 save(DOC/'private-full22-current-plane-restoration-nomination.json.gz',serial(output))
 save(DOC/'complete-added-current-plane-packing-diagnostic.json.gz',serial(dict(rows=packing,oldFacets=11580,newFacets=len(candidate),newRawSHA256=digest(candidate),fullIdealCoverageAlreadyCompletedNotNewPackingProof=True,packingResidualsMeasuredNotWaived=True,noDetExcludedFacetOrPackedCoverageAcceptance=True,notTerrainAcceptance=True)))
 fence();outputs=[ref(p)for p in DOC.iterdir()if p.is_file()];refs+=outputs
 baseline.module(baseline.FREEZER,'upton_full22_current_restoration_nomination_freezer').freeze(BATCH,'private-full22-exact-saved-authentic-current-plane-restoration-nomination-only',[check(q)for q in refs],dict(uids=baseline.OWNED+[baseline.SECONDARY,baseline.NATIVE],sourceOnly=True,physicalAccepted=False,newlyInstalled=0))

def main():
 if '--schema-only'in sys.argv:print(json.dumps(schema_only(),sort_keys=True));return
 if '--owned'in sys.argv:return owned()
 assert '--nominate-full22-current-plane-restoration-only'in sys.argv and not DOC.exists() and not LOCAL.exists()
 load();prep=read(PROPOSAL/'actual-readonly-preparation.json');assert prep['passed'] and prep['caller']==ref(Path(__file__))
 uids=baseline.OWNED+[baseline.SECONDARY,baseline.NATIVE,baseline.FOREIGN];resources=['building:'+u for u in uids]+['terrain-patch:'+u for u in uids]+['immutable-source-proof:'+BATCH]
 claim=reservations.claim('upton-full22-current-restoration-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  save(LEASE,json.loads(json.dumps(lease,default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
