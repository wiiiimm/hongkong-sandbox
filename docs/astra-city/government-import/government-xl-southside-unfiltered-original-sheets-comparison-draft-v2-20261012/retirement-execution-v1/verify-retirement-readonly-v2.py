"""ROOT-reviewed retirement verification only: no file, lease, job or review writes."""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[5]
H=R/'source-scripts/city/government-import';sys.path.insert(0,str(H))
from run import ROOT,connect,reservations
from psycopg.rows import dict_row
assert ROOT==R
B='government-xl-southside-315025-300867-unfiltered-original-sheets-comparison-v1-20261012'
LOCAL=H/'local'/B;D=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
audit_path=D/'terminal-audit.json';audit_sha=sha(audit_path)
assert audit_sha=='6fca46945cff5fb8b90f92800e112c1311676246ea20db48f51666050005b2d5'
audit=json.loads(audit_path.read_text());lease_path=LOCAL/'reservation.json';lease=json.loads(lease_path.read_text())
assert audit['priorBatch']==lease['batch']==B and audit['priorLeaseToken']==str(lease['token'])
assert sha(lease_path)==audit['priorLeaseFileSHA256']=='f16f0c05fc7813dd86ec120371d0ca76ef971a1f568317347c21f985a9b3377e'
assert len(lease['resources'])==len(set(lease['resources']))==52
assert audit['priorLeaseReleased']is True and audit['noOwnedOrSupervisorProcessRemaining']is True and audit['noChildProcessGroupRemaining']is True
assert audit['supervisorResult']==dict(ok=False,error='interrupted',exitCode=130,released=True)
assert not any((Path('/proc')/str(pid)).exists()for pid in [1342911,1342764])
lines=subprocess.check_output(['ps','-eo','pid=,ppid=,pgid=,args='],text=True).splitlines()
assert not any(int(q.split(None,3)[2])==1342911 for q in lines if q.strip())
caller=str(H/'xl-southside-315025-300867-unfiltered-original-sheets-comparison-v1-20261012.py');supervisor=str(H.parent/'shared-modelling/reservations.py')
assert not any((caller in q and '--owned'in q)or(supervisor in q and str(lease_path)in q)for q in lines)
assert sha(R/'3d-viewer/city/data/manifest.json')=='2dde0cfc3c0869963c185c3398e48a1928c76802b2efa6c2d9713183a6ad5540'
assert sha(LOCAL/'completed-315025-0-providerOriginal.json.gz')=='1323728290de2fea8731df60a8091d9aaa422aa7b8f9bce415bcfe6522389b21'
assert not(R/'docs/astra-city/government-import'/B/'result.json').exists()
with connect()as c:
 c.execute('SET TRANSACTION READ ONLY');c.row_factory=dict_row
 group=c.execute('SELECT *, (released_at IS NULL AND lease_until>clock_timestamp()) AS active FROM astra_modelling.reservation_groups WHERE token=%s AND owner=%s',(lease['token'],lease['owner'])).fetchone()
 assert group and group['batch']==B and group['resources']==lease['resources']and group['released_at']is not None and group['active']is False
 assert str(group['released_at'])==audit['currentGroup']['released_at']
 rows=reservations._rows(c,lease['resources'])
 assert len(rows)==52 and {q['resource']:q['generation']for q in rows}==lease['generations']
 assert all(str(q['token'])==str(lease['token'])and q['active']is False and q['released_at']==group['released_at']for q in rows)
 events=c.execute('SELECT action,actor,token,resources FROM astra_modelling.reservation_events WHERE token=%s AND action=%s',(lease['token'],'release')).fetchall()
 assert len(events)==1 and events[0]['actor']==lease['owner']and events[0]['resources']==lease['resources']
 assert reservations._current(c,lease)is None
 release_time=group['released_at'].isoformat()
print(json.dumps(dict(verified=True,terminalAuditSHA256=audit_sha,exactResources=52,exactTokenAndGenerationsVerified=True,exactOneReleaseEventVerified=True,leaseReleased=True,releaseTime=release_time,oldChildSupervisorAndGroupAbsent=True,currentManifest2ddeVerified=True,completeProviderCheckpointVerified=True,completedV1Absent=True,readOnly=True,descriptorIssued=False,newWorkerStarted=False,currentAcceptance=False),sort_keys=True))
