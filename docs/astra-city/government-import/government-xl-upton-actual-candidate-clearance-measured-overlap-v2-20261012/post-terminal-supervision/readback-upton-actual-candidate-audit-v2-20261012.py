"""Terminal-only independent receipt/hash/release/PID audit; no proof math."""
from pathlib import Path
import hashlib,json,gzip,sys,subprocess
r=Path.cwd();h=r/'source-scripts/city/government-import';sys.path.insert(0,str(h));from run import connect
batch='government-xl-upton-actual-candidate-clearance-measured-overlap-v2-20261012';d=r/'docs/astra-city/government-import'/batch;local=h/'local'/batch
terminal=json.loads(Path('/tmp/upton-approved-actual-candidate-audit-v2-terminal-20261012.json').read_text());assert terminal['exitCode']==0
def load(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b)if p.suffix=='.gz'else b)
def hashfile(p):
 q=hashlib.sha256()
 with p.open('rb')as f:
  while(b:=f.read(1024*1024)):q.update(b)
 return q.hexdigest()
def ref(p):return dict(path=str(p.relative_to(r)),sha256=hashfile(p))
receipt=load(d/'result.json');assert receipt['batch']==batch and receipt['stage']=='private-actual-candidate-ordinary-clearance-measured-overlap-only'and receipt['uids']==['landsd/338946:0','landsd/12728:0','landsd/12662:0','landsd/79882:0']and receipt['completeOwnedFaces']==13704 and receipt['newlyInstalled']==0 and not receipt['physicalAccepted']and not receipt['installationApproved']
lease=load(local/'reservation.json')
with connect()as c:
 c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 group=c.execute('SELECT released_at,(released_at IS NULL AND lease_until>clock_timestamp()) FROM astra_modelling.reservation_groups WHERE token=%s AND owner=%s',(lease['token'],lease['owner'])).fetchone();assert group and group[0]is not None and group[1]is False
 groups=c.execute('SELECT token,owner,released_at,(released_at IS NULL AND lease_until>clock_timestamp()) FROM astra_modelling.reservation_groups WHERE batch=%s',(batch,)).fetchall();assert groups and all(q[2]is not None and q[3]is False for q in groups)
amount=0
for i,q in enumerate(receipt['evidenceRefs']):
 p=r/q['path'];assert hashfile(p)==q['sha256'],q
 if 'bytes'in q:assert p.stat().st_size==q['bytes']
 amount+=p.stat().st_size
 if (i+1)%256==0:print(json.dumps(dict(verified=i+1,totalRefs=len(receipt['evidenceRefs']),bytes=amount)),flush=True)
manifest=r/'3d-viewer/city/data/manifest.json';assert hashfile(manifest)=='2dde0cfc3c0869963c185c3398e48a1928c76802b2efa6c2d9713183a6ad5540'
known=[3490345,3490361,3490801,3490804,3490846,3498496];lines=subprocess.check_output(['ps','-eo','pid=,ppid=,args='],text=True).splitlines();assert not[q for q in lines if int(q.split()[0])in known]
caller=str(h/'upton_actual_candidate_clearance_audit_draft_v2_20261012.py');runtime=str(h/'upton_actual_candidate_clearance_audit_runtime_draft_v1_20261012.mjs');leasepath=str(local/'reservation.json');assert not[q for q in lines if caller in q.split()[2:]or runtime in q.split()[2:]or leasepath in q.split()[2:]]
clearance=load(d/'complete-candidate-clearance.json.gz');measure=load(d/'measured-projection-and-parent-edge.json.gz');rays=load(d/'actual-native-sampler-ray-findings.json.gz');seams=load(d/'complete-core-boundary-fixed-band-findings.json.gz');validator=load(d/'real-validator-outcome.json')
actors=[]
for a in clearance['actors']:
 actors.append(dict(uid=a['uid'],worlds=[dict(mode=w['mode'],completeFaces=w['completeFaces'],checkedFaces=len(w['selectedFaceIDs']),candidateCoverageUnproved=w['findings']['candidateUncovered'],candidateOrdinaryUnproved=w['findings']['candidateOrdinaryUnproved'],beforeClearCandidateUnproved=w['findings']['currentClearCandidateUnproved'],beforeUnprovedCandidateClear=w['findings']['currentUnprovedCandidateClear'],sameCompleteTupleReuse=w['sameCompleteTupleReuse'])for w in a['worlds']]))
