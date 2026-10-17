from pathlib import Path
import json,gzip,hashlib,datetime,sys
R=Path('/home/williamli/projects/wiiiimm/hongkong-sandbox/.claude/worktrees/astra-hong-kong-city');H=R/'source-scripts/city/government-import';sys.path.insert(0,str(H));from run import connect,dict_row
B=R/'docs/astra-city/government-import';P=B/'government-xl-southside-private-authentic-terrain-draft-v2-20261012/selective13-parent-restoration-draft-v1/certified-width-constructor-draft-v1';O=P/'actual-terminal-readback-constructor-v4';O.mkdir(exist_ok=False)
CODE=O/'readonly-terminal-verifier-v1.py';CODE.write_bytes(Path(__file__).read_bytes())
BATCH='government-xl-southside-selective13-certified-width-private-terrain-v4-20261013';D=B/BATCH;L=H/'local'/BATCH
CURRENT='c00fd9f731b1bcbf4d2df6067a5cb3231f0eaa8c503a8adea584fec39bf73bf7';JOB='45269823085c3b14077add6a8b9c25e3abc7d3977408e1c2e65a6b12e8f33b63'
def read(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ref(p):return dict(path=str(p.relative_to(R)),sha256=sha(p))
q=read(D/'result.json');t=read(P/'execution-logs-constructor-v4/terminal.json');a=read(D/'full-computed-candidate-and-account.json.gz');lease=read(L/'reservation.json')
assert q['jobId']==JOB and q['batch']==BATCH and t['actualExitCode']==0
assert q['outputFacets']==a['account']['outputFacets']==45447 and q['triangleBudget']==a['account']['triangleBudget']==25000 and q['triangleBudgetPass']is a['account']['triangleBudgetPass']is False
assert a['account']['expensiveRuntimeSkippedBecauseRealBudgetFailure']is True and q['currentAcceptance']is q['physicalAccepted']is q['installationApproved']is q['publication']is False and q['newlyInstalled']==0
assert len(q['evidenceRefs'])==len({r['path']for r in q['evidenceRefs']})==9127
for p in q['evidenceRefs']:assert sha(R/p['path'])==p['sha256'],p['path']
for p,h in a['inputHashes'].items():assert sha(R/p)==h,p
assert sha(R/a['candidatePath'])==a['candidateSHA256'] and sha(R/'3d-viewer/city/data/manifest.json')==CURRENT
pids=[1013600,1013668,1019535,1019565];assert all(not Path('/proc',str(pid)).exists()for pid in pids)
workers=[]
for proc in Path('/proc').iterdir():
 if not proc.name.isdigit():continue
 try:
  argv=(proc/'cmdline').read_bytes().split(b'\0');stat=(proc/'stat').read_text().split(') ',1)[1].split()
  if (any(x.endswith(b'/xl-southside-selective13-certified-width-private-terrain-draft-v4-20261013.py')for x in argv)and any(x in [b'--owned']for x in argv))or int(stat[2])==1019565:workers.append(int(proc.name))
 except(FileNotFoundError,PermissionError,ProcessLookupError):pass
assert not workers
with connect()as c:
 c.row_factory=dict_row;c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT current_database()AS name').fetchone()['name']=='neondb'
 actual=c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(JOB,)).fetchone();assert actual['status']=='complete'and actual['result']==q
 groups=c.execute('SELECT token,owner,batch,resources,released_at,heartbeat_at,lease_until,(released_at IS NULL AND lease_until>clock_timestamp())AS active FROM astra_modelling.reservation_groups WHERE batch=%s ORDER BY created_at',(BATCH,)).fetchall();assert len(groups)==2
 audits=[]
 for g in groups:
  assert g['released_at']is not None and g['active']is False
  rows=c.execute('SELECT resource,token,generation FROM astra_modelling.reservations WHERE token=%s ORDER BY resource',(g['token'],)).fetchall()
  events=c.execute('SELECT action,actor,token,resources FROM astra_modelling.reservation_events WHERE token=%s AND action=%s',(g['token'],'release')).fetchall();assert len(events)==1 and events[0]['actor']==g['owner']and events[0]['resources']==g['resources']
  assert {r['resource']for r in rows}==set(g['resources'])and all(str(r['token'])==str(g['token'])and int(r['generation'])>0 for r in rows)
  if str(g['token'])==lease['token']:
   assert g['owner']==lease['owner']and g['resources']==lease['resources']and len(g['resources'])==124
   assert {r['resource']:r['generation']for r in rows}==lease['generations']
  else:assert g['resources']==['source-context:'+BATCH]
  audits.append(dict(group=g,reservationRows=rows,releaseEvents=events))
assert sum(str(g['token'])==lease['token']for g in groups)==1
account=a['account'];result=dict(checkedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),jobId=JOB,exactPinnedNeonCompleteResult=True,result=ref(D/'result.json'),mainDiagnostic=ref(D/'full-computed-candidate-and-account.json.gz'),candidate=ref(R/a['candidatePath']),allEvidenceRefHashesVerified=9127,allBeforeEndInputHashesVerified=len(a['inputHashes']),currentManifestSHA256=CURRENT,allCanonical124AndDistinctFreezerReleased=True,reservations=audits,absentPIDs=pids,noOwnedWorkerOrProcessGroup=True,terminal=ref(P/'execution-logs-constructor-v4/terminal.json'),auditor=ref(CODE),outputFacets=45447,triangleBudget=25000,triangleBudgetPass=False,packedCollapsedOutputFacetIDs=account['packedCollapsedOutputFacetIDs'],nativeActorsNominated=len(account['whole6650ActualNativeDomainNomination']['nominated']),expensiveRuntimeSkippedBecauseRealBudgetFailure=True,currentAcceptance=False,physicalAccepted=False,newlyInstalled=0,noProducerOrProofReplay=True)
with(O/'audit.json').open('x')as f:json.dump(result,f,sort_keys=True,indent=2,default=str);f.write('\n')
print(json.dumps(dict(jobId=JOB,resultSHA256=sha(D/'result.json'),diagnosticSHA256=sha(D/'full-computed-candidate-and-account.json.gz'),refs=9127,inputPins=len(a['inputHashes']),releasedGroups=len(groups),noPIDs=True,outputFacets=45447,budgetPass=False,collapseIDs=account['packedCollapsedOutputFacetIDs'],auditor=ref(CODE),audit=ref(O/'audit.json'),releasedAt=[str(g['released_at'])for g in groups])))
