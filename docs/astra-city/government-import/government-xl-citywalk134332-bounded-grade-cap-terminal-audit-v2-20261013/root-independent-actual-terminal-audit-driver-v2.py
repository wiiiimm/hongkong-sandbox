"""Read-only actual terminal/output/release audit; no numerical replay or claim."""
import argparse,json,pathlib,subprocess,sys,hashlib,shutil
ROOT=pathlib.Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'source-scripts/city/government-import'))
import citywalk134332_bounded_whole_facet_grade_cap_draft_v2_20261013 as Q
A=pathlib.Path(__file__).resolve().parent
MAN='c00fd9f731b1bcbf4d2df6067a5cb3231f0eaa8c503a8adea584fec39bf73bf7'
PIDS=[1599820,1602373,1602551]
assert Q.ref(A/'actual-terminal-no-pids-release-audit-v2.json')['sha256']=='08db0a8e1026b4cbce536d712b2aec9b8d7900343f075579f855c101a0e1f91b'
raw=pathlib.Path('/tmp/citywalk134332-bounded-grade-cap-supervised-terminal-v2-20261013.log')
assert all(not pathlib.Path('/proc',str(p)).exists() for p in PIDS)
ps=subprocess.check_output(['ps','-eo','pid,ppid,args'],text=True)
survivors=[l for l in ps.splitlines() if 'citywalk134332_bounded_whole_facet_grade_cap_draft_v2_20261013.py' in l and '/tmp/astra-city-venv/bin/python' in l and '/bin/bash' not in l]
assert not survivors,survivors
log=raw.read_bytes();stat=raw.stat();h=hashlib.sha256(log).hexdigest()
assert b"'ok': False, 'error': 'reserved'" in log and b'46e163f6-0361-41be-aef2-dcf8683fbccc' in log and b'"released": true' in log and b'"exitCode": 1' in log
closed=A/'root-closed-actual-full-supervised-terminal-v2.log';assert not closed.exists();closed.write_bytes(log)
assert hashlib.sha256(raw.read_bytes()).hexdigest()==h
failed=Q.read(Q.LOCAL/'failed-terminal-parent-audit.json');release=Q.read(Q.LOCAL/'parent-release-audit.json');lease=Q.read(Q.LOCAL/'immutable-lease-at-start.json')
assert failed['noCompletedResultClaim'] and release['ownsAfterCleanup'] is False
with Q.connect() as db:
 db.execute('SET TRANSACTION READ ONLY')
 group=db.execute('SELECT token,owner,heartbeat_at,lease_until,released_at,clock_timestamp() FROM astra_modelling.reservation_groups WHERE token=%s',(lease['token'],)).fetchone()
 retained=db.execute('SELECT count(*) FROM astra_modelling.reservations WHERE token=%s',(lease['token'],)).fetchone()[0]
 active=db.execute('SELECT count(*) FROM astra_modelling.reservations r JOIN astra_modelling.reservation_groups g USING(token) WHERE r.token=%s AND g.released_at IS NULL AND g.lease_until>clock_timestamp()',(lease['token'],)).fetchone()[0]
 activebatch=db.execute('SELECT count(*) FROM astra_modelling.reservation_groups WHERE batch=%s AND released_at IS NULL AND lease_until>clock_timestamp()',(Q.BATCH,)).fetchone()[0]
