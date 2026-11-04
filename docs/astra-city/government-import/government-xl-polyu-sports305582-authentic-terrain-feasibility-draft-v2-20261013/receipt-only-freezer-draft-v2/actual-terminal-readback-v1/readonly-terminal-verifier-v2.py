from pathlib import Path
import hashlib,json,sys,datetime
R=Path('/home/williamli/projects/wiiiimm/hongkong-sandbox/.claude/worktrees/astra-hong-kong-city');H=R/'source-scripts/city/government-import';sys.path.insert(0,str(H));from run import connect,dict_row
D=R/'docs/astra-city/government-import/government-xl-polyu-sports305582-authentic-terrain-feasibility-draft-v2-20261013/receipt-only-freezer-draft-v2';O=D/'actual-terminal-readback-v1';assert O.is_dir();(O/'readonly-terminal-verifier-v2.py').write_bytes(Path(__file__).read_bytes());BATCH='government-xl-polyu-sports305582-authentic-terrain-feasibility-source-context-v2-20261013';P=R/'docs/astra-city/government-import'/BATCH/'result.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ref(p):return dict(path=str(p.relative_to(R)),sha256=sha(p))
def read(p):return json.loads(p.read_bytes())
q=read(P);t=read(D/'execution-logs-freeze-v1/terminal.json');v=read(D/'actual-readonly-preparation-v1/validation.json');assert t['exitCode']==0 and t['allLiteralPinsUnchanged']and t['beforeEndPinCount']==7574 and v['allPassed']
assert t['wrapperPID']==2237378 and t['producerPID']==2237429 and not Path('/proc/2237378').exists()and not Path('/proc/2237429').exists()
for pin in v['beforeEndLiteralPins']+v['transitiveImportedCodePins']:assert sha(R/pin['path'])==pin['sha256'],pin['path']
assert len({pin['path']for pin in q['evidenceRefs']})==len(q['evidenceRefs'])
for pin in q['evidenceRefs']:assert sha(R/pin['path'])==pin['sha256'],pin['path']
assert q['batch']==BATCH and q['currentAcceptance']is False and q['physicalAccepted']is False and q['identityAccepted']is False and q['sourceRoleAccepted']is False and q['publication']is False and q['installationApproved']is False and q['newlyInstalled']==q['modelGeometryChanges']==q['terrainGeometryChanges']==0
assert sha(R/'3d-viewer/city/data/manifest.json')==t['currentManifestSHA256']=='c00fd9f731b1bcbf4d2df6067a5cb3231f0eaa8c503a8adea584fec39bf73bf7'
with connect()as c:
 c.row_factory=dict_row;c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT current_database() AS name').fetchone()['name']=='neondb'
 actual=c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(q['jobId'],)).fetchone();assert actual['status']=='complete'and actual['result']==q
 groups=c.execute('SELECT token,owner,batch,resources,released_at,(released_at IS NULL AND lease_until>clock_timestamp()) AS active FROM astra_modelling.reservation_groups WHERE batch=%s',(BATCH,)).fetchall();assert len(groups)==1;g=groups[0]
 assert g['resources']==['source-context:'+BATCH]and g['released_at']is not None and g['active']is False
 rows=c.execute('SELECT resource,token,generation FROM astra_modelling.reservations WHERE token=%s ORDER BY resource',(g['token'],)).fetchall();assert len(rows)==1 and rows[0]['resource']==g['resources'][0]and str(rows[0]['token'])==str(g['token'])and int(rows[0]['generation'])>0
 events=c.execute('SELECT action,actor,token,resources FROM astra_modelling.reservation_events WHERE token=%s AND action=%s',(g['token'],'release')).fetchall();assert len(events)==1 and events[0]['actor']==g['owner']and events[0]['resources']==g['resources']
audit=dict(checkedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),exactPinnedNeonCompleteResult=True,jobId=q['jobId'],result=ref(P),allEvidenceRefHashesVerified=len(q['evidenceRefs']),allPreparationInputHashesRetained=True,currentManifestSHA256=t['currentManifestSHA256'],sourceContextGroup=g,reservationRows=rows,releaseEvents=events,activeFalse=True,currentResourceGenerationRecordedNotClaimTimeSnapshot=True,wrapperAndProducerAbsent=True,terminal=ref(D/'execution-logs-freeze-v1/terminal.json'),auditor=ref(O/'readonly-terminal-verifier-v2.py'),noModelReviewWrites=True,noAcceptanceOrPublication=True,noNumericalReplay=True)
with(O/'audit.json').open('x')as f:json.dump(audit,f,sort_keys=True,indent=2,default=str);f.write('\n')
print(json.dumps(dict(jobId=q['jobId'],resultSHA256=sha(P),refs=len(q['evidenceRefs']),releasedToken=str(g['token']),releasedAt=str(g['released_at']),active=False,noPIDs=True,audit=ref(O/'audit.json'),auditor=ref(O/'readonly-terminal-verifier-v2.py'))))
