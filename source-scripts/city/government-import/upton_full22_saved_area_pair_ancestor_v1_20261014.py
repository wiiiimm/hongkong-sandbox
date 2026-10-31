"""Saved new area-pair continuation; exact prefix reuse/fresh added ancestors only."""
from pathlib import Path
import json,sys,time,uuid,subprocess
import numpy as np
import upton_full22_current_plane_actual_production_capture_v1_20261014 as capture
import upton_three_own_layer_changed_area_pair_ancestor_draft_v1_20261013 as previous_pairs
from upton_actual_candidate_clearance_audit_v1_20261012 import candidate_surface
from upton_whole_current_facet_protection_v1_20261012 import exact_overlap_attribution
from upton_inherited_overlap_boundary_v1_20261012 import overlap_pair
from upton_v6_saved_overlap_source_classification_v1_20261013 import classify
from upton_captured_ground_tuple_representation_v1_20261012 import adapt_captured_ground
from upton_parent_tin_regression_bookkeeping_v1_20261012 import sha
from run import ROOT,HERE,read,save,connect,reservations
ref,check=capture.ref,capture.check
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-upton-full22-saved-area-pair-ancestor-v1-20261014'
DOC=BASE/BATCH;PROPOSAL=BASE/(BATCH+'-proposal');LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
OLD_JOB='33ea439d74bee82780434620fb223b67b254ec5c25c7c50b487b5b5aa1f3f96f'
TESTS=previous_pairs.TESTS

