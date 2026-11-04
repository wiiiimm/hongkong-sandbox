from pathlib import Path
import os,sys,json,hashlib,signal,datetime
R=Path('/home/williamli/projects/wiiiimm/hongkong-sandbox/.claude/worktrees/astra-hong-kong-city');H=R/'source-scripts/city/government-import';sys.path.insert(0,str(H))
from run import ROOT,connect,reservations
from psycopg.rows import dict_row
assert ROOT==R
D=R/'docs/astra-city/government-import/government-xl-southside-unfiltered-original-sheets-comparison-draft-v2-20261012/retirement-execution-v1';D.mkdir(exist_ok=False)
B='government-xl-southside-315025-300867-unfiltered-original-sheets-comparison-v1-20261012';L=H/'local'/B;P=H/'xl-southside-315025-300867-unfiltered-original-sheets-comparison-v1-20261012.py';leasefile=L/'reservation.json';PY='/tmp/astra-city-venv/bin/python';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not(R/'docs/astra-city/government-import'/B/'result.json').exists()
assert sha(P)=='eccc85281d7a6e047fdfd852cb95f06947cea10d6057b74a5b575b187df5dee9'
checkpoint=L/'completed-315025-0-providerOriginal.json.gz';assert sha(checkpoint)=='1323728290de2fea8731df60a8091d9aaa422aa7b8f9bce415bcfe6522389b21'
assert sha(R/'3d-viewer/city/data/manifest.json')=='2dde0cfc3c0869963c185c3398e48a1928c76802b2efa6c2d9713183a6ad5540'
def proc(pid):
 base=Path('/proc')/str(pid);cmd=base.joinpath('cmdline').read_bytes().decode().rstrip('\x00').split('\x00');stat=base.joinpath('stat').read_text().rsplit(') ',1)[1].split()
 return dict(pid=pid,ppid=int(stat[1]),state=stat[0],startTicks=int(stat[19]),cmdline=cmd,cwd=os.readlink(base/'cwd'),pgid=os.getpgid(pid))
expected_supervisor=[PY,str(H.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(leasefile),'--ttl','3600','--',PY,str(P),'--owned'];expected_child=[PY,str(P),'--owned']
sup=proc(1342764);child=proc(1342911)
assert sup['cmdline']==expected_supervisor and sup['cwd']==str(R)and child['cmdline']==expected_child and child['cwd']==str(R)and child['ppid']==sup['pid']and child['pgid']==child['pid']
lease=json.loads(leasefile.read_text());assert lease['batch']==B and len(lease['resources'])==52 and len(set(lease['resources']))==52
with connect()as c:
 c.execute('SET TRANSACTION READ ONLY');c.row_factory=dict_row
 group=reservations._current(c,lease);assert group is not None and str(group['token'])==str(lease['token'])and group['owner']==lease['owner']and group['batch']==B and group['resources']==lease['resources']
 rows=reservations._rows(c,lease['resources']);assert len(rows)==52 and all(str(q['token'])==str(lease['token'])and q['active']for q in rows)
 assert {q['resource']:q['generation']for q in rows}==lease['generations']
preflight=dict(kind='southside-root-authorised-exact-supervisor-retirement-preflight-v1',checkedAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),supervisor=sup,child=child,priorLeaseFileSHA256=sha(leasefile),currentGroup=group,resourceRows=rows,checkpointSHA256=sha(checkpoint),completeProviderModePreserved=True,completedV1Absent=True,currentManifestUnchanged=True,currentAcceptance=False)
(D/'preflight.json').write_text(json.dumps(preflight,default=str,sort_keys=True,indent=2)+'\n');(D/'log-before-retirement.txt').write_bytes(Path('/tmp/xl-southside-unfiltered-original-sheets-comparison-v1-20261012.log').read_bytes());(D/'retirement-command.py').write_bytes(Path(__file__).read_bytes())
assert proc(sup['pid'])==sup and proc(child['pid'])==child
assert not(R/'docs/astra-city/government-import'/B/'result.json').exists()and sha(checkpoint)==preflight['checkpointSHA256']and sha(leasefile)==preflight['priorLeaseFileSHA256']
os.kill(sup['pid'],signal.SIGTERM)
action=dict(kind='exact-supervisor-SIGTERM-sent',pid=sup['pid'],signal='SIGTERM',sentAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),childDirectSignalSent=False,manualLeaseRelease=False,newWorkerStarted=False,currentAcceptance=False)
(D/'signal.json').write_text(json.dumps(action,sort_keys=True,indent=2)+'\n');print(json.dumps(action))
