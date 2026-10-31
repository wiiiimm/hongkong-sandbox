"""Readonly pinned receipt/reference/group audit; writes only a new local audit."""
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT/'source-scripts/city/government-import'))
from run import connect
BATCH='government-xl-southside-saved-layer-cause-receipt-only-freeze-v1-20261012'
JOB='f1d0c0a639249884387382e7c05e1d48746404063e4fe6ea7716466bd96a2be8'
CURRENT='2dde0cfc3c0869963c185c3398e48a1928c76802b2efa6c2d9713183a6ad5540'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
q=json.loads((DOC/'result.json').read_bytes());assert q['jobId']==JOB and q['positiveOriginalPairs']==6239 and q['packingOnlyPairs']==12 and q['currentAcceptance']is False and q['physicalAccepted']is False
for pin in q['evidenceRefs']:assert sha(ROOT/pin['path'])==pin['sha256'],pin['path']
assert sha(ROOT/'3d-viewer/city/data/manifest.json')==CURRENT
with connect()as c:
 c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(JOB,)).fetchone()==('complete',q)
 groups=c.execute('SELECT token,owner,resources,released_at,(released_at IS NULL AND lease_until>clock_timestamp()) FROM astra_modelling.reservation_groups WHERE batch=%s',(BATCH,)).fetchall();assert len(groups)==1
 token,owner,resources,released,active=groups[0];assert released is not None and active is False and resources==['source-context:'+BATCH]
 events=c.execute('SELECT id,occurred_at,action,actor,resources FROM astra_modelling.reservation_events WHERE token=%s ORDER BY id',(token,)).fetchall();r=[e for e in events if e[2]=='release'];assert len(r)==1 and r[0][3:]==(owner,resources)
 rows=c.execute('SELECT resource,token,generation,(lease_until>clock_timestamp()) FROM astra_modelling.reservations WHERE resource=ANY(%s)',(resources,)).fetchall();assert len(rows)==1 and str(rows[0][1])==str(token)and rows[0][3]is False
 old=c.execute('SELECT released_at,(released_at IS NULL AND lease_until>clock_timestamp()) FROM astra_modelling.reservation_groups WHERE token=%s',('b0b13f7b-914b-4690-a923-3c7b6f84956c',)).fetchone();assert old[0]is not None and old[1]is False
matches=[]
for p in Path('/proc').iterdir():
 if not p.name.isdigit():continue
 try:cmd=(p/'cmdline').read_bytes().split(b'\0')
 except(FileNotFoundError,ProcessLookupError,PermissionError):continue
 if any(x.decode(errors='replace').endswith('xl-southside-saved-layer-cause-receipt-only-freeze-draft-v1-20261012.py')for x in cmd):matches.append(int(p.name))
assert not matches and all(not Path('/proc',str(p)).exists()for p in [4139705,4146273,4146343,119538,119531])
out=dict(jobId=JOB,resultSHA256=sha(DOC/'result.json'),exactPinnedNeonComplete=True,everyReferenceSHA256Matches=True,evidenceReferenceVersions=len(q['evidenceRefs']),positiveOriginalPairs=6239,packingOnlyPairs=12,positivePackedPairs=6251,releaseToken=str(token),releaseOwner=owner,releasedAt=str(released),releaseEventId=r[0][0],releaseEventTime=str(r[0][1]),resourceGeneration=rows[0][2],ownsFalse=True,prior124GroupReleasedAt=str(old[0]),producerProcesses=[],currentManifestSHA256=CURRENT,noNumericalReplay=True,noNewTerrain=True,currentAcceptance=False,physicalAccepted=False)
target=Path(__file__).with_suffix('.json')
with target.open('x')as f:json.dump(out,f,sort_keys=True,indent=2);f.write('\n')
print(json.dumps(dict(**out,auditPath=str(target.relative_to(ROOT)),auditSHA256=sha(target))),flush=True)
