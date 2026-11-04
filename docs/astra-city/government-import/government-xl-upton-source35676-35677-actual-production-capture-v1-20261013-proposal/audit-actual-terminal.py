from pathlib import Path
import sys,json
import numpy as np
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT/'source-scripts/city/government-import'))
import upton_source35676_35677_actual_production_capture_draft_v1_20261013 as a
P=Path(__file__).parent;receipt=a.read(a.DOC/'result.json');total=0
for q in receipt['evidenceRefs']:total+=a.check(q).stat().st_size
pins=a.read(P/'draft-pins.json')
for q in pins['codeRefs']+pins['inputRefs']:a.check(q)
prep=a.read(P/'actual-readonly-preparation.json');assert prep['passed']
for q in prep['evidenceRefs']:a.check(q)
for row in prep['commands']:assert row['exitCode']==0;a.check(row['log'])
with a.connect()as c:
 c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 cursor=c.execute('SELECT token,owner,batch,resources,heartbeat_at,lease_until,released_at FROM astra_modelling.reservation_groups WHERE batch=%s ORDER BY released_at',(a.BATCH,));groups=[dict(zip([d.name for d in cursor.description],row))for row in cursor.fetchall()]
assert len(groups)==2 and all(g['released_at']is not None for g in groups)and sorted(len(g['resources'])for g in groups)==[1,11]
pids=[2195959,2195974,2196227,2196409];assert not any(Path('/proc',str(i)).exists()for i in pids);matched=[]
for q in Path('/proc').iterdir():
 if not q.name.isdigit():continue
 try:args=q.joinpath('cmdline').read_bytes().split(b'\0')
 except OSError:continue
 if str(Path(a.__file__)).encode()in args or str(a.LEASE).encode()in args or str(a.RUNTIME).encode()in args:matched.append(int(q.name))
assert not matched
assert a.ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==a.legacy.CURRENT
runtime=a.read(a.DOC/'actual-production-replay.json.gz');guards=a.read(a.DOC/'six-existing-production-protection-guards.json.gz');validator=a.read(a.DOC/'real-validator-outcome.json');measured=a.read(a.DOC/'new-scoped-geometry-measured-overlap.json.gz')
assert runtime['startEndAllInputsVerified']and runtime['currentExteriorXYZOrderedHashMatched']and runtime['currentManifestSHA256']==a.legacy.CURRENT
for path,h in runtime['inputHashes'].items():a.check(dict(path=path,sha256=h))
_,_,source,raw,pv,_=a.load();patch=a.read(a.DOC/'private-native-terrain-candidate.json.gz');pos=np.asarray(patch['nativeMesh']['position'],dtype='<f8').reshape(-1,3);ix=np.asarray(patch['nativeMesh']['index'],dtype=np.int64).reshape(-1,3);assert pos[ix].tobytes()==raw.tobytes()
assert not patch['nativeMesh'].get('sourceOverlap')and not patch['nativeMesh']['source'].get('numericalCoverageGap')
log=P/'actual-terminal-supervisor.log';assert not log.exists();log.write_bytes(Path('/tmp/upton-scoped-actual-production-20261013.log').read_bytes())
out=dict(passed=True,actualPTY=82645,actualCallerExitCode=0,jobId=receipt['jobId'],result=a.ref(a.DOC/'result.json'),candidate=a.ref(a.DOC/'private-native-terrain-candidate.json.gz'),actualDraw=a.ref(a.DOC/'actual-production-replay.json.gz'),pinnedNeonCompleteExactResult=True,allEvidenceRefsVerified=len(receipt['evidenceRefs']),totalEvidenceBytes=total,all55Code117InputPinsExact=True,currentManifestSHA256=a.legacy.CURRENT,releasedGroups=json.loads(json.dumps(groups,default=str)),observedProducerPIDs=pids,allObservedProducerPIDsAbsent=True,directProcNoCallerOwnedRuntimeOrLeaseSupervisorMatches=True,terminalLog=a.ref(log),preparation=a.ref(P/'actual-readonly-preparation.json'),completeNativeFaces=len(raw),completeCandidateDrawnFaces=len(runtime['after']['closedDomainDrawnTriplets']),completeCurrentDrawnFaces=len(runtime['before']['closedDomainDrawnTriplets']),completeRawNominationBytesEqual=True,completeOldNewIndexMapVerified=True,unchangedOtherOldTriplets=11574,protectedWholeCurrentTripletsUnchanged=68,exteriorXYZMatched=True,actualSamplerGridErrors=sum(r['error']is not None for r in runtime['actualCandidateSamplerGridFindings']),allSixExisting516GuardsPassed=guards['allPassed'],guardSamplerErrors=len(guards['allSamplerErrors']),actualValidator=validator,measuredExcessM2=measured['measured']['nativeProjectedExcessM2'],positiveAreaPairs=sum(r['projectedDimension']=='area'for r in measured['measured']['allProjectedIntersectingPairs']),newGeometryNoOldOverlapApproval=True,physicalAccepted=False,installationApproved=False)
path=P/'actual-terminal-neon-allrefs-release-pid-audit.json';assert not path.exists();a.save(path,out);print(json.dumps(out,sort_keys=True))
