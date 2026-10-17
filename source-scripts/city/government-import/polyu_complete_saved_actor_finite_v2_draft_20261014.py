"""Exact closed-v1 chunk resume with validated combined executor; no prefix arithmetic."""
from pathlib import Path
from fractions import Fraction as F
import json,sys,time,uuid,subprocess,importlib.util
import numpy as np
from run import ROOT,HERE,read,save,connect,reservations
from exact_distinct_evidence_refs_v1_20261014 import distinct_refs
from exact_closed_ground_aabb_pruning_v1_20261011 import CompleteGround
from upton_parent_tin_regression_bookkeeping_v1_20261012 import sha,triangles
from exact_finite_combined_coverage_cache_v1_draft_20261014 import executor
import polyu_whole_actor_current_ground_delta3_caller_v1_draft_20261014 as capture
ref,check=capture.ref,capture.check
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-polyu-complete-saved-actor-finite-v2-20261014'
DOC=BASE/BATCH;PROPOSAL=BASE/(BATCH+'-proposal');LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'

PRIOR_BATCH='government-xl-polyu-complete-saved-actor-finite-v1-20261014'
PRIOR_DOC=BASE/PRIOR_BATCH;PRIOR_CALLER=HERE/'polyu_complete_saved_actor_finite_v1_draft_20261014.py'
PRIOR_LEASE=HERE/'local'/PRIOR_BATCH/'reservation.json'
def inactive_status(status,resources):
 keys=set(resources);rows=status['resources'];assert len({r['resource']for r in rows})==len(rows)
 expected={key:None for key in keys}
 for row in rows:
  assert row['resource']in keys and type(row['active'])is bool and not row['active'],'Active owner remains'
  expected[row['resource']]=str(row['token'])
 assert status['expectedTokens']==expected,'Status tokens do not match exact inactive historical rows'
 return True

def lifecycle():
 stop=read(PROPOSAL/'prior-terminal-release.json')
 assert stop['schema']=='polyu-finite-v1-observed-terminal-release-v1'and stop['priorCaller']==ref(PRIOR_CALLER)and stop['priorReservation']==ref(PRIOR_LEASE)
 assert stop['observedTerminal']and type(stop['observedExitCode'])is int and stop['canonicalLeaseReleased']and stop['noCompletedPriorResult']
 assert not(PRIOR_DOC/'result.json').exists(),'Prior completed result exists; do not duplicate'
 pids=stop['priorPIDs'];assert len(pids)==len(set(pids))==4 and all(type(pid)is int and pid>0 for pid in pids)
 assert all(not(Path('/proc')/str(pid)).exists()for pid in pids),'Prior process still exists'
 assert inactive_status(stop['actualResourceStatus'],read(PRIOR_LEASE)['resources'])
 for q in distinct_refs(stop['evidenceRefs']):check(q)
 return stop

def prefix_entries(pins,actors,before,after):
 manifest=read(ROOT/pins['prefixManifest']['path']);assert manifest['priorTerminalRelease']==ref(PROPOSAL/'prior-terminal-release.json')and manifest['partialPriorEvidenceNotCompleteReceipt']
 expected={(i,mode)for i,a in enumerate(actors['rows'])for mode in a['worlds']};entries={};before_sha,after_sha=sha(before),sha(after);declared={(q['path'],q['sha256'])for q in pins['inputRefs']}
 for e in manifest['entries']:
  key=e['actorIndex'],e['mode'];assert key in expected and key not in entries
  a=actors['rows'][e['actorIndex']];stream=a['worlds'][e['mode']]
  assert e['uid']==a['uid']and e['role']==a['role']and e['wholeWorldSHA256']==stream['worldSHA256']and e['completeFaces']==len(stream['completeWorldTriangles'])
  assert e['beforeGroundSHA256']==before_sha and e['afterGroundSHA256']==after_sha
  assert [Path(q['path']).name for q in e['chunks']]==[f'{j:05}.json.gz'for j in range(len(e['chunks']))]
  folder=PRIOR_DOC/'chunks'/str(e['actorIndex']).zfill(2)/e['mode'];assert [q['path']for q in e['chunks']]==[str(q.relative_to(ROOT))for q in sorted(folder.glob('[0-9][0-9][0-9][0-9][0-9].json.gz'))]
  assert all((q['path'],q['sha256'])in declared for q in e['chunks'])
  assert 0<=e['closedRows']<=e['completeFaces']and(e['closedRows']==e['completeFaces']or e['closedRows']%64==0)
  entries[key]=e
 assert set(entries)==expected
 return manifest,entries