def load():
 pins=read(PROPOSAL/'draft-pins.json');assert pins['caller']==ref(Path(__file__))
 for q in pins['codeRefs']+pins['inputRefs']:check(q)
 new_receipt=read(capture.DOC/'result.json');assert new_receipt['jobId']==pins['completedCaptureJob']
 verified=read(capture.DOC/'ROOT-VERIFIED.json');assert verified['jobId']==new_receipt['jobId'] and verified['exactNeonReadback'] and verified['allEvidenceHashesVerified'] and verified['leaseReleased']
 assert read(previous_pairs.DOC/'result.json')['jobId']==OLD_JOB
 _,_,nom,raw,pv,inp,whole=capture.load()
 patch=read(capture.DOC/'private-native-terrain-candidate.json.gz');geometry=previous_pairs.previous_pairs.old_pairs.previous.canonical(patch);assert geometry==pins['candidateGeometryCanonicalSHA256']
 actual=candidate_surface(patch,pv);assert len(actual)==len(raw)==pins['completeNewNativeFacets']
 measured=read(capture.DOC/'new-scoped-geometry-measured-overlap.json.gz')['measured'];assert measured['candidateGeometryCanonicalSHA256']==geometry
 area=[r for r in measured['allProjectedIntersectingPairs']if r['projectedDimension']=='area'];assert len(area)==pins['completeSavedAreaPairs'] and len({(r['leftFace'],r['rightFace'])for r in area})==len(area)
 old_nom=read(check(nom['previousOwnLayerNomination']));old_raw=np.asarray(old_nom['candidateRawPositionTriplets'],dtype='<f8');old_pv=old_nom['candidateFaceProvenance'];assert old_raw.shape==(11580,3,3) and raw[:11580].tobytes()==old_raw.tobytes() and pv[:11580]==old_pv
 old_patch=read(capture.previous_capture.DOC/'private-native-terrain-candidate.json.gz');old_actual=candidate_surface(old_patch,old_pv);assert old_actual.shape==(11580,3,3) and actual[:11580].tobytes()==old_actual.tobytes()
 correspondence=read(previous_pairs.DOC/'complete2141-saved-area-pair-source-ancestor-diagnostic.json.gz');assert correspondence['completeSavedPositiveAreaPairs']==len(correspondence['rows'])==2141 and correspondence['unresolvedRows']==0
 old_measured=read(capture.previous_capture.DOC/'new-scoped-geometry-measured-overlap.json.gz')['measured']
 old_area={(r['leftFace'],r['rightFace']):r for r in old_measured['allProjectedIntersectingPairs']if r['projectedDimension']=='area'}
 old_records={(r['newSavedMeasuredPairVerbatim']['leftFace'],r['newSavedMeasuredPairVerbatim']['rightFace']):r for r in correspondence['rows']};assert len(old_records)==2141 and set(old_records)==set(old_area)
 original=read(check(old_nom['originalNomination']));source_input=read(check(original['allSourceOriginalTriplets']));source=np.asarray(source_input['allOriginalTriplets'],dtype='<f8');assert source.shape==(122721,3,3) and sha(source)==source_input['completeSourceSHA256']=='3ace7f401040b2109fd196c603f506d42f0238292742e528c3c46f786b2d93e6'
 attr=read(check(original['allCurrentTriplets']));current,representation=adapt_captured_ground(attr['rows'][0],expected_faces=9214,expected_ground_sha='b4916dac0a7c911a5b20e7dde729fa9a99fca63fa01896db8380523e6158670a',expected_source_counts=[('3d-viewer/city/data/terrain.json',32),('3d-viewer/city/data/government-native-79882-0.json',9182)])
 si,ci=original['wholeSourceOriginalFaceInventory'],original['wholeCurrentFaceInventory'];assert len(si)==122721 and len(ci)==9214
 for arr,inv in [(source,si),(current,ci)]:
  for i,r in enumerate(inv):assert r['originalFace']==i and r['originalFaceSHA256']==sha(arr[i]) and r['completeOriginalTripletRetainedInSavedInput']
 attribution=read(capture.V6/'packed-source-current-before-compatibility.json.gz')['completeCurrentAttribution'];assert len(attribution)==9214
 for i,r in enumerate(attribution):assert r['globalCurrentFace']==i and r['globalOrderedSavedFaceSHA256']==sha(current[i])
 def ancestor(p):
  kind=p['kind'];assert kind in ['originalTIN','capturedCurrentRing'];i=p['originalFace'];assert type(i)is int
  arr,inv=(source,si)if kind=='originalTIN'else(current,ci);assert 0<=i<len(arr) and inv[i]['originalFaceSHA256']==sha(arr[i])
  if kind=='capturedCurrentRing':assert p['completeCurrentSourceAttribution']==attribution[i]
  return arr[i],dict(kind=kind,originalFace=i,completeSavedAncestorTriplet=arr[i].tolist(),orderedAncestorSHA256=sha(arr[i]),sourceInput=original['allSourceOriginalTriplets']if kind=='originalTIN'else original['allCurrentTriplets'],currentSourceAttribution=p.get('completeCurrentSourceAttribution'))
 reused=[];changed=[];seen=set()
 for r in area:
  a,b=r['leftFace'],r['rightFace'];assert 0<=a<b<len(raw) and r['leftProvenance']==pv[a] and r['rightProvenance']==pv[b]
  _,ar=ancestor(pv[a]);_,br=ancestor(pv[b]);ancestors=[ar,br];key=(a,b)
  if b>=11580:
   changed.append(dict(newSavedMeasuredPairVerbatim=r,completeAncestors=ancestors,reason='new appended authentic current-plane facet requires fresh exact raw/Float32 and ancestor proof'));continue
  saved=old_records[key];old_class=saved.get('freshSourceAncestorClassification',saved.get('oldSourceAncestorClassificationVerbatim'));assert old_class is not None
  assert saved['newSavedMeasuredPairVerbatim']==old_area[key] and r==old_area[key] and key not in seen
  assert raw[a].tobytes()==old_raw[a].tobytes() and raw[b].tobytes()==old_raw[b].tobytes() and actual[a].tobytes()==old_actual[a].tobytes() and actual[b].tobytes()==old_actual[b].tobytes()
  assert pv[a]==old_pv[a] and pv[b]==old_pv[b] and ancestors==old_class['completeAncestors']
  assert saved['noCopiedApproval'] and not saved['physicalAccepted'] and not saved['installationApproved'] and old_class['noCopiedApproval'] and not old_class['physicalAccepted'] and not old_class['installationApproved']
  seen.add(key);reused.append(dict(newSavedMeasuredPairVerbatim=r,completeAncestors=ancestors,oldSourceAncestorClassificationVerbatim=old_class,completePreviousPairCorrespondenceVerbatim=saved,previousCandidateFaces=[a,b],bothRawAndFloat32TripletsExactlyEqual=True,completeAncestorArraysExactlyEqual=True,oldLabelsRemainOldGeometryContext=True,noOldKernelHashOrApprovalRelabelling=True,noCopiedApproval=True,physicalAccepted=False,installationApproved=False))
 assert seen==set(old_records), 'append-only geometry must retain every old pair and every old negative context'
 assert len(reused)==2141 and len(changed)==pins['freshChangedAreaPairs'] and len(area)==len(reused)+len(changed)
 assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==capture.legacy.CURRENT
 return pins,nom,raw,actual,area,reused,changed,correspondence,ancestor,representation,geometry

