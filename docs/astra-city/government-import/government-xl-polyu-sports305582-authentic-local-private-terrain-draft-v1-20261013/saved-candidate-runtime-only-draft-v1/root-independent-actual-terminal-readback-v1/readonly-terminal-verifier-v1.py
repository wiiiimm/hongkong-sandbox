from pathlib import Path
import json,gzip,hashlib,datetime,sys
R=Path('/home/williamli/projects/wiiiimm/hongkong-sandbox/.claude/worktrees/astra-hong-kong-city');H=R/'source-scripts/city/government-import';sys.path.insert(0,str(H));from run import connect,dict_row
B=R/'docs/astra-city/government-import';P=B/'government-xl-polyu-sports305582-authentic-local-private-terrain-draft-v1-20261013/saved-candidate-runtime-only-draft-v1';O=P/'root-independent-actual-terminal-readback-v1';O.mkdir(exist_ok=False);CODE=O/'readonly-terminal-verifier-v1.py';CODE.write_bytes(Path(__file__).read_bytes())
BATCH='government-xl-polyu-sports305582-saved-private-candidate-runtime-only-v1-20261013';D=B/BATCH;L=H/'local'/BATCH;CURRENT='c00fd9f731b1bcbf4d2df6067a5cb3231f0eaa8c503a8adea584fec39bf73bf7';JOB='ce2589c6c43d007f527d6bc78e51204abf4344a261fd41b0436dc1c6234d316f'
def read(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ref(p):return dict(path=str(p.relative_to(R)),sha256=sha(p))
q=read(D/'result.json');t=read(P/'execution-logs-v1/terminal.json');a=read(D/'saved-candidate-runtime-only-account.json.gz');lease=read(L/'reservation.json');account=a['account']
assert q['jobId']==JOB and q['batch']==BATCH and t['exitCode']==0 and q['candidateFacets']==3214
assert 'actualRuntimeFailure'not in account and account['noConstructionOrDecodeOrPointCheckReplay']is True and account['unchangedRawPatchValidator']['passed']is True and account['ordinary25NeighbourGuardsPass']is False
ray=account['actualProductionSamplerMAXRayReport'];assert ray['allActualRaySamplesPass']is True and ray['failedSamples']==0 and ray['samples']==6701 and ray['completeCandidateFacets']==3214 and ray['existingRayAgreementThresholdM']==1e-5 and ray['ordinaryJoinThresholdM']==.01
edge=read(D/'complete-actual-edge-incidents.json.gz');assert edge['completeIncidentCount']==9642 and edge['completeOutputFacetCount']==3214 and edge['everyOriginalFacetLocalEdgeAccounted']is True
assert q['currentAcceptance']is q['physicalAccepted']is q['installationApproved']is q['publication']is False and q['newlyInstalled']==0
assert len(q['evidenceRefs'])==len({r['path']for r in q['evidenceRefs']})==8824
for p in q['evidenceRefs']:assert sha(R/p['path'])==p['sha256'],p['path']
for p,h in a['inputHashes'].items():assert sha(R/p)==h,p
assert sha(R/account['candidatePath'])==account['candidateSHA256']=='b033b8f2e451d7ce73a6c409d0b855686a7a1b604454a04a8b6a56db118ed647'and sha(R/'3d-viewer/city/data/manifest.json')==CURRENT
assert sha(P/'execution-logs-v1/execution.log')==t['logSHA256']
failures=[r for r in account['ordinary25NeighbourRawGuards']['rows']if r['reasons']];basic={r['uid']for r in failures if r['reasons']==['increased-neighbour-ground-gap']};assert basic=={'landsd/'+str(i)+':0'for i in [63758,72322,89540,258381,258681,258852,198620,305600,305626]};assert len(failures)==10 and any(r['uid']=='landsd/305793:0'and r['reasons']==['existing-native-neighbour-requires-full-mesh-check']for r in failures)
pids=[2662964,2663362,2664259,2664287];assert all(not Path('/proc',str(pid)).exists()for pid in pids);workers=[]
for proc in Path('/proc').iterdir():
 if not proc.name.isdigit():continue
 try:
  argv=(proc/'cmdline').read_bytes().split(b'\0');stat=(proc/'stat').read_text().split(') ',1)[1].split()
  if any(x.endswith(b'/xl-polyu-sports305582-saved-private-candidate-runtime-only-draft-v1-20261013.py')or x==str(L/'reservation.json').encode()for x in argv)or int(stat[2])==2664287:workers.append(int(proc.name))
 except(FileNotFoundError,PermissionError,ProcessLookupError):pass
assert not workers
with connect()as c:
 c.row_factory=dict_row;c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT current_database()AS name').fetchone()['name']=='neondb';actual=c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(JOB,)).fetchone();assert actual['status']=='complete'and actual['result']==q
 groups=c.execute('SELECT token,owner,batch,resources,released_at,heartbeat_at,lease_until,(released_at IS NULL AND lease_until>clock_timestamp())AS active FROM astra_modelling.reservation_groups WHERE batch=%s ORDER BY created_at',(BATCH,)).fetchall();assert len(groups)==2;audits=[]
 for g in groups:
  assert g['released_at']is not None and g['active']is False;rows=c.execute('SELECT resource,token,generation FROM astra_modelling.reservations WHERE token=%s ORDER BY resource',(g['token'],)).fetchall();events=c.execute('SELECT action,actor,token,resources FROM astra_modelling.reservation_events WHERE token=%s AND action=%s',(g['token'],'release')).fetchall();assert len(events)==1 and events[0]['actor']==g['owner']and events[0]['resources']==g['resources'];assert {r['resource']for r in rows}==set(g['resources'])and all(str(r['token'])==str(g['token'])and int(r['generation'])>0 for r in rows)
  if str(g['token'])==lease['token']:assert g['owner']==lease['owner']and g['resources']==lease['resources']and len(g['resources'])==28 and {r['resource']:r['generation']for r in rows}==lease['generations']
  else:assert g['resources']==['source-context:'+BATCH]
  audits.append(dict(group=g,reservationRows=rows,releaseEvents=events))
assert sum(str(g['token'])==lease['token']for g in groups)==1 and sha(R/'3d-viewer/city/data/manifest.json')==CURRENT
result=dict(checkedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),jobId=JOB,exactPinnedNeonCompleteResult=True,result=ref(D/'result.json'),mainDiagnostic=ref(D/'saved-candidate-runtime-only-account.json.gz'),candidate=ref(R/account['candidatePath']),allEvidenceRefHashesVerified=8824,allBeforeEndInputHashesVerified=len(a['inputHashes']),currentManifestSHA256=CURRENT,allCanonical28AndDistinctFreezerReleased=True,reservations=audits,absentRecordedPIDs=pids,noCallerOwnedOrSupervisorOrOwnedGroup=True,terminal=ref(P/'execution-logs-v1/terminal.json'),auditor=ref(CODE),outputFacets=3214,all9642FacetEdgeIncidentsAccounted=True,actualMAXSamplerSamples=6701,actualMAXSamplerAllPass=True,unchangedRawValidatorPass=True,ordinaryNeighbourGuardsPass=False,allNineBasicFailuresAndHeldCampusVerbatim=failures,currentAcceptance=False,physicalAccepted=False,newlyInstalled=0,noProducerOrProofReplay=True)
with(O/'audit.json').open('x')as f:json.dump(result,f,sort_keys=True,indent=2,default=str);f.write('\n')
print(json.dumps(dict(jobId=JOB,resultSHA256=sha(D/'result.json'),diagnosticSHA256=sha(D/'saved-candidate-runtime-only-account.json.gz'),refs=8824,inputPins=len(a['inputHashes']),releasedGroups=len(groups),noPIDs=True,auditor=ref(CODE),audit=ref(O/'audit.json'),releasedAt=[str(g['released_at'])for g in groups])))
