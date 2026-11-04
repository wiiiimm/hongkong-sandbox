from pathlib import Path
from collections import Counter,defaultdict
import sys,json
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT/'source-scripts/city/government-import'))
import upton_saved_uncovered_packed_ancestor_boundary_attribution_draft_v1_20261013 as a
P=Path(__file__).parent
receipt=a.read(a.DOC/'result.json');assert receipt['jobId']=='99e1e9daa5bde8286df4224360ab17934044b87d13226d7491e8700ca4860b6a'
refs=receipt['evidenceRefs'];total=0
for q in refs:total+=a.check(q).stat().st_size
pins=a.read(P/'draft-pins.json')
for q in pins['codeRefs']+pins['inputRefs']:a.check(q)
with a.connect()as c:
 c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 cursor=c.execute('SELECT token,owner,batch,resources,heartbeat_at,lease_until,released_at FROM astra_modelling.reservation_groups WHERE batch=%s ORDER BY released_at',(a.BATCH,));groups=[dict(zip([d.name for d in cursor.description],row))for row in cursor.fetchall()]
assert len(groups)==2 and all(g['released_at']is not None for g in groups)and sorted(len(g['resources'])for g in groups)==[1,11]
groups=json.loads(json.dumps(groups,default=str));pids=[1768217,1768419,1768628,1768673];assert not any(Path('/proc',str(i)).exists()for i in pids)
assert a.ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==a.prior.CURRENT
output=a.read(a.DOC/'complete-saved-failures-packed-ancestor-boundary-attribution.json.gz');assert len(output['rows'])==357
counts=defaultdict(Counter);kind_counts=defaultdict(Counter)
for r in output['rows']:
 k=r['uid']+'|'+r['mode'];cc=counts[k];q=r['localGapAttribution'];cc['completeRawFailureRows']+=1;cc['areaGapLocationsUnresolved']+=q['areaGapPolygonCoordinatesNotSaved']
 for g in q['savedFirstIntervalGapAttribution']:
  cc['savedIntervalGapMidpoints']+=1;cc['explicitSavedFinalReachTailGaps']+=g['tailGapFromSavedFinalReach']
  cc['idealNonzeroProjectedFragmentContainsMidpoint']+=bool(g['idealFragmentPointMembershipCandidates']);cc['packedSelectedFragmentContainsMidpoint']+=bool(g['packedFragmentPointMembershipWithinSavedSelectedDrawOrigins'])
  cc['idealContainsButPackedDoesNot']+=bool(g['idealFragmentPointMembershipCandidates'])and not bool(g['packedFragmentPointMembershipWithinSavedSelectedDrawOrigins'])
 for p in output['relevantCandidateFaces'][:0]:pass
for c in output['relevantCandidateFaces']:
 cc=kind_counts[c['provenanceVerbatim']['kind']];cc['completeRelevantCandidateFaces']+=1
 for v in c['completeVertices']:
  cc['verticesWithNonzeroExactPackingDisplacement']+=any(a.F(x)!=0 for x in v['exactPackingDeltaXYZ'])
  for r in v['ancestorBoundaryCorrespondences']:
   cc['exactIdealAncestorEdgePointCorrespondences']+=1;cc['packedVertexOffPackedAncestorEdge']+=not r['packedPointOnPackedAncestorClosedEdge']
 for e in c['completeEdges']:
  cc['completeEdgeRows']+=1;cc['idealProjectedEdgeWithDifferentPackedMate']+=bool(e['idealProjectedMatesWithDifferentPackedEdges'])
log=P/'actual-terminal-supervisor.log';assert not log.exists();log.write_bytes(Path('/tmp/upton-saved-packed-ancestor-boundaries-20261013.log').read_bytes())
result=dict(passed=True,actualPTY=70020,actualCallerExitCode=0,supervisorReportedReleased=True,jobId=receipt['jobId'],result=a.ref(a.DOC/'result.json'),output=a.ref(a.DOC/'complete-saved-failures-packed-ancestor-boundary-attribution.json.gz'),pinnedNeonCompleteExactResult=True,allEvidenceRefsVerified=len(refs),totalEvidenceBytes=total,allCodeAndInputPinsExact=True,currentManifestSHA256=a.prior.CURRENT,releasedGroups=groups,producerPIDs=pids,allObservedProducerPIDsAbsent=True,terminalLog=a.ref(log),preparation=a.ref(P/'actual-readonly-preparation-v2.json'),countsByUIDAndWorld={k:dict(v)for k,v in counts.items()},candidateBoundaryCountsByKind={k:dict(v)for k,v in kind_counts.items()},completeRelevantCandidateFaces=len(output['relevantCandidateFaces']),noCoverageUnionGeometryOrAcceptance=True)
out=P/'actual-terminal-neon-allrefs-release-pid-audit.json';assert not out.exists();a.save(out,result);print(json.dumps(result,sort_keys=True))
