from pathlib import Path
import sys,hashlib,json,shutil
R=Path('/home/williamli/projects/wiiiimm/hongkong-sandbox/.claude/worktrees/astra-hong-kong-city');H=R/'source-scripts/city/government-import';sys.path.insert(0,str(H))
from run import read,save,connect
b='government-xl-upton-whole-parent-original-tin-regression-v2-20261012';D=R/'docs/astra-city/government-import'/b;L=H/'local'/b
pin=lambda p:dict(path=str(p.relative_to(R)),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
r=read(D/'result.json');assert r['batch']==b and r['sourceOnly']is True and r['physicalAccepted']is False and r['newlyInstalled']==0 and r['installationApproved']is False and r['newTerrainJoinConstructed']is False
for ref in r['evidenceRefs']:assert pin(R/ref['path'])==ref,ref
lease=read(L/'reservation.json')
with connect()as c:
 c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 owner,resources,released,active=c.execute('SELECT owner,resources,released_at,(released_at IS NULL AND lease_until>clock_timestamp()) FROM astra_modelling.reservation_groups WHERE token=%s',(lease['token'],)).fetchone();assert owner==lease['owner']and len(resources)==11 and released is not None and active is False
manifest=pin(R/'3d-viewer/city/data/manifest.json');assert manifest['sha256']=='2dde0cfc3c0869963c185c3398e48a1928c76802b2efa6c2d9713183a6ad5540'
caller=pin(H/'upton_whole_parent_original_tin_regression_draft_v2_20261012.py');assert caller['sha256']=='d316ca491e61931ddc3d415d5ba05e03384f762a7f17a6d20a6c154069c96662'
d=read(D/'diagnostic.json.gz');assert d['wholeSourceTINFacets']==122721 and d['wholeCurrentDrawnGroundFacets']==9214 and len(d['actors'])==4 and len(d['completeBasicRows'])==1911
assert d['wholeCurrentDrawnGroundSHA256']=='b4916dac0a7c911a5b20e7dde729fa9a99fca63fa01896db8380523e6158670a'
fields=['currentUnprovedOriginalTINClear','currentClearOriginalTINUnproved','currentUncovered','sourceTINUncovered','bothOrdinaryUnproved']
def summary(w):
 q=w['allWholeFacetComparisons'];rows=q['rows'];return dict(mode=w['mode'],completeFaces=w['completeFaces'],selectedComparisons=len(rows),wholeWorldSHA256=w['wholeWorldSHA256'],sourceROISHA256=w['wholeOriginalROISHA256'],exactFullTupleReuse=w['exactFullTupleReuse'],currentOrdinaryProved=sum(x['current']['ordinaryBoundProved']for x in rows),originalTINOrdinaryProved=sum(x['originalTIN']['ordinaryBoundProved']for x in rows),currentBurialOrUnprovedCovered=sum(x['current']['projectionCovered']and not x['current']['ordinaryBoundProved']for x in rows),originalTINBurialOrUnprovedCovered=sum(x['originalTIN']['projectionCovered']and not x['originalTIN']['ordinaryBoundProved']for x in rows),currentOutsideCaptureExtractionLimits=sum(x['comparison']['currentUncoveredOutsideCapturedDomainIsNotRuntimeGap']for x in rows),**{k:dict(count=len(q[k]),completeFaceIDs=q[k])for k in fields})
actors=[dict(uid=a['uid'],role=a['role'],worlds=[summary(w)for w in a['worlds']])for a in d['actors']]
assert sum(a['worlds'][0]['completeFaces']for a in d['actors'][:3])==13704
basic=[dict(uid=a['uid'],completeFaces=a['completeFacets'],selectedFaces=len(a['scope']['selectedFaceIDs']),outsideFaces=len(a['scope']['strictClosedBoundsDisjointFaceIDs']),world=summary(a['affectedComparisons']['worlds'][0])if 'affectedComparisons'in a else None)for a in d['completeBasicRows']]
assert all(x['completeFaces']==x['selectedFaces']+x['outsideFaces']for x in basic)
s=dict(passed=True,jobId=r['jobId'],result=pin(D/'result.json'),verifiedEvidenceRefs=len(r['evidenceRefs']),currentManifest=manifest,caller=caller,canonicalReservation=dict(token=lease['token'],owner=owner,resourceCount=len(resources),resources=resources,releasedAt=str(released),active=False),sourceTINCompleteFacets=122721,currentCompleteGroundFacets=9214,actors=actors,completeBasicRows=1911,affectedBasicRows=sum(bool(x['selectedFaces'])for x in basic),completeBasicSelectedFacets=sum(x['selectedFaces']for x in basic),completeBasicOutsideFacets=sum(x['outsideFaces']for x in basic),basicRegressions=[x for x in basic if x['world']and any(x['world'][k]['count']for k in fields)],sourceOnly=True,noPhysicalGradeRootRoleOrInstallationCredit=True)
save(D/'independent-completed-readback-summary.json',s)
shutil.copyfile('/tmp/upton-whole-parent-original-tin-regression-v2-20261012.log',D/'actual-supervisor-terminal-exit0.log')
save(D/'independent-terminal-readback-pins.json',dict(summary=pin(D/'independent-completed-readback-summary.json'),log=pin(D/'actual-supervisor-terminal-exit0.log'),result=pin(D/'result.json'),diagnostic=pin(D/'diagnostic.json.gz')))
print(json.dumps(dict(jobId=r['jobId'],resultSHA256=s['result']['sha256'],verifiedEvidenceRefs=len(r['evidenceRefs']),released=s['canonicalReservation'],actors=[dict(uid=a['uid'],worlds=[{k:v for k,v in w.items()if k not in fields}|{k:w[k]['count']for k in fields}for w in a['worlds']])for a in actors],affectedBasicRows=s['affectedBasicRows'],basicSelectedFacets=s['completeBasicSelectedFacets'],basicOutsideFacets=s['completeBasicOutsideFacets'],basicRegressionRows=len(s['basicRegressions']),summary=pin(D/'independent-completed-readback-summary.json')),indent=2))
