"""DRAFT ONLY. Freeze complete diagnostics; no model-review/acceptance writes."""
import argparse,json
from exact_frozen_finite_chunk_prefix_draft_v1_20261012 import hydrate,verify_prefixes
from pathlib import Path
from run import ROOT,HERE,read,connect,reservations
from west_wing26195_complete_current_finite_ground_draft_v3_20261012 import BATCH,DOC,LOCAL,PROPOSAL,CAP,RUNTIME,UID,FACES,CAP_JOB,SOURCE_SHA,MANIFEST_SHA,GROUND_SHA,NAMES,ref,module,state,load_inputs,validation_refs,verified_hydration_history

def verified_lease_history():
 path=PROPOSAL/'exact-two-actual-lease-history-contract.json';assert ref(path)['sha256']=='1d74ee4923a2339364a8fc7e2cf2f8fe5dfa4b3901a9c65f957e4db4c10d89aa';p=read(path);assert p['metadataOnly']and p['exactHistoricalByteArchives']and p['oldReceiptsUnchanged']and p['noSignatureAliases']and len(p['aliases'])==2
 expected={'5b6a47ba-2c22-476f-a3f8-9a4f1577af62','a87ce8c0-b8c2-4cbd-a0f6-bc912ce8a53d'};assert {r['token']for r in p['aliases']}==expected;lookup={};paths={path}
 original=str((HERE/'local/government-xl-west-wing26195-complete-current-finite-ground-v2-20261012/reservation.json').relative_to(ROOT))
 for r in p['aliases']:
  assert r['originalPath']==original and r['ownershipHistoryOnly']and r['noRuntimeOrGeometryExemption'];a=r['actualArchive'];assert ref(ROOT/a['path'])==a and a['sha256']==r['historicalSHA256'];archived=read(ROOT/a['path']);assert archived['token']==r['token']and archived['batch']=='government-xl-west-wing26195-complete-current-finite-ground-v2-20261012';lookup[(original,r['historicalSHA256'])]=ROOT/a['path'];paths.add(ROOT/a['path'])
 return lookup,paths