def schema_only():
 p,n,r,a,area,reused,changed,old,ancestor,representation,geometry=load()
 return dict(passed=True,caller=ref(Path(__file__)),completeNewSavedAreaPairs=len(area),eligibleExactCompletePairAncestorReuse=len(reused),freshChangedPairNominations=len(changed),allOld2141AndHistoricalNegativesRetained=True,completeSourceFacets=122721,completeCurrentFacets=9214,geometryCanonicalSHA256=geometry,noExactPairOrAncestorCalculationDBLeaseOrWorker=True)

def owned():
 lease=read(LEASE);assert reservations.owns(lease) and not DOC.exists();last=time.monotonic()
 def pulse():
  nonlocal last
  if time.monotonic()-last>15:assert reservations.heartbeat(lease)['ok'] and reservations.owns(lease);last=time.monotonic()
 pins,nom,raw,actual,area,reused,changed,old,ancestor,representation,geometry=load();prep=read(PROPOSAL/'actual-readonly-preparation.json');assert prep['passed'] and prep['caller']==ref(Path(__file__))
 refs=pins['codeRefs']+pins['inputRefs']+[ref(PROPOSAL/'draft-pins.json'),ref(PROPOSAL/'METHOD.md'),ref(PROPOSAL/'actual-readonly-preparation.json')]+prep['evidenceRefs']
 for folder,job in [(capture.DOC,pins['completedCaptureJob']),(previous_pairs.DOC,OLD_JOB)]:
  receipt=read(folder/'result.json')
  with connect()as db:db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(job,)).fetchone()==('complete',receipt)
  refs+=[ref(folder/'result.json')]+receipt['evidenceRefs']
 refs=list({(q['path'],q['sha256']):q for q in refs}.values())
 def fence():
  for q in refs:check(q);pulse()
  assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==capture.legacy.CURRENT and reservations.owns(lease)
 fence();DOC.mkdir();fresh=[];unresolved=[]
 for row in changed:
  r=row['newSavedMeasuredPairVerbatim'];a,b=r['leftFace'],r['rightFace'];aa,ar=ancestor(nom['candidateFaceProvenance'][a]);bb,br=ancestor(nom['candidateFaceProvenance'][b]);proof=comparison=raw_proof=raw_comparison=None
  try:
   raw_proof=exact_overlap_attribution(raw[a],raw[b],aa,bb);raw_comparison=overlap_pair(raw[a],raw[b],aa,bb)
   proof=exact_overlap_attribution(actual[a],actual[b],aa,bb);comparison=overlap_pair(actual[a],actual[b],aa,bb)
   pair=dict(leftFace=a,rightFace=b,leftProvenance=r['leftProvenance'],rightProvenance=r['rightProvenance'],measuredProjectedDimension=r['projectedDimension'],proof=proof)
   result=classify(pair,comparison);result['completeAncestors']=[ar,br]
   fresh.append(dict(newSavedMeasuredPairVerbatim=r,freshSourceAncestorClassification=result,freshRawExactPairProof=raw_proof,freshRawAncestorComparison=raw_comparison,rawAndFloat32AreSeparateExactRepresentations=True,allExactKernelsUnchanged=True,noCopiedApproval=True,physicalAccepted=False,installationApproved=False))
  except (AssertionError,KeyError,ValueError)as e:unresolved.append(dict(**row,freshExactPairProof=proof,freshAncestorComparison=comparison,freshRawExactPairProof=raw_proof,freshRawAncestorComparison=raw_comparison,measuredAreaNeverOverridesExactDimension=True,reason=type(e).__name__+': '+str(e),unresolved=True,noCopiedApproval=True,physicalAccepted=False,installationApproved=False))
  pulse()
 by_pair=lambda r:(r['newSavedMeasuredPairVerbatim']['leftFace'],r['newSavedMeasuredPairVerbatim']['rightFace']);complete={by_pair(r):r for r in reused+fresh+unresolved};expected=[(r['leftFace'],r['rightFace'])for r in area]
 assert len(complete)==len(expected) and set(complete)==set(expected)
 save(DOC/'complete-saved-area-pair-source-ancestor-continuation.json.gz',dict(rows=[complete[k]for k in expected],completeSavedPositiveAreaPairs=len(area),exactUnchangedPairReuse=len(reused),freshChangedPairProofs=len(fresh),unresolvedRows=len(unresolved),previousCompleted2141PairPacketVerbatim=old,completeSourceFacets=122721,completeCurrentFacets=9214,currentRepresentation=representation,noNewAllPairsSearch=True,noOldKernelHashOrApprovalRelabelling=True,noApprovalWritten=True,physicalAccepted=False,installationApproved=False))
 save(DOC/'diagnostic.json.gz',dict(candidate=ref(capture.DOC/'private-native-terrain-candidate.json.gz'),newGeometryCanonicalSHA256=geometry,completeSavedMeasuredPairs=ref(capture.DOC/'new-scoped-geometry-measured-overlap.json.gz'),onlyChangedAppendedPairCalculations=True,rawAndFloat32ExactRepresentationsSeparate=True,noMAXRayValidatorOrMetadataApproval=True,noPhysicalOrInstallationApproval=True,newlyInstalled=0))
 fence();refs+=[ref(p)for p in DOC.iterdir()if p.is_file()]
 capture.legacy.module(capture.legacy.FREEZER,'upton_full22_area_pair_freezer').freeze(BATCH,'private-full22-actual-saved-area-pair-exact-source-ancestor-continuation',[check(q)for q in refs],dict(uids=capture.legacy.OWNED+[capture.legacy.SECONDARY,capture.legacy.NATIVE],sourceOnly=True,physicalAccepted=False,newlyInstalled=0))

def main():
 if '--schema-only'in sys.argv:print(json.dumps(schema_only(),sort_keys=True));return
 if '--owned'in sys.argv:return owned()
 assert '--classify-saved-full22-area-pairs-only'in sys.argv and not DOC.exists() and not LOCAL.exists()
 load();prep=read(PROPOSAL/'actual-readonly-preparation.json');assert prep['passed'] and prep['caller']==ref(Path(__file__))
 uids=capture.legacy.OWNED+[capture.legacy.SECONDARY,capture.legacy.NATIVE,capture.legacy.FOREIGN];resources=['building:'+u for u in uids]+['terrain-patch:'+u for u in uids]+['immutable-source-proof:'+BATCH]
 claim=reservations.claim('upton-full22-area-ancestors-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  save(LEASE,json.loads(json.dumps(lease,default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
