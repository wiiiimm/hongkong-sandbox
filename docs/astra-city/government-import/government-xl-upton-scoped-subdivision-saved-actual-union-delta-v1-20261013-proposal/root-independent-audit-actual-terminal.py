from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT/'source-scripts/city/government-import'))
import upton_scoped_subdivision_saved_actual_union_delta_draft_v1_20261013 as a
P=Path(__file__).parent;receipt=a.read(a.DOC/'result.json');total=0
for q in receipt['evidenceRefs']:total+=a.check(q).stat().st_size
pins=a.read(P/'draft-pins.json')
for q in pins['codeRefs']+pins['inputRefs']:a.check(q)
prep=a.read(P/'actual-readonly-preparation.json');assert prep['passed']
for q in prep['evidenceRefs']:a.check(q)
for r in prep['commands']:assert r['exitCode']==0;a.check(r['log'])
with a.connect()as c:
 c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 cursor=c.execute('SELECT token,owner,batch,resources,heartbeat_at,lease_until,released_at FROM astra_modelling.reservation_groups WHERE batch=%s ORDER BY released_at',(a.BATCH,));groups=[dict(zip([d.name for d in cursor.description],row))for row in cursor.fetchall()]
assert len(groups)==2 and all(g['released_at']is not None for g in groups)and sorted(len(g['resources'])for g in groups)==[1,11]
pids=[2309658,2309665,2310095,2310148];assert not any(Path('/proc',str(i)).exists()for i in pids);matched=[]
for q in Path('/proc').iterdir():
 if not q.name.isdigit():continue
 try:args=q.joinpath('cmdline').read_bytes().split(b'\0')
 except OSError:continue
 if str(Path(a.__file__)).encode()in args or str(a.LEASE).encode()in args:matched.append(int(q.name))
assert not matched and a.ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==a.baseline.CURRENT
out=a.read(a.DOC/'complete-actual-union-finite-delta.json.gz');assert out['newGroundSHA256']==a.GROUND_SHA and out['completeNewDrawnFaces']==11604 and out['completeOldDrawnFaces']==11603
summaries=[]
for actor in out['actors']+[b['findings']for b in out['completeBasicRows']if 'findings'in b]:
 worlds=[]
 for w in actor['worlds']:
  f=w['findings'];rows=[]
  for q in f['chunks']:
   data=a.read(a.check(q));assert data['wholeWorldSHA256']==w['wholeWorldSHA256']and data['completeNewGroundSHA256']==a.GROUND_SHA;rows+=data['rows']
  assert [r['face']for r in rows]==w['completeScope']['selectedFaceIDs']and len(rows)==f['completeProcessedFaces']
  worlds.append(dict(mode=w['mode'],completeFaces=w['completeFaces'],wholeWorldSHA256=w['wholeWorldSHA256'],processedFaces=f['completeProcessedFaces'],exactTupleReused=f['exactRelevantProofsReused'],changedTupleFinite=f['changedTupleFiniteClaims'],uncovered=f['candidateUncovered'],ordinaryUnproved=f['candidateOrdinaryUnproved'],currentClearCandidateUnproved=f['currentClearCandidateUnproved'],exactCompleteTupleModeReuse=w['exactCompleteTupleModeReuse']))
 summaries.append(dict(uid=actor['uid'],role=actor['role'],worlds=worlds))
assert len(out['completeBasicRows'])==1911 and sum('findings'in b for b in out['completeBasicRows'])==52
log=P/'actual-terminal-supervisor.log';assert log.read_bytes()==Path('/tmp/upton-scoped-actual-union-delta-20261013.log').read_bytes()
result=dict(passed=True,actualPTY=87320,actualCallerExitCode=0,jobId=receipt['jobId'],result=a.ref(a.DOC/'result.json'),output=a.ref(a.DOC/'complete-actual-union-finite-delta.json.gz'),pinnedNeonCompleteExactResult=True,allEvidenceRefsVerified=len(receipt['evidenceRefs']),totalEvidenceBytes=total,all57Code124InputPinsExact=True,currentManifestSHA256=a.baseline.CURRENT,releasedGroups=json.loads(json.dumps(groups,default=str)),observedProducerPIDs=pids,allObservedProducerPIDsAbsent=True,directProcNoCallerOwnedOrLeaseSupervisorMatches=True,terminalLog=a.ref(log),preparation=a.ref(P/'actual-readonly-preparation.json'),completeNewDrawnFaces=11604,newGroundSHA256=a.GROUND_SHA,completeOldDrawnFaces=11603,completeBasicActors=1911,affectedBasicActors=52,actorWorldSummary=summaries,allZerosAndCrossingsRetained=out['allZerosAnd23CrossingsRetained'],noGeometryOverlapRootRolePhysicalOrInstallationApproval=True)
assert len(summaries)==56 and all(len(x['worlds'])==4 for x in summaries[:4])
for x in summaries[:2]:
 assert x['uid'] in ['landsd/338946:0','landsd/12728:0']
 assert all(not w['uncovered'] and not w['ordinaryUnproved'] and not w['currentClearCandidateUnproved'] for w in x['worlds'])
assert next(x for x in summaries if x['uid']=='landsd/79883:0')['worlds'][0]['currentClearCandidateUnproved']==[17]
releaseDetails=[]
with a.connect() as c:
 c.execute('SET TRANSACTION READ ONLY')
 for g in groups:
  expected=['source-context:'+a.BATCH] if len(g['resources'])==1 else sorted(['building:'+u for u in a.baseline.OWNED+[a.baseline.SECONDARY,a.baseline.NATIVE,a.baseline.FOREIGN]]+['terrain-patch:'+u for u in a.baseline.OWNED+[a.baseline.SECONDARY,a.baseline.NATIVE,a.baseline.FOREIGN]]+['immutable-source-proof:'+a.BATCH])
  assert sorted(g['resources'])==expected
  assert str(g['token']) in ['0f8f013c-7a61-4e4a-bd2d-651a070a83a3','a85815f8-522f-48c6-b472-4635ddf52b73']
  q=c.execute('SELECT resource,token,generation FROM astra_modelling.reservations WHERE token=%s ORDER BY resource',(g['token'],));rows=[dict(zip([d.name for d in q.description],row))for row in q.fetchall()]
  assert [x['resource']for x in rows]==sorted(g['resources']) and all(str(x['token'])==str(g['token']) and int(x['generation'])>0 for x in rows)
  q=c.execute('SELECT action,actor,token,resources FROM astra_modelling.reservation_events WHERE token=%s AND action=%s',(g['token'],'release'));events=[dict(zip([d.name for d in q.description],row))for row in q.fetchall()]
  assert len(events)==1 and events[0]['actor']==g['owner'] and events[0]['resources']==g['resources']
  releaseDetails.append(dict(token=str(g['token']),rows=rows,releaseEvents=events,currentGenerationNotClaimTimeSnapshot=True))
result['rootReleaseDetails']=json.loads(json.dumps(releaseDetails,default=str));result['executor']='ROOT';result['jobIdExpected']= 'd5ede71c98345b8d3e767d6ac428c29480e20e61b664b8ca01ca8a65577c1e6a';assert receipt['jobId']==result['jobIdExpected'];assert len(receipt['evidenceRefs'])==10324
path=P/'root-independent-terminal-neon-allrefs-release-pid-audit.json';assert not path.exists();a.save(path,result);print(json.dumps(dict(passed=True,jobId=receipt['jobId'],refs=len(receipt['evidenceRefs']),fullOwnedOriginalsOrdinaryPass=True,currentClearBasicRegression=['landsd/79883:0',17],noInstallationApproval=True)))
