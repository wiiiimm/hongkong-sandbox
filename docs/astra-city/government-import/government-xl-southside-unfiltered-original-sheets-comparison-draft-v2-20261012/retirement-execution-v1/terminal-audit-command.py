from pathlib import Path
import sys,json,hashlib,subprocess,datetime
R=Path('/home/williamli/projects/wiiiimm/hongkong-sandbox/.claude/worktrees/astra-hong-kong-city');H=R/'source-scripts/city/government-import';sys.path.insert(0,str(H));from run import ROOT,connect,reservations
from psycopg.rows import dict_row
D=R/'docs/astra-city/government-import/government-xl-southside-unfiltered-original-sheets-comparison-draft-v2-20261012/retirement-execution-v1';B='government-xl-southside-315025-300867-unfiltered-original-sheets-comparison-v1-20261012';L=H/'local'/B;leasefile=L/'reservation.json';lease=json.loads(leasefile.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not any((Path('/proc')/str(pid)).exists()for pid in [1342911,1342764])
ps=subprocess.check_output(['ps','-eo','pid=,ppid=,pgid=,args='],text=True);(D/'process-table-after-retirement.txt').write_text(ps)
assert not any(int(q.split(None,3)[2])==1342911 for q in ps.splitlines()if q.strip())
caller=str(H/'xl-southside-315025-300867-unfiltered-original-sheets-comparison-v1-20261012.py');supervisor=str(H.parent/'shared-modelling/reservations.py')
assert not any((caller in q and '--owned'in q)or(supervisor in q and str(leasefile)in q)for q in ps.splitlines())
log=Path('/tmp/xl-southside-unfiltered-original-sheets-comparison-v1-20261012.log').read_bytes();assert b'"released": true'in log and b'"error": "interrupted"'in log
assert not(R/'docs/astra-city/government-import'/B/'result.json').exists()
checkpoint=L/'completed-315025-0-providerOriginal.json.gz';assert sha(checkpoint)=='1323728290de2fea8731df60a8091d9aaa422aa7b8f9bce415bcfe6522389b21'
with connect()as c:
 c.execute('SET TRANSACTION READ ONLY');c.row_factory=dict_row
 group=c.execute('SELECT *, (released_at IS NULL AND lease_until>clock_timestamp()) AS active FROM astra_modelling.reservation_groups WHERE token=%s AND owner=%s',(lease['token'],lease['owner'])).fetchone()
 assert group and group['released_at']is not None and not group['active']and group['batch']==B and group['resources']==lease['resources']
 rows=reservations._rows(c,lease['resources']);assert len(rows)==52 and all(str(q['token'])==str(lease['token'])and not q['active']and q['released_at']==group['released_at']for q in rows)
 assert {q['resource']:q['generation']for q in rows}==lease['generations']and reservations._current(c,lease)is None
 events=c.execute('SELECT action,actor,token,resources FROM astra_modelling.reservation_events WHERE token=%s AND action=%s',(lease['token'],'release')).fetchall();assert len(events)==1 and events[0]['actor']==lease['owner']and events[0]['resources']==lease['resources']
(D/'log-after-retirement.txt').write_bytes(log)
partial=[dict(path=str(p.relative_to(R)),bytes=p.stat().st_size,sha256=sha(p))for p in sorted(L.rglob('*'))if p.is_file()]
assert sha(R/'3d-viewer/city/data/manifest.json')=='2dde0cfc3c0869963c185c3398e48a1928c76802b2efa6c2d9713183a6ad5540'
result=dict(kind='southside-root-authorised-supervisor-retirement-observation-v1',observedAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),priorBatch=B,authoritativePTY=96525,authoritativePTYTerminalExitCode=1,supervisorResult=dict(ok=False,error='interrupted',exitCode=130,released=True),priorSupervisorPID=1342764,priorChildPID=1342911,noOwnedOrSupervisorProcessRemaining=True,noChildProcessGroupRemaining=True,priorLeaseReleased=True,priorLeaseFileSHA256=sha(leasefile),priorLeaseToken=str(lease['token']),exactResourceCount=52,currentGroup=group,exactResourceRows=rows,exactReleaseEvents=events,completeCheckpointSHA256=sha(checkpoint),completedV1Absent=True,preservedPartialArtifacts=partial,currentManifestSHA256='2dde0cfc3c0869963c185c3398e48a1928c76802b2efa6c2d9713183a6ad5540',oldSourceCodeUnchanged=True,sourceGeometryChanges=0,terrainChanges=0,manualLeaseRelease=False,descriptorIssued=False,newWorkerStarted=False,currentAcceptance=False)
assert sha(H/'xl-southside-315025-300867-unfiltered-original-sheets-comparison-v1-20261012.py')=='eccc85281d7a6e047fdfd852cb95f06947cea10d6057b74a5b575b187df5dee9'
(D/'terminal-audit.json').write_text(json.dumps(result,default=str,sort_keys=True,indent=2)+'\n');(D/'terminal-audit-command.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(dict(auditPath=str((D/'terminal-audit.json').relative_to(R)),auditSHA256=sha(D/'terminal-audit.json'),priorLeaseFileSHA256=sha(leasefile),priorLeaseToken=str(lease['token']),exactResources=52,released=True,allProcessesAndGroupAbsent=True,partialFiles=len(partial),checkpointSHA256=sha(checkpoint),logSHA256=sha(D/'log-after-retirement.txt'),descriptorIssued=False,newWorkerStarted=False)))
