from pathlib import Path
import json,gzip,hashlib,datetime,sys
R=Path('/home/williamli/projects/wiiiimm/hongkong-sandbox/.claude/worktrees/astra-hong-kong-city');H=R/'source-scripts/city/government-import';sys.path.insert(0,str(H));from run import connect,dict_row
B=R/'docs/astra-city/government-import';P=B/'government-xl-polyu-sports305582-authentic-local-private-terrain-draft-v1-20261013';O=P/'actual-terminal-readback-constructor-v2';O.mkdir(exist_ok=False)
CODE=O/'readonly-terminal-verifier-v1.py';CODE.write_bytes(Path(__file__).read_bytes())
BATCH='government-xl-polyu-sports305582-authentic-local-private-terrain-v2-20261013';D=B/BATCH;L=H/'local'/BATCH
CURRENT='c00fd9f731b1bcbf4d2df6067a5cb3231f0eaa8c503a8adea584fec39bf73bf7';JOB='f27f496a7877e8eda20dcab082a0c8dbd08eb67e7c6051ca90f908578748ccdf'
def read(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ref(p):return dict(path=str(p.relative_to(R)),sha256=sha(p))
q=read(D/'result.json');t=read(P/'execution-logs-constructor-v2/terminal.json');a=read(D/'full-computed-private-candidate-and-account.json.gz');lease=read(L/'reservation.json');account=a['account']
assert q['jobId']==JOB and q['batch']==BATCH and t['actualExitCode']==0
assert q['outputFacets']==account['outputFacets']==3214 and q['triangleBudget']==account['triangleBudget']==25000 and q['triangleBudgetPass']is account['triangleBudgetPass']is True
assert account['realFloat32CollapsedOutputFacets']==[] and account['actualRuntimeFailure']['errorType']=='KeyError'and account['actualRuntimeFailure']['message']=="'allIncidentRecords'"
assert 'actualProductionSamplerMAXRayReport'not in account and 'unchangedRawPatchValidator'not in account and 'ordinary25NeighbourRawGuards'not in account
assert q['currentAcceptance']is q['physicalAccepted']is q['installationApproved']is q['publication']is False and q['newlyInstalled']==0
assert len(q['evidenceRefs'])==len({r['path']for r in q['evidenceRefs']})==8804
for p in q['evidenceRefs']:assert sha(R/p['path'])==p['sha256'],p['path']
for p,h in a['inputHashes'].items():assert sha(R/p)==h,p
assert sha(R/a['candidatePath'])==a['candidateSHA256'] and sha(R/'3d-viewer/city/data/manifest.json')==CURRENT
assert sha(P/'execution-logs-constructor-v2/execution.log')==t['actualLogSHA256']
pids=[2569264,2569299];assert all(not Path('/proc',str(pid)).exists()for pid in pids)
workers=[]
for proc in Path('/proc').iterdir():
 if not proc.name.isdigit():continue
 try:
  argv=(proc/'cmdline').read_bytes().split(b'\0')
  if any(x.endswith(b'/xl-polyu-sports305582-authentic-local-private-terrain-draft-v2-20261013.py')for x in argv)or any(x==str(L/'reservation.json').encode()for x in argv):workers.append(int(proc.name))
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
   assert g['owner']==lease['owner']and g['resources']==lease['resources']and len(g['resources'])==28
   assert {r['resource']:r['generation']for r in rows}==lease['generations']
  else:assert g['resources']==['source-context:'+BATCH]
  audits.append(dict(group=g,reservationRows=rows,releaseEvents=events))
assert sum(str(g['token'])==lease['token']for g in groups)==1
assert sha(R/'3d-viewer/city/data/manifest.json')==CURRENT
result=dict(checkedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),jobId=JOB,exactPinnedNeonCompleteResult=True,result=ref(D/'result.json'),mainDiagnostic=ref(D/'full-computed-private-candidate-and-account.json.gz'),candidate=ref(R/a['candidatePath']),allEvidenceRefHashesVerified=8804,allBeforeEndInputHashesVerified=len(a['inputHashes']),currentManifestSHA256=CURRENT,allCanonical28AndDistinctFreezerReleased=True,reservations=audits,absentRecordedPIDs=pids,noCallerOwnedOrLeaseSupervisorProcess=True,actualUnrecordedChildPIDNotInvented=True,terminal=ref(P/'execution-logs-constructor-v2/terminal.json'),auditor=ref(CODE),outputFacets=3214,triangleBudget=25000,triangleBudgetPass=True,packedCollapsedOutputFacetIDs=[],nativeActorsNominated=[r['uid']for r in account['native6650ClosedDomainNomination']['nominated']],actualRuntimeFailure=account['actualRuntimeFailure'],MAXRawValidatorAndNeighbourNotExecuted=True,currentAcceptance=False,physicalAccepted=False,newlyInstalled=0,noProducerOrProofReplay=True)
with(O/'audit.json').open('x')as f:json.dump(result,f,sort_keys=True,indent=2,default=str);f.write('\n')
print(json.dumps(dict(jobId=JOB,resultSHA256=sha(D/'result.json'),diagnosticSHA256=sha(D/'full-computed-private-candidate-and-account.json.gz'),refs=8804,inputPins=len(a['inputHashes']),releasedGroups=len(groups),noPIDs=True,outputFacets=3214,budgetPass=True,collapseCount=0,auditor=ref(CODE),audit=ref(O/'audit.json'),releasedAt=[str(g['released_at'])for g in groups])))