def exact_declared_metadata_refs(x,paths,lookup):
 if isinstance(x,dict):
  if 'path'in x and 'sha256'in x:
   p=ROOT/x['path'];assert p.is_file()
   if ref(p)['sha256']==x['sha256']:paths.add(p)
   else:
    key=(x['path'],x['sha256']);assert key in lookup,'No exact actual lease archive for declared historical ref';a=lookup[key];assert ref(a)['sha256']==x['sha256'];paths.add(a)
  if 'inputHashes'in x:
   for path,h in x['inputHashes'].items():assert ref(ROOT/path)['sha256']==h;paths.add(ROOT/path)
  for v in x.values():exact_declared_metadata_refs(v,paths,lookup)
 elif isinstance(x,list):
  for v in x:exact_declared_metadata_refs(v,paths,lookup)

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--lease-file',required=True);a=parser.parse_args();lease=read(Path(a.lease_file));assert reservations.owns(lease)and not(DOC/'result.json').exists();receipt,scope,selection,streams,ground,unused=load_inputs();validation_refs();history,history_ref=verified_hydration_history();d=read(DOC/'diagnostic.json.gz');before=read(CAP/'protected-state-before.json')
 assert d['uid']==UID and d['completeFaces']==FACES and d['completeGroundFaces']==3240 and d['completeGroundSHA256']==GROUND_SHA and d['currentNativeCount']==6649 and d['currentManifest']==scope['currentManifest']and d['ordinaryThresholdM']=='-1/2'
 assert d['sourceOnly']and d['legacyInstalledDeliveryPreserved']and d['legacyAcceptanceGapRetained']and not any(d[k]for k in ['physicalAccepted','installationApproved','sourceGeometryChanges','terrainGeometryChanges','sourceBodyRolesQualified','gradeRootProved','wholeEdgeCapPathsQualified','foreignHoldsDischarged','currentAllNativePhysicalProved'])
 assert set(d['allFourStreamBindings'])==NAMES and d['completeActualUnusedPositionBindings']==unused;top=d['originalBodyCensus'];partition=[i for fs in top['sharedEdgeConnectedComponents']for i in fs]+top['exactNonrenderingOriginalFaces'];assert len(partition)==FACES and sorted(partition)==list(range(FACES))and d['genuineBodyObligations']==len(top['sharedEdgeConnectedComponents'])and d['zeroFaceObligations']==len(top['exactNonrenderingOriginalFaces'])and len(d['completeOriginalPlaneAttribution'])==FACES
 from run import digest
 for name,s in streams.items():
  sh=digest(s.tobytes());key=digest((sh+GROUND_SHA).encode());assert d['allFourStreamBindings'][name]==dict(completeFaces=FACES,wholeWorldSHA256=sh,wholeGroundSHA256=GROUND_SHA,proofTupleSHA256=key);proof=d['distinctCompleteFiniteProofs'][key];rows=proof['allWholeFacetProofs'];assert proof['completeFaces']==FACES and [r['face']for r in rows]==list(range(FACES))
  for r in rows:
   assert r['selection']['completeGroundSHA256']==GROUND_SHA and r['selection']['completeGroundFacetCount']==3240 and r['selection']['everyNoncandidateStrictlyDisjoint']and r['selection']['touchingAndCollapsedProjectionsRetained'];assert r['originalGroundFaceBySelectedKernelFace']==r['selection']['selectedOriginalGroundFaces']
  for field,predicate in [('ordinaryFailingFaces','ordinaryFiniteProved'),('coverageFailingFaces','completeProjectionCovered'),('strictUncertifiedFaces','strictPositiveFiniteProved')]:assert proof[field]==[r['face']for r in rows if not r[predicate]]
 assert d['explicitHistoricalNumericalProducerMapping']==history_ref and d['previousFrozenChunkContractsPreserved']and d['allHistoricalProofRowsVerifiedUnchanged']and d['bulkHydrationFullBeforeAfterLeaseCodeSourceCurrentProtectedStateFences']and d['newlyComputedChunksRetainPerChunkFencesAndHeartbeat']
 assert set(d['distinctCompleteFiniteProofs'])=={b['proofTupleSHA256']for b in d['allFourStreamBindings'].values()}
 assert top['completeWorldTrianglesSHA256']==d['allFourStreamBindings']['original']['wholeWorldSHA256']and top['completeOriginalFaceIds']==list(range(FACES))
 labels={i:b for b,fs in enumerate(top['sharedEdgeConnectedComponents'])for i in fs};historical,historical_refs=hydrate(ROOT,history['chunkDescriptors'],labels);assert verify_prefixes(historical,d['distinctCompleteFiniteProofs'])==history['expectedWorldPrefixes']
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(CAP_JOB,)).fetchone()==('complete',receipt)
 assert json.loads(json.dumps(state(before['uids']),default=str))==before['rows'];walker=module(HERE/'parkview_block17_freeze_current_source_evidence_20261011.py','westwing_finite_freezer');paths=set();walker.local_imports(Path(__file__),paths);walker.local_imports(HERE/'west_wing26195_complete_current_finite_ground_draft_v3_20261012.py',paths)
 for e in d['evidenceRefs']+receipt['evidenceRefs']:assert ref(ROOT/e['path'])==e;paths.add(ROOT/e['path'])
 for path in [DOC/'diagnostic.json.gz',LOCAL/'reservation.json']:paths.add(path);walker.declared_refs(read(path),paths)
 lookup,lease_paths=verified_lease_history();paths.update(lease_paths);previous=read(ROOT/history['previousResumeContract']['path'])
 for e in [history['previousResumeContract']]+previous['priorSignalAndReleaseRefs']:
  assert ref(ROOT/e['path'])==e;paths.add(ROOT/e['path']);exact_declared_metadata_refs(read(ROOT/e['path']),paths,lookup)
 assert ref(ROOT/'3d-viewer/city/data/manifest.json')==scope['currentManifest']and reservations.owns(lease)
 result=walker.F.freeze(BATCH,'existing-west-wing-complete-current-finite-ground-no-root-or-physical-approval',sorted(paths),dict(uids=[UID],sourceSHA256=SOURCE_SHA,sourceOnly=True,currentManifestSHA256=MANIFEST_SHA,nativeCount=6649,completeOriginalFaces=FACES,completeActualGroundFaces=3240,genuineBodyObligations=d['genuineBodyObligations'],zeroFaceObligations=d['zeroFaceObligations'],allFourWorldsComplete=True,legacyInstalledDeliveryPreserved=True,legacyPhysicalAcceptanceGapRetained=True,physicalAccepted=False,installationApproved=False,sourceGeometryChanges=0,terrainGeometryChanges=0,modelReviewWrites=0,gradeRootProved=False,wholeEdgeCapPathsQualified=False,foreignHoldsDischarged=False))
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(result['jobId'],)).fetchone()==('complete',result)
 for e in result['evidenceRefs']:assert ref(ROOT/e['path'])==e
 assert json.loads(json.dumps(state(before['uids']),default=str))==before['rows']and ref(ROOT/'3d-viewer/city/data/manifest.json')==scope['currentManifest']and reservations.owns(lease);print(json.dumps(dict(jobId=result['jobId'],allRefs=len(result['evidenceRefs']),physicalAccepted=False)),flush=True)
if __name__=='__main__':main()
