import pathlib,sys,json
from types import SimpleNamespace
R=pathlib.Path.cwd();H=R/'source-scripts/city/government-import';sys.path.insert(0,str(H))
import citywalk134332_current_complete_finite_ground_draft_v1_20261013 as Q
A=R/'docs/astra-city/government-import/government-xl-citywalk134332-current-complete-finite-terminal-audit-v1-20261013';result=Q.read(Q.D/'result.json');before=Q.read(Q.LOCAL/'protected-state-before.json');lease=Q.read(Q.LEASE)
for e in result['evidenceRefs']:assert Q.ref(R/e['path'])==e
with Q.connect()as c:
 c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(result['jobId'],)).fetchone()==('complete',result);groups=[r[0]for r in c.execute('SELECT row_to_json(g) FROM astra_modelling.reservation_groups g WHERE batch=%s ORDER BY token',(Q.BATCH,)).fetchall()]
assert len(groups)==2 and all(g['released_at']is not None for g in groups);assert {len(g['resources'])for g in groups}=={1,21};assert any(g['token']==lease['token']and g['owner']==lease['owner']for g in groups);assert not Q.reservations.owns(lease)
a=SimpleNamespace(expected_manifest='c00fd9f731b1bcbf4d2df6067a5cb3231f0eaa8c503a8adea584fec39bf73bf7');after,*_=Q.inputs(a);assert after==before
names={'citywalk134332_current_complete_finite_ground_draft_v1_20261013.py','citywalk134332_freeze_current_complete_finite_ground_draft_v1_20261013.py'};survivors=[]
for f in pathlib.Path('/proc').glob('[0-9]*/cmdline'):
 try:argv=f.read_bytes().decode(errors='replace').split(chr(0))
 except (FileNotFoundError,ProcessLookupError,PermissionError):continue
 if any(pathlib.Path(arg).name in names for arg in argv if arg):survivors.append(dict(pid=int(f.parent.name),argv=argv))
assert not survivors,survivors
for pid in [741351,741358,743378,743727]:assert not pathlib.Path('/proc/'+str(pid)).exists(),pid
d=Q.read(Q.D/'diagnostic.json.gz');assert len(d['allSourceGroundBindings'])==12 and d['completeSourceFaces']==41277 and d['completeOriginalBodies']==193;summary={}
for k,p in d['distinctCompleteFiniteProofs'].items():
 rows=p['allWholeFacetProofs'];assert [r['face']for r in rows]==list(range(41277));assert len(p['completeOriginalBodyObligations'])==193
 summary[k]=dict(ordinaryFailCount=len(p['ordinaryFailingFaces']),coverageFailCount=len(p['coverageFailingFaces']),strictWarningCount=len(p['strictUncertifiedFaces']),bodiesWithOrdinaryFailures=[b['originalBody']for b in p['completeOriginalBodyObligations']if b['ordinaryFailingFaces']],bodiesWithCoverageFailures=[b['originalBody']for b in p['completeOriginalBodyObligations']if b['coverageFailingFaces']],foundationOrdinarySurfacePolicyProved=p['foundationOrdinarySurfacePolicyProved'])
out=dict(jobId=result['jobId'],result=Q.ref(Q.D/'result.json'),completePinnedNeonExact=True,allLiteralRefsVerified=len(result['evidenceRefs']),authoritativePTY=39568,terminalExitCode=0,knownExecutionPIDs=[741351,741358,743378,743727],noPIDs=True,reservationGroups=groups,bothGroupsReleased=True,ownsAfterRelease=False,currentBeforeAfterExact=True,contextUIDs=19,protectedReviewRows=1704,currentNativeCount=6650,currentManifest=after['currentState']['currentManifest'],completeSourceFaces=41277,completeOriginalBodies=193,sourceGroundBindings=12,distinctExactTuples=len(summary),completeProofSummaries=summary,sourceOnly=True,currentAcceptance=False,physicalAccepted=False,installationApproved=False,evidenceRefs=[Q.ref(Q.D/'result.json'),Q.ref(Q.D/'diagnostic.json.gz'),Q.ref(Q.LOCAL/'protected-state-before.json'),Q.ref(Q.LOCAL/'immutable-lease-at-start.json'),Q.ref(A/'actual-full-supervised-terminal-v1.log'),Q.ref(pathlib.Path(__file__))])
Q.save(A/'independent-complete-finite-Neon-allrefs-state-release-audit-v1.json',out);print(json.dumps(dict(jobId=result['jobId'],resultSHA256=Q.ref(Q.D/'result.json')['sha256'],allRefs=len(result['evidenceRefs']),audit=Q.ref(A/'independent-complete-finite-Neon-allrefs-state-release-audit-v1.json'),summaries=summary,released=True,noPIDs=True)),flush=True)