basic=[]
for a in clearance['completeBasicRows']:
 if 'findings'in a:
  w=a['findings']['worlds'][0];basic.append(dict(uid=a['uid'],checkedFaces=len(w['selectedFaceIDs']),candidateUncovered=w['findings']['candidateUncovered'],candidateOrdinaryUnproved=w['findings']['candidateOrdinaryUnproved'],beforeClearCandidateUnproved=w['findings']['currentClearCandidateUnproved'],beforeUnprovedCandidateClear=w['findings']['currentUnprovedCandidateClear'],outsideDomainExtractionLimitFaceIDs=[q['face']for q in w['findings']['rows']if q['comparison']['candidateCoverageUnprovedOutsideCapturedDomainIsExtractionLimit']]))
summary=dict(jobId=receipt['jobId'],status='complete',result=ref(d/'result.json'),allEvidenceRefsVerified=len(receipt['evidenceRefs']),allReferenceBytes=amount,currentManifest=ref(manifest),canonicalElevenResources=lease['resources'],canonicalToken=lease['token'],canonicalOwner=lease['owner'],canonicalReleasedAt=str(group[0]),allBatchReservationGroupsReleased=[dict(token=str(q[0]),owner=q[1],releasedAt=str(q[2]))for q in groups],knownProducerPIDsGone=known,noRemainingExactCallerRuntimeHeartbeatArguments=True,actors=actors,completeBasicRows=len(clearance['completeBasicRows']),affectedBasic=basic,selectedBasicFaces=sum(q['checkedFaces']for q in basic),totalBasicBeforeClearCandidateUnproved=sum(len(q['beforeClearCandidateUnproved'])for q in basic),measurement={k:measure[k]for k in ['nativeProjectedExcessM2','missingInsideParentM2','outsideParentM2','symmetricCoverageDifferenceM2','validatorToleranceM2','pairsBySavedProvenanceKinds','parentEdgeMaximumGap','parentEdgeExistingLimitM']},actualProductionRaySamples=rays['samples'],actualProductionRayMaxError=rays['maxError'],actualProductionRayFailures=rays['failedRows'],completeCoreBoundarySegments=seams['completeSegments'],coreBoundaryFixedBandFailures=[q['savedBoundary']for q in seams['rows']if not q['actualCandidateGroundProof']['verifiedCompleteOriginalEdgeContactBand']],coreBoundaryCoverageFailures=[q['savedBoundary']for q in seams['rows']if not q['actualCandidateGroundProof']['completeFiniteCoverage']],fixedBandNotExactSeamCredit=True,unchangedRealValidator=validator,noApprovalWritten=True,sourceGeometryChanges=0,liveTerrainChanges=0,installationApproved=False,proofOutputs=[ref(p)for p in sorted(d.iterdir())if p.is_file()])
f=d/'independent-completed-readback-summary.json';assert not f.exists();f.write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n');print(json.dumps({'jobId':receipt['jobId'],'result':ref(d/'result.json'),'allEvidenceRefsVerified':len(receipt['evidenceRefs']),'allReferenceBytes':amount,'releasedEleven':len(lease['resources'])==11,'summary':ref(f),'actorModeCounts':[{**a,'worlds':[{**w,'candidateCoverageUnproved':len(w['candidateCoverageUnproved']),'candidateOrdinaryUnproved':len(w['candidateOrdinaryUnproved']),'beforeClearCandidateUnproved':len(w['beforeClearCandidateUnproved']),'beforeUnprovedCandidateClear':len(w['beforeUnprovedCandidateClear'])}for w in a['worlds']]}for a in actors],'basicBeforeClearCandidateUnproved':summary['totalBasicBeforeClearCandidateUnproved'],'realValidator':validator,'fixedBandFailures':len(summary['coreBoundaryFixedBandFailures']),'fixedBandCoverageFailures':len(summary['coreBoundaryCoverageFailures'])},indent=2),flush=True)