assert str(group[0])==str(lease['token']) and group[1]==lease['owner'] and group[4] is not None and retained==21 and active==0 and activebatch==0
assert Q.reservations.owns(lease) is False
*_,before,contract=Q.inputs(argparse.Namespace(expected_manifest=MAN))
assert before==Q.read(Q.LOCAL/'protected-state-before.json') and len(before['currentState']['uids'])==19 and before['currentState']['observedProtectedReviewRecords']==1704
d=Q.read(Q.D/'diagnostic.json.gz');assert len(d['all12Bindings'])==12 and len(d['distinctGradeCapDiagnostics'])==3 and d['completeSourceFaces']==41277 and d['originalBodies']==193 and d['completeGroundFaces']==4215
assert d['sourceOnly'] and not any(d[k] for k in ['currentAcceptance','identityAccepted','physicalAccepted','installationApproved','gradeRootAccepted'])
seeds=sorted((Q.LOCAL/'grade').glob('*/*.json.gz'));tuples=sorted(Q.LOCAL.glob('completed-*.json.gz'));assert len(seeds)==2049 and len(tuples)==3
summary=[]
for key,z in d['distinctGradeCapDiagnostics'].items():
 assert Q.read(Q.LOCAL/('completed-'+z['sourceWorld']+'.json.gz'))==z
 assert len(z['all683SeedProofs'])==len(z['all683Routes'])==683 and len(z['coverageOnlyFaceIDs'])==1322
 for s in z['all683SeedProofs']:assert Q.read(Q.LOCAL/'grade'/key/f"{s['seed']:05d}.json.gz")==s
 summary.append(dict(world=z['sourceWorld'],gradeCandidates=683,qualifiedGrade=sum(s['qualifiedGradeDiagnostic'] for s in z['all683SeedProofs']),capPaths=sum(bool(s['pathCapToSeed']) for s in z['all683Routes']),scopedMisses=sum(not bool(s['pathCapToSeed']) for s in z['all683Routes']),budgetReached=sum(s['budgetReached'] for s in z['all683Routes']),examinedEdges=len(z['allExaminedWholeSharedEdges'])))
evidence=[closed,pathlib.Path(__file__),pathlib.Path(Q.__file__),Q.FREEZER,Q.P/'METHOD.md',Q.P/'input-contract.json',Q.LOCAL/'failed-terminal-parent-audit.json',Q.LOCAL/'parent-release-audit.json',Q.LOCAL/'immutable-lease-at-start.json',Q.LOCAL/'actual-launch-process-session-token-audit-v2.json',Q.LOCAL/'protected-state-before.json']
refs=[Q.ref(p) for p in evidence];seedrefs=[Q.ref(p) for p in seeds];tuplerefs=[Q.ref(p) for p in tuples];diagref=Q.ref(Q.D/'diagnostic.json.gz')
assert Q.inputs(argparse.Namespace(expected_manifest=MAN))[-2]==before
assert all(not pathlib.Path('/proc',str(p)).exists() for p in PIDS) and Q.reservations.owns(lease) is False
for e in refs+seedrefs+tuplerefs+[diagref]:assert Q.ref(ROOT/e['path'])==e
assert hashlib.sha256(raw.read_bytes()).hexdigest()==h
out=dict(authoritativeSession=53906,exitCode=1,numericalDiagnosticsComplete=True,freezerReservationCollisionObserved=True,actualProducerPIDs=PIDS,allActualProducerPIDsGone=True,canonicalGroupReleased=True,ownsAfterTerminal=False,savedCompleteDiagnostic=diagref,actualTerminalEvidenceRefs=refs,allCompletedPerSeedRefs=seedrefs,completedTupleRefs=tuplerefs,tupleSummaries=summary,currentUIDs=19,protectedReviewRecords=1704,currentProtectedBeforeAfterExact=True,currentNativeCount=6650,sourceOnly=True,currentAcceptance=False,physicalAccepted=False,installationApproved=False,numericalReplay=False,reservationReadback=dict(token=str(group[0]),owner=group[1],heartbeatAt=str(group[2]),leaseUntil=str(group[3]),releasedAt=str(group[4]),observedAt=str(group[5]),retainedResourceRows=retained,activeJoinedResourceRows=active,activeBatchGroups=activebatch),fullExternalLogLineage=dict(path=str(raw),sha256=h,bytes=len(log),inode=stat.st_ino,mtimeNS=stat.st_mtime_ns,closedCopy=Q.ref(closed),notTrimmed=True))
Q.save(A/'root-independent-actual-terminal-no-pids-release-audit-v2.json',out)
print(json.dumps(dict(audit=Q.ref(A/'root-independent-actual-terminal-no-pids-release-audit-v2.json'),tuples=summary,perSeedRefs=len(seedrefs),completedTupleRefs=len(tuplerefs),released=True,noPIDs=True)))
