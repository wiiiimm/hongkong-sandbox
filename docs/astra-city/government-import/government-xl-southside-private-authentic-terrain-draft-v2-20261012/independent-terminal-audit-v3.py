"""Readonly completed diagnostic/lease audit; writes only a new local audit."""
import collections, gzip, hashlib, json, os, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
HERE=ROOT/'source-scripts/city/government-import'
sys.path.insert(0,str(HERE))
from run import connect
BATCH='government-xl-southside-315025-300867-private-authentic-terrain-diagnostic-v3-20261012'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
LOCAL=HERE/'local'/BATCH
JOB='1be4acb6a5e52787ecc57dd7806df25dc4d5281fa6e94b6858a5ea2c14b2cfae'
CURRENT='2dde0cfc3c0869963c185c3398e48a1928c76802b2efa6c2d9713183a6ad5540'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def load(p):
 return json.load(gzip.open(p,'rt')if p.suffix=='.gz'else p.open())
def pin(p):return dict(path=str(p.relative_to(ROOT)),sha256=sha(p),bytes=p.stat().st_size)
result=load(DOC/'result.json');lease=load(LOCAL/'reservation.json')
assert result['jobId']==JOB and result['batch']==BATCH
assert len(lease['resources'])==124 and lease['token']=='b0b13f7b-914b-4690-a923-3c7b6f84956c'
assert len(set(lease['resources']))==124 and set(lease['generations'])==set(lease['resources'])
refs=result['evidenceRefs']
for ref in refs:assert sha(ROOT/ref['path'])==ref['sha256'],ref['path']
assert sha(ROOT/'3d-viewer/city/data/manifest.json')==CURRENT
with connect()as c:
 c.execute('SET TRANSACTION READ ONLY')
 assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(JOB,)).fetchone()==('complete',result)
 group=c.execute('SELECT owner,batch,resources,released_at,(released_at IS NULL AND lease_until>clock_timestamp()) FROM astra_modelling.reservation_groups WHERE token=%s',(lease['token'],)).fetchone()
 assert group and group[:3]==(lease['owner'],BATCH,lease['resources'])and group[3]is not None and group[4]is False
 rows=c.execute('SELECT resource,token,generation FROM astra_modelling.reservations WHERE resource=ANY(%s) ORDER BY resource',(lease['resources'],)).fetchall()
 assert len(rows)==124 and {r[0]:r[2]for r in rows}==lease['generations']and all(str(r[1])==lease['token']for r in rows)
 events=c.execute('SELECT id,occurred_at,action,actor,resources FROM astra_modelling.reservation_events WHERE token=%s ORDER BY id',(lease['token'],)).fetchall()
 releases=[e for e in events if e[2]=='release'];assert len(releases)==1
 assert releases[0][3:]==(lease['owner'],lease['resources'])
known=[4139705,4146273,4146343]
assert all(not Path('/proc',str(pid)).exists()for pid in known)
matching=[];group_members=[]
for p in Path('/proc').iterdir():
 if not p.name.isdigit():continue
 try:
  cmd=(p/'cmdline').read_bytes().split(b'\0');stat=(p/'stat').read_text();tail=stat[stat.rfind(')')+2:].split()
 except(FileNotFoundError,ProcessLookupError,PermissionError):continue
 if int(tail[2])==4146343:group_members.append(int(p.name))
 if any(x.decode(errors='replace').endswith('xl-southside-315025-300867-private-authentic-terrain-diagnostic-v3-20261012.py')for x in cmd):matching.append(int(p.name))
assert not matching and not group_members
full=load(DOC/'source-terrain-inventory-and-proposal-account.json.gz');a=full['account']
assert a['completeInputFacets']==774477 and a['completeInputSHA256']=='7f4a1b2e43b38c2512cd3f5d44e256b36af1cab07d1e2b37d39db4a7e9da9b66'
candidate=ROOT/a['privateCandidatePath'];assert sha(candidate)==a['privateCandidateSHA256']
assert result['currentAcceptance']is False and result['newlyInstalled']==0
assert all(full[k]is False for k in ['sourceRoleAccepted','currentAcceptance','physicalAccepted','installationApproved'])
log=Path(__file__).parent/'execution-logs/supervised-private-construction-v3.log'
text=log.read_text();assert '"exitCode": 0'in text and '"released": true'in text and JOB in text
out=dict(schema='southside-independent-terminal-audit-v3',jobId=JOB,pinnedNeonExactCompleteResult=True,everyEvidenceReferenceHashMatches=True,evidenceReferenceVersions=len(refs),uniqueEvidencePaths=len({r['path']for r in refs}),currentManifestSHA256=CURRENT,currentManifestUnchanged=True,canonicalResources=124,exactResourceGenerationsMatch=True,leaseToken=lease['token'],leaseOwner=lease['owner'],releasedAt=str(group[3]),ownsFalse=True,releaseEvent=dict(id=releases[0][0],occurredAt=str(releases[0][1]),action=releases[0][2]),knownProcessesAbsent=known,ownedProcessGroupAbsent=True,matchingProducerProcesses=[],artifacts=[pin(p)for p in [DOC/'result.json',DOC/'source-terrain-inventory-and-proposal-account.json.gz',candidate,log,Path(__file__)]],completeInputFacets=774477,selectedOriginalFacets=len(a['completeSelectedOriginalFacetAccounts']),outsideOriginalFacets=len(a['allOutsideAlteredDomainOriginalFacetIds']),exactZeroOriginalFacets=len(a['exactZeroOriginalFacetIds']),verticalRealOriginalFacets=len(a['allVerticalRealOriginalFacetIds']),boundaryTouchOriginalFacets=len(a['allBoundaryTouchOnlyOriginalFacetIds']),outputFacets=len(a['completeOutputFacetLineage']),outputClassificationCounts=dict(collections.Counter(x['classification']for x in a['completeOutputFacetLineage'])),realPackedCollapses=len(a['realOutputFacetsCollapsedByFloat32']),sourceCorePackingChanges=len(a['sourceCoreOutputsChangedByFloat32Packing']),wholeAlteredDomainBounds=a['wholeAlteredDomainAllPackedAndUnusedGridBounds'],triangleBudget=a['triangleBudget'],triangleBudgetPass=a['triangleBudgetPass'],ordinaryPatchValidatorDiagnostic=a['ordinaryPatchValidatorDiagnostic'],completeFiniteSeamCoverageAndSamplerQualificationPending=True,currentAcceptance=False,newlyInstalled=0)
target=Path(__file__).parent/'independent-terminal-audit-v3.json'
with target.open('x')as f:json.dump(out,f,indent=2,sort_keys=True);f.write('\n')
print(json.dumps(dict(audit=pin(target),**{k:out[k]for k in ['jobId','evidenceReferenceVersions','releasedAt','outputFacets','outputClassificationCounts','triangleBudgetPass','ordinaryPatchValidatorDiagnostic']})),flush=True)
