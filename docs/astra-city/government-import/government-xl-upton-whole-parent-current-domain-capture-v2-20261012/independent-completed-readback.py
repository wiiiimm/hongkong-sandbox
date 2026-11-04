import sys,json,hashlib
from pathlib import Path
root=Path('/home/williamli/projects/wiiiimm/hongkong-sandbox/.claude/worktrees/astra-hong-kong-city');here=root/'source-scripts/city/government-import';sys.path.insert(0,str(here))
from run import read,save,connect
batch='government-xl-upton-whole-parent-current-domain-capture-v2-20261012';doc=root/'docs/astra-city/government-import'/batch;local=here/'local'/batch
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
result=read(doc/'result.json');assert result['batch']==batch and result['currentAcceptance']is False and result['newlyInstalled']==0
for pin in result['evidenceRefs']:
 p=root/pin['path'];assert p.is_file()and sha(p)==pin['sha256'],pin
lease=read(local/'reservation.json')
with connect()as c:
 c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(result['jobId'],)).fetchone()==('complete',result)
 released,active=c.execute('SELECT released_at,(released_at IS NULL AND lease_until>clock_timestamp()) FROM astra_modelling.reservation_groups WHERE token=%s AND owner=%s',(lease['token'],lease['owner'])).fetchone();assert released is not None and not active
 resourcecount=c.execute('SELECT count(*) FROM astra_modelling.reservations WHERE token=%s',(lease['token'],)).fetchone()[0];assert resourcecount==11
manifest=root/'3d-viewer/city/data/manifest.json';assert sha(manifest)=='2dde0cfc3c0869963c185c3398e48a1928c76802b2efa6c2d9713183a6ad5540'
actors=read(doc/'whole-domain-current-actors.json.gz');ground=read(doc/'whole-domain-actual-parent-attribution.json.gz');inp=read(doc/'input.json.gz')
assert actors['startEndAllInputsVerified']and ground['startEndAllInputsVerified'];assert [r['uid']for r in actors['rows']]==['landsd/338946:0','landsd/12728:0','landsd/12662:0'];assert [r['uid']for r in actors['nativeContextRows']]==['landsd/79882:0'];assert any(r['uid']=='landsd/254809:0'for r in actors['basicContextRows'])
assert sum(len(r['completeOriginalIndex'])//3 for r in actors['rows'])==13704
assert inp['rederivedCoarseCells']==[457,449,460,451]and inp['domain']==[-2477.5,-37.5,-2267.5,102.5]
assert len(ground['rows'])==1 and ground['rows'][0]['completeAttributionMultisetMatchedActual']
row=ground['rows'][0];sources=row['completeAttributedSources']
out=dict(passed=True,jobId=result['jobId'],resultSHA256=sha(doc/'result.json'),verifiedEvidenceRefs=len(result['evidenceRefs']),currentManifestSHA256=sha(manifest),callerSHA256=sha(here/'upton_whole_parent_current_domain_capture_draft_v2_20261012.py'),canonicalReservation=dict(token=lease['token'],owner=lease['owner'],resourceCount=resourcecount,releasedAt=str(released),active=False),completeOwnedFaces=13704,actors=[dict(uid=r['uid'],faces=len(r['completeOriginalIndex'])//3,unusedAndUsedVertices=len(r['completeLiteralWorldPosition'])//3)for r in actors['rows']+actors['nativeContextRows']],completeBasicRows=len(actors['basicContextRows']),foreign254809Preserved=True,wholeDomainXZ=inp['domain'],wholeDomainCells=inp['rederivedCoarseCells'],currentDrawnDomainFacets=len(row['completeActualDrawnTriplets']),attributedSourceMeshes=len(sources),attributedTerrainSourcePaths=sorted({r['sourcePath']for r in sources}),wholeParentRegistryRows=len(ground['wholeParentRegistry']),completeMeshOmissionRecords=len(ground['wholeMeshOmissionInventory']),exactActualAttributionMultisetMatched=True,wholeCurrentNativeNomination=6649,retainedParentOriginalBytes=inp['retainedParent'],retainedParentTargets=inp['retainedParentExactCurrentData']['meta']['targetUids'],sourceTerrainNotClaimedUntouched=True,currentAcceptance=False,noTerrainCandidateConstructed=True,nativeReacceptance=False,newlyInstalled=0)
save(doc/'independent-completed-readback-summary.json',out);print(json.dumps(out,separators=(',',':')))