def prefix_rows(entry,world,before_sha,after_sha,before_count,after_count,pulse):
 count=0
 for ordinal,q in enumerate(entry['chunks']):
  data=read(ROOT/q['path']);assert data['uid']==entry['uid']and data['role']==entry['role']and data['mode']==entry['mode']and data['wholeWorldSHA256']==entry['wholeWorldSHA256']
  assert data['beforeGroundSHA256']==before_sha and data['afterGroundSHA256']==after_sha
  assert 0<len(data['rows'])<=64 and(len(data['rows'])==64 or count+len(data['rows'])==len(world))
  for row in data['rows']:
   assert row['sourceFace']==count and row['sourceFaceSHA256']==sha(world[count])and row['noRoleRootAcceptanceCredit']
   for label,ground_sha,ground_count in [('current',before_sha,before_count),('candidate',after_sha,after_count)]:
    selection=row[label+'CompleteSelectedGround'];proof=row[label];ids=selection['selectedOriginalGroundFaces']
    assert selection['completeGroundSHA256']==ground_sha and selection['completeGroundFacetCount']==ground_count
    assert len(ids)==selection['selectedFacetCount'];previous=-1
    for i in ids:assert type(i)is int and previous<i<ground_count;previous=i
    assert proof['sourceFaceSHA256']==row['sourceFaceSHA256']and type(proof['projectionCovered'])is bool and type(proof['ordinaryBoundProved'])is bool
    if proof['coarse']is not None:
     for nested in [proof['coarse']]+([proof['paired']]if proof['paired']is not None else[]):
      assert nested['sourceFaceSHA256']==row['sourceFaceSHA256']and nested['completeCurrentGroundSHA256']==proof['completeGroundSHA256']
    else:assert not ids and not proof['projectionCovered']and not proof['ordinaryBoundProved']
    if proof['ordinaryBoundProved']:assert proof['projectionCovered']and F(proof['exactLowerM'])>=-F(1,2)
   yield row;count+=1;pulse()
 assert count==entry['closedRows']

def canonical_resources():
 resources=[r for r in capture.load()[-1]if not r.startswith('immutable-source-proof:')]+['immutable-source-proof:'+BATCH]
 resources=sorted(resources);assert len(resources)==57 and reservations.normalise(resources)==resources;return resources
def load():
 pins=read(PROPOSAL/'draft-pins.json');assert pins['caller']==ref(Path(__file__))
 for q in distinct_refs(pins['codeRefs']+pins['inputRefs']):check(q)
 comparison=read(ROOT/pins['verifiedExecutorComparison']['path']);assert comparison['passed']and comparison['allBeforeEndPinsVerified']and len(comparison['rows'])==comparison['completeExpectedCases']==6 and all(r['passed']for r in comparison['rows'])
 cert=read(capture.DOC/'ROOT-VERIFIED.json');receipt=read(capture.DOC/'result.json');assert cert['jobId']==receipt['jobId']==pins['completedGroundCaptureJob']and cert['exactNeonReadback']and cert['allEvidenceHashesVerified']and cert['leaseReleased']
 diagnostic=read(capture.DOC/'diagnostic.json.gz');assert diagnostic['startEndAllInputsVerified']and diagnostic['strictOutsideDrawUnchanged']
 actors=read(capture.DOC/'complete-saved-actor-worlds.json.gz');roi=actors['completeWholeActorROI'];assert roi==diagnostic['completeWholeActorROI']
 before=triangles(np.asarray(read(capture.DOC/'complete-whole-actor-current-before-ground.json.gz')['completeRelevantDrawnTriplets'],dtype='<f8').reshape(-1,3,3))
 after=triangles(np.asarray(read(capture.DOC/'complete-whole-actor-current-candidate-ground.json.gz')['completeRelevantDrawnTriplets'],dtype='<f8').reshape(-1,3,3))
 assert sha(before)==pins['beforeGroundSHA256']and sha(after)==pins['afterGroundSHA256']
 assert len(actors['rows'])==26 and actors['rows'][0]['role']=='retained-native'and actors['rows'][1]['role']=='complete-owned-original'and len(actors['rows'][0]['worlds'])==len(actors['rows'][1]['worlds'])==4
 assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==capture.prior.binding.CURRENT
 assert len(actors['rows'][0]['worlds']['providerOriginal']['completeWorldTriangles'])==59527 and len(actors['rows'][1]['worlds']['providerOriginal']['completeWorldTriangles'])==10536
 assert len({r['uid']for r in actors['rows'][2:]})==24 and all(r['role']=='current-BASIC'and len(r['worlds'])==3 for r in actors['rows'][2:])
 for actor in actors['rows']:
  for stream in actor['worlds'].values():
   w=triangles(stream['completeWorldTriangles']);assert sha(w)==stream['worldSHA256']
   if len(w):assert np.all(w[:,:,[0,2]]>=np.array(roi[:2]))and np.all(w[:,:,[0,2]]<=np.array(roi[2:]))
 lifecycle();manifest,entries=prefix_entries(pins,actors,before,after)
 return pins,receipt,actors,before,after,manifest,entries

