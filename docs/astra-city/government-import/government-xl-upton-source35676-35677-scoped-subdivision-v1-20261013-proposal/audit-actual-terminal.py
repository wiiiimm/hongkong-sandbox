from pathlib import Path
import sys,json
import numpy as np
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT/'source-scripts/city/government-import'))
import upton_saved_source35676_35677_scoped_subdivision_draft_v1_20261013 as a
P=Path(__file__).parent
receipt=a.read(a.DOC/'result.json');assert receipt['jobId']=='631ef7725bfb00469d06c137117df65204fb7965c3150f03a301301683a39c49';refs=receipt['evidenceRefs'];total=0
for q in refs:total+=a.check(q).stat().st_size
pins=a.read(P/'draft-pins.json')
for q in pins['codeRefs']+pins['inputRefs']:a.check(q)
prep=a.read(P/'actual-readonly-preparation.json');a.check(prep['driver']);a.check(prep['helperValidation'])
for row in prep['commands']:assert row['exitCode']==0;a.check(row['log'])
with a.connect()as c:
 c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 cursor=c.execute('SELECT token,owner,batch,resources,heartbeat_at,lease_until,released_at FROM astra_modelling.reservation_groups WHERE batch=%s ORDER BY released_at',(a.BATCH,));groups=[dict(zip([d.name for d in cursor.description],row))for row in cursor.fetchall()]
assert len(groups)==2 and all(g['released_at']is not None for g in groups)and sorted(len(g['resources'])for g in groups)==[1,11]
groups=json.loads(json.dumps(groups,default=str));pids=[2102207,2102210];assert not any(Path('/proc',str(i)).exists()for i in pids)
matched=[]
for q in Path('/proc').iterdir():
 if not q.name.isdigit():continue
 try:args=q.joinpath('cmdline').read_bytes().split(b'\0')
 except OSError:continue
 if str(Path(a.__file__)).encode()in args or str(a.LEASE).encode()in args:matched.append(int(q.name))
assert not matched
assert a.ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==a.prior.prior.prior.prior.CURRENT
out=a.read(a.DOC/'private-source-family-subdivision-nomination.json.gz');candidate=np.asarray(out['candidateRawPositionTriplets'],dtype='<f8');old=np.asarray(a.read(a.check(out['originalNomination']))['candidateRawPositionTriplets'],dtype='<f8');mapping=out['completeOldNewIndexMapping']
assert candidate.shape==(11576,3,3)and old.shape==(11575,3,3)and len(mapping)==11575
assert [q['oldCandidateFace']for q in mapping]==list(range(11575))and [j for q in mapping for j in q['newCandidateFaces']]==list(range(11576))
for i,r in enumerate(mapping):
 if i==380:assert len(r['newCandidateFaces'])==2 and not r['allOldRawBytesUnchanged'];continue
 assert r['allOldRawBytesUnchanged']and len(r['newCandidateFaces'])==1 and candidate[r['newCandidateFaces'][0]].tobytes()==old[i].tobytes()
assert len(out['protectedWholeCurrentTripletsUnchanged'])==68
for q in out['protectedWholeCurrentTripletsUnchanged']:assert candidate[q['newCandidate']].tobytes()==old[q['oldCandidate']].tobytes()
assert len(out['completeSavedFailuresVerbatim']['interval'])==100 and len(out['completeSavedFailuresVerbatim']['area'])==257
log=P/'actual-terminal-supervisor.log';assert not log.exists();log.write_bytes(Path('/tmp/upton-source-family-subdivision-20261013.log').read_bytes())
result=dict(passed=True,actualPTY=10558,actualCallerExitCode=0,supervisorReportedReleased=True,jobId=receipt['jobId'],result=a.ref(a.DOC/'result.json'),output=a.ref(a.DOC/'private-source-family-subdivision-nomination.json.gz'),pinnedNeonCompleteExactResult=True,allEvidenceRefsVerified=len(refs),totalEvidenceBytes=total,all46Code110InputPinsExact=True,currentManifestSHA256=a.prior.prior.prior.prior.CURRENT,releasedGroups=groups,observedProducerPIDs=pids,allObservedProducerPIDsAbsent=True,directProcNoCallerOwnedOrLeaseSupervisorMatches=True,supervisorOwnedPIDsNotCapturedBeforeTerminal=True,terminalLog=a.ref(log),preparation=a.ref(P/'actual-readonly-preparation.json'),validation=a.ref(P/'helper-validation.json'),oldCandidateFaces=11575,newNativeNominationFaces=11576,unchangedOldTriplets=11574,protectedWholeCurrentTripletsUnchanged=68,completeOldNewIndexMapVerified=True,exactIdealPartitionProofVerbatim=out['exactSourceFamilyPartitionProof'],noProductionCaptureCoverageOrdinarySamplerValidatorOrAcceptance=True)
path=P/'actual-terminal-neon-allrefs-release-pid-audit.json';assert not path.exists();a.save(path,result);print(json.dumps(result,sort_keys=True))
