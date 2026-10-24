import sys,json,hashlib,os
from pathlib import Path
R=Path('/home/williamli/projects/wiiiimm/hongkong-sandbox/.claude/worktrees/astra-hong-kong-city');H=R/'source-scripts/city/government-import';sys.path.insert(0,str(H))
from run import read,digest,connect,dict_row
B='government-xl-polyu-sports305582-current-four-world-ground-capture-v1-20261013';D=R/'docs/astra-city/government-import'/B;P=R/'docs/astra-city/government-import/government-xl-polyu-sports305582-current-four-world-ground-draft-v1-20261013';CURRENT='c00fd9f731b1bcbf4d2df6067a5cb3231f0eaa8c503a8adea584fec39bf73bf7'
r=read(D/'result.json');lease=read(H/'local'/B/'reservation.json');terminal=read(P/'execution-logs-capture-v1/terminal.json');assert terminal['exitCode']==0
with connect()as c:
 c.row_factory=dict_row;c.execute('SET TRANSACTION READ ONLY')
 j=c.execute('SELECT id,status,result,owner,token,lease_until FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone();assert j['status']=='complete'and j['result']==r and j['owner']is None and j['token']is None and j['lease_until']is None
 groups=c.execute('SELECT token,owner,resources,released_at,(released_at IS NULL AND lease_until>clock_timestamp())AS active FROM astra_modelling.reservation_groups WHERE batch=%s',(B,)).fetchall();assert len(groups)==2 and all(g['released_at']is not None and not g['active']for g in groups)
 canonical,=[g for g in groups if str(g['token'])==lease['token']];assert canonical['resources']==lease['resources']and canonical['owner']==lease['owner']
 rows=c.execute('SELECT resource,token,generation FROM astra_modelling.reservations WHERE resource=ANY(%s)',(lease['resources'],)).fetchall();assert len(rows)==13 and all(str(z['token'])==lease['token']and z['generation']==lease['generations'][z['resource']]for z in rows)
 freezer,=[g for g in groups if str(g['token'])!=lease['token']];assert freezer['resources']==['source-context:'+B]
 events=c.execute("SELECT action,actor,token,resources FROM astra_modelling.reservation_events WHERE token=ANY(%s)AND action='release'",([g['token']for g in groups],)).fetchall();assert len(events)==2 and all(any(str(e['token'])==str(g['token'])and e['actor']==g['owner']and e['resources']==g['resources']for e in events)for g in groups)
refs=r['evidenceRefs'];assert len(refs)==len({x['path']for x in refs})
for x in refs:assert digest((R/x['path']).read_bytes())==x['sha256'],x['path']
for x in read(P/'review-file-pins.json')['filePins']:assert digest((R/x['path']).read_bytes())==x['sha256'],x['path']
cap=read(D/'complete-current-actual-source-and-ground-305582-0.json.gz');worlds=read(D/'complete-sports-four-stream-current-ground-inputs.json.gz')
for p,h in cap['inputHashes'].items():assert digest((R/p).read_bytes())==h,p
assert digest((R/'3d-viewer/city/data/manifest.json').read_bytes())==CURRENT and cap['startAndEndInputsVerified']is True
assert all(x['completeFaces']==10536 for x in worlds['completeWorldStreams'].values())and len(worlds['completeWorldStreams'])==4
survivors=[]
for q in Path('/proc').iterdir():
 if not q.name.isdigit():continue
 try:a=(q/'cmdline').read_bytes().split(b'\0')
 except(OSError,PermissionError):continue
 if any(b'xl-polyu-sports305582-current-four-world-ground-'in x for x in a if x.endswith(b'.py')or x.endswith(b'.mjs')):survivors.append(int(q.name))
assert not survivors and all(not(Path('/proc')/str(pid)).exists()for pid in [1824552,1824661])
assert r['currentAcceptance']is False and r['physicalAccepted']is False and r['installationApproved']is False and r['nativePublicationHoldPreserved']is True
out=dict(allPassed=True,jobId=r['jobId'],resultSHA256=digest((D/'result.json').read_bytes()),evidenceRefVersions=len(refs),completeSourceFaces=10536,completeWorldModes=list(worlds['completeWorldStreams']),originalBodies=21,originalZeroFaces=4,currentGroundFaces=cap['currentDrawnGround']['completeRegionalFaces'],canonicalResources=13,groupsReleased=[dict(token=str(g['token']),owner=g['owner'],resources=len(g['resources']),releasedAt=str(g['released_at']),ownsFalse=True)for g in groups],releaseEvents=2,noProducerPIDs=True,currentManifestSHA256=CURRENT,currentNativeActors=6650,allReviewedBeforeEndPinsUnchanged=True,currentAcceptance=False,physicalAccepted=False,installedPodiumPublicationFlagPreservedFalse=True,terminal=terminal,preparation=dict(path=str((P/'actual-readonly-preparation-v1/validation.json').relative_to(R)),sha256=digest((P/'actual-readonly-preparation-v1/validation.json').read_bytes())))
A=P/'actual-terminal-readback-v1';A.mkdir();f=A/'audit.json'
with f.open('x')as q:json.dump(out,q,sort_keys=True,indent=2);q.write('\n')
print(json.dumps(dict(**out,auditPath=str(f.relative_to(R)),auditSHA256=digest(f.read_bytes()))))
