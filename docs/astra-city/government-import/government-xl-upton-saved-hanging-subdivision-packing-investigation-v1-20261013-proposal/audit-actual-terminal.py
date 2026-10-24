from pathlib import Path
from collections import Counter
import sys,json
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT/'source-scripts/city/government-import'))
import upton_saved_hanging_subdivision_investigation_draft_v1_20261013 as a
P=Path(__file__).parent
receipt=a.read(a.DOC/'result.json');assert receipt['jobId']=='9c99aebc039537788fde09021ce0f7987ae6f21a4d151156d832866eb70e61f1'
refs=receipt['evidenceRefs'];total=0
for q in refs:total+=a.check(q).stat().st_size
pins=a.read(P/'draft-pins.json')
for q in pins['codeRefs']+pins['inputRefs']:a.check(q)
prep=a.read(P/'actual-readonly-preparation.json');a.check(prep['driver']);a.check(prep['fixtureValidation'])
for row in prep['commands']:assert row['exitCode']==0;a.check(row['log'])
with a.connect()as c:
 c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 cursor=c.execute('SELECT token,owner,batch,resources,heartbeat_at,lease_until,released_at FROM astra_modelling.reservation_groups WHERE batch=%s ORDER BY released_at',(a.BATCH,));groups=[dict(zip([d.name for d in cursor.description],row))for row in cursor.fetchall()]
assert len(groups)==2 and all(g['released_at']is not None for g in groups)and sorted(len(g['resources'])for g in groups)==[1,11]
groups=json.loads(json.dumps(groups,default=str));pids=[1906719,1906755,1907419,1907477];assert not any(Path('/proc',str(i)).exists()for i in pids)
assert a.ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==a.prior.prior.CURRENT
out=a.read(a.DOC/'complete-saved-gap-hanging-subdivision-investigation.json.gz');assert len(out['completeSavedFailureRowsVerbatim'])==357 and out['areaRowsStillUnlocated']==257 and len(out['literalWholeCurrentProtectionVerbatim'])==68
counts=Counter();bykind={};eligible_nodes=set();eligible_edges=set();constrained_nodes=set();kinds=Counter()
for row in out['rejectingLongEdgeRows']:
 counts['rejectingLongEdgeRows']+=1;kinds[row['provenanceVerbatim']['kind']]+=1
 for n in row['completeInteriorSubdivisionNodes']:
  counts['interiorProjectedNodeEdgeRelations']+=1
  for key in ['projectedOnlyDifferentHeightLayer','protectedWholeCurrentNodeIncident','protectedIncidentFamilyConstrainedUnresolved','eligibleComputed3DHangingSubdivisionNomination','packedNodeOnLongPackedProjectedEdge']:counts[key]+=bool(n[key])
  if n['exactFinite3DParameter']is not None:counts['exactFinite3DNodeEdgeRelations']+=1
  if n['eligibleComputed3DHangingSubdivisionNomination']:
   assert not row['longEdgeLiteralWholeProtected']and not n['protectedWholeCurrentNodeIncident']and n['exactFinite3DParameter']is not None
   eligible_nodes.add(tuple(n['exactIdealXYZ']));eligible_edges.add((row['candidateFace'],row['edge']))
  if n['protectedIncidentFamilyConstrainedUnresolved']:constrained_nodes.add(tuple(n['exactIdealXYZ']))
counts['distinctEligibleExactIdealXYZNodes']=len(eligible_nodes);counts['distinctEligibleCandidateEdges']=len(eligible_edges);counts['distinctProtectedConstrainedIdealXYZNodes']=len(constrained_nodes)
pointcounts=Counter()
for row in out['intervalPointRows']:
 pointcounts['savedIntervalPointRows']+=1
 pointcounts['pointRowsWithPackedCollapse']+=any(t['packedProjectedCollapseUncredited']for t in row['idealContainingPackedRejectingFacets'])
 pointcounts['pointRowsWithRejectingEdges']+=any(t['packedRejectingEdges']for t in row['idealContainingPackedRejectingFacets'])
log=P/'actual-terminal-supervisor.log';assert not log.exists();log.write_bytes(Path('/tmp/upton-saved-hanging-subdivision-20261013.log').read_bytes())
result=dict(passed=True,actualPTY=60761,actualCallerExitCode=0,supervisorReportedReleased=True,jobId=receipt['jobId'],result=a.ref(a.DOC/'result.json'),output=a.ref(a.DOC/'complete-saved-gap-hanging-subdivision-investigation.json.gz'),pinnedNeonCompleteExactResult=True,allEvidenceRefsVerified=len(refs),totalEvidenceBytes=total,all42Code86InputPinsExact=True,currentManifestSHA256=a.prior.prior.CURRENT,releasedGroups=groups,producerPIDs=pids,allObservedProducerPIDsAbsent=True,terminalLog=a.ref(log),preparation=a.ref(P/'actual-readonly-preparation.json'),fixtureValidation=a.ref(P/'actual-nine-fixture-validation.json'),counts=dict(counts),rejectingEdgesBySourceKind=dict(kinds),intervalPointCounts=dict(pointcounts),savedFailureRows=357,areaRowsUnlocatedUnresolved=257,protectedLiteralWholeFacets=68,noCoverageUnionGeometryOrAcceptance=True)
path=P/'actual-terminal-neon-allrefs-release-pid-audit.json';assert not path.exists();a.save(path,result);print(json.dumps(result,sort_keys=True))
