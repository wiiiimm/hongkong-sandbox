from pathlib import Path
import sys,json,copy
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT/'source-scripts/city/government-import'))
import upton_scoped_subdivision_saved64_geometry_bound_validator_draft_v1_20261013 as a
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
pids=[2560704,2560711,2561169,2561712];assert not any(Path('/proc',str(i)).exists()for i in pids);matches=[]
for p in Path('/proc').iterdir():
 if not p.name.isdigit():continue
 try:args=p.joinpath('cmdline').read_bytes().split(b'\0')
 except OSError:continue
 if any(str(q).encode()in args for q in [Path(a.__file__),a.RUNTIME,a.LEASE]):matches.append(int(p.name))
assert not matches and a.ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==a.previous.prior.CURRENT
rays=a.read(a.DOC/'actual-saved64-full-candidate-native-max-ray-findings.json.gz');outcome=a.read(a.DOC/'unchanged-base-parent-validator-outcome.json')
assert rays['samples']==len(rays['rows'])==64 and not rays['failedRows']and rays['maxError']<.01 and outcome['passed']
candidate=a.read(a.check(outcome['metadataOnlyCandidate']));stripped=copy.deepcopy(candidate);stripped['nativeMesh'].pop('sourceOverlap');assert stripped==a.read(a.capture.DOC/'private-native-terrain-candidate.json.gz')and a.previous.canonical(stripped)==a.GEOMETRY
pairproof=a.read(a.DOC/'complete2128-exact-new-old-area-pair-correspondence.json.gz');assert pairproof['completePairs']==len(pairproof['rows'])==2128
log=P/'actual-terminal-supervisor.log';assert not log.exists();log.write_bytes(Path('/tmp/upton-scoped-max64-geometry-bound-20261013.log').read_bytes())
result=dict(passed=True,actualPTY=15375,actualCallerExitCode=0,jobId=receipt['jobId'],result=a.ref(a.DOC/'result.json'),allEvidenceRefsVerified=len(receipt['evidenceRefs']),totalEvidenceBytes=total,all66Code130InputPinsExact=True,currentManifestSHA256=a.previous.prior.CURRENT,releasedGroups=json.loads(json.dumps(groups,default=str)),observedProducerPIDs=pids,allObservedProducerPIDsAbsent=True,directProcNoCallerRuntimeOrLeaseSupervisorMatches=True,terminalLog=a.ref(log),samples=64,maxError=rays['maxError'],failedRows=[],completeNativeFaces=11576,areaPairCorrespondence=2128,newGeometryCanonicalSHA256=a.GEOMETRY,metadataOnlyUnderlyingCandidateExactlyEqual=True,validatorOutcome=outcome,noContinuousMAXPhysicalOrInstallationApproval=True)
path=P/'actual-terminal-neon-allrefs-release-pid-audit.json';assert not path.exists();a.save(path,result);print(json.dumps(result,sort_keys=True))