def schema_only():
 p,r,a,b,n,manifest,entries=load();before_sha,after_sha=sha(b),sha(n)
 for(i,mode),entry in entries.items():
  world=triangles(a['rows'][i]['worlds'][mode]['completeWorldTriangles'])
  for row in prefix_rows(entry,world,before_sha,after_sha,len(b),len(n),lambda:None):pass
 return dict(reusedClosedRows=sum(e['closedRows']for e in entries.values()),passed=True,completeActorRecords=26,completeOwnedFaces=10536,nativeCompleteFaces=59527,BASICRows=24,beforeGroundFaces=len(b),afterGroundFaces=len(n),canonicalResources=canonical_resources(),noFiniteDBLease=True)
def owned():
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();last=time.monotonic()
 def pulse(force=False):
  nonlocal last
  if force or time.monotonic()-last>20:assert reservations.heartbeat(lease)['ok']and reservations.owns(lease);last=time.monotonic()
 pins,receipt,actors,before,after,manifest,entries=load();prep=read(PROPOSAL/'actual-readonly-preparation.json');assert prep['passed']and prep['caller']==ref(Path(__file__))
 refs=distinct_refs(pins['codeRefs']+pins['inputRefs']+prep['evidenceRefs']+[ref(PROPOSAL/'draft-pins.json'),ref(PROPOSAL/'actual-readonly-preparation.json')])
 with connect()as db:db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 def fence():
  for q in distinct_refs(refs):check(q);pulse()
  assert reservations.owns(lease)and ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==capture.prior.binding.CURRENT
 assert lease['resources']==canonical_resources()
 fence();DOC.mkdir();old=CompleteGround(before);new=CompleteGround(after);before_sha=sha(before);after_sha=sha(after);cache={};mode_cache={};results=[];finite_record,coverage_cache=executor()
 for actor_index,actor in enumerate(actors['rows']):
  modes=[]
  for mode,stream in actor['worlds'].items():
   world=triangles(stream['completeWorldTriangles']);key=(stream['worldSHA256'],before_sha,after_sha);reused=key in mode_cache
   if not reused:
    entry=entries[(actor_index,mode)];chunks=list(entry['chunks']);rows=[];current_failed=[];candidate_failed=[];regressed=[];candidate_uncovered=[]
    def account(row):
     i=row['sourceFace'];current,candidate=row['current'],row['candidate']
     if not current['ordinaryBoundProved']:current_failed.append(i)
     if not candidate['ordinaryBoundProved']:candidate_failed.append(i)
     if not candidate['projectionCovered']:candidate_uncovered.append(i)
     if current['ordinaryBoundProved']and not candidate['ordinaryBoundProved']:regressed.append(i)
    for row in prefix_rows(entry,world,before_sha,after_sha,len(before),len(after),pulse):account(row)
    print(json.dumps(dict(actor=actor['uid'],mode=mode,reusedClosedRows=entry['closedRows'],reusedChunks=len(chunks),noPrefixFiniteOrSelectorReplay=True)),flush=True)
    def flush():
     nonlocal rows
     if not rows:return
     p=DOC/'chunks'/str(actor_index).zfill(2)/mode/(str(len(chunks)).zfill(5)+'.json.gz');assert not p.exists();tmp=p.with_name(p.name+'.tmp.json.gz')
     save(tmp,dict(uid=actor['uid'],role=actor['role'],mode=mode,wholeWorldSHA256=stream['worldSHA256'],beforeGroundSHA256=before_sha,afterGroundSHA256=after_sha,rows=rows));tmp.replace(p);chunks.append(ref(p));rows=[];pulse(True)
    for i in range(entry['closedRows'],len(world)):
     face=world[i]
     exact=[[F(float(x))for x in q]for q in face.tolist()];old_ids,old_binding=old.select(exact);new_ids,new_binding=new.select(exact)
     findings=[]
     for ground,ids in [(before,old_ids),(after,new_ids)]:
      k=(sha(face),sha(ground[ids]))
      if k not in cache:cache[k]=finite_record(face,ground[ids])
      findings.append(cache[k])
     current,candidate=findings
     row=dict(sourceFace=i,sourceFaceSHA256=sha(face),currentCompleteSelectedGround=old_binding,candidateCompleteSelectedGround=new_binding,current=current,candidate=candidate,unchangedCompleteRelevantTuple=current is candidate,noRoleRootAcceptanceCredit=True)
     account(row);rows.append(row);pulse()
     if len(rows)==64:flush();print(json.dumps(dict(actor=actor['uid'],role=actor['role'],mode=mode,completed=min(len(chunks)*64,len(world)),total=len(world))),flush=True)
    flush();summary=dict(chunks=chunks,completeProcessedSourceFaces=len(world),currentOrdinaryUnproved=current_failed,candidateOrdinaryUnproved=candidate_failed,currentClearCandidateUnproved=regressed,candidateUncovered=candidate_uncovered);mode_cache[key]=summary
   modes.append(dict(mode=mode,wholeWorldSHA256=stream['worldSHA256'],completeFaces=len(world),findings=mode_cache[key],exactWholeSourceAndTwoGroundTupleModeReuse=reused));pulse(True)
  results.append(dict(uid=actor['uid'],role=actor['role'],suppressionVerbatim=actor.get('suppressionVerbatim'),worlds=modes,allSourceSlotsAccounted=True,emptyConstructorUncredited=actor.get('emptyConstructorIsAccountedNotFabricated',False)))
 old.verify_binding();new.verify_binding();save(DOC/'complete-full-actor-current-candidate-finite.json.gz',dict(rows=results,completeWholeActorROI=actors['completeWholeActorROI'],beforeGroundSHA256=before_sha,afterGroundSHA256=after_sha,allUncoveredBurialAndZerosRetained=True,noHeightIndexEveryFaceOrEngineeringGate=True,noGuardRayConstructorOrSourceDecodeReplay=True,physicalAccepted=False,installationApproved=False,priorPrefixManifest=pins['prefixManifest'],noPrefixArithmeticReplayed=True,combinedCoverageCacheCounters=dict(hits=coverage_cache.hits,misses=coverage_cache.misses,bounds=coverage_cache.bounds_totals)))
 refs=distinct_refs(refs+[ref(p)for p in DOC.rglob('*')if p.is_file()]);fence()
 spec=importlib.util.spec_from_file_location('polyu_complete_finite_freezer',capture.prior.FREEZER);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 result=m.freeze(BATCH,'complete-native59527-owned10536-and24-current-BASIC-actual-union-finite-only',[check(q)for q in refs],dict(uids=sorted(set(r['uid']for r in results)),sourceOnly=True,newlyInstalled=0,physicalAccepted=False));fence();print(json.dumps(dict(jobId=result['jobId'],result=ref(DOC/'result.json'))),flush=True)
def main():
 if '--schema-only'in sys.argv:print(json.dumps(schema_only()));return
 if '--owned'in sys.argv:return owned()
 assert '--resume-complete-saved-actors-only'in sys.argv and not DOC.exists()and not LOCAL.exists();load();resources=canonical_resources()
 assert not reservations.owns(read(PRIOR_LEASE));status=reservations.status(read(PRIOR_LEASE)['resources']);assert inactive_status(status,read(PRIOR_LEASE)['resources'])
 claim=reservations.claim('polyu-complete-finite-v2-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  save(LEASE,json.loads(json.dumps(lease,default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
