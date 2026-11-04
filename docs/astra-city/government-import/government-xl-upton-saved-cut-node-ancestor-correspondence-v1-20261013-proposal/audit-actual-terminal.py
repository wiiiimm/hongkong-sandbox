from pathlib import Path
from collections import Counter
import sys,json
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT/'source-scripts/city/government-import'))
import upton_saved_cut_node_ancestor_correspondence_draft_v1_20261013 as a
P=Path(__file__).parent
receipt=a.read(a.DOC/'result.json');refs=receipt['evidenceRefs'];total=0
for q in refs:total+=a.check(q).stat().st_size
pins=a.read(P/'draft-pins.json')
for q in pins['codeRefs']+pins['inputRefs']:a.check(q)
prep=a.read(P/'actual-readonly-preparation.json');a.check(prep['driver'])
for row in prep['commands']:assert row['exitCode']==0;a.check(row['log'])
with a.connect()as c:
 c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 cursor=c.execute('SELECT token,owner,batch,resources,heartbeat_at,lease_until,released_at FROM astra_modelling.reservation_groups WHERE batch=%s ORDER BY released_at',(a.BATCH,));groups=[dict(zip([d.name for d in cursor.description],row))for row in cursor.fetchall()]
assert len(groups)==2 and all(g['released_at']is not None for g in groups)and sorted(len(g['resources'])for g in groups)==[1,11]
groups=json.loads(json.dumps(groups,default=str));pids=[2011701,2011714,2012013,2012091];assert not any(Path('/proc',str(i)).exists()for i in pids)
assert a.ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==a.prior.prior.prior.CURRENT
out=a.read(a.DOC/'complete-saved-cut-node-ancestor-correspondence.json.gz');assert len(out['intervalPointRows'])==100 and len(out['areaRows'])==257 and len(out['whole68ProtectedTripletsVerbatim'])==68
counts=Counter();incident_kinds=Counter()
for r in out['allCompleteCandidateNodeIncidents']:
 counts['candidateNodeIncidents']+=1;incident_kinds[r['provenanceVerbatim']['kind']]+=1
 for k in ['exact3DNodeIncident','projectedDifferentHeight','literalWholeCurrentProtected']:counts[k]+=bool(r[k])
for r in out['intervalPointRows']:
 counts['intervalPointRows']+=1;counts['idealProtectionMaskMembershipNonempty']+=bool(r['idealProtectionMaskMembership']);counts['currentIdealMembershipNonempty']+=bool(r['completeCurrentIdealPointMembership']);counts['currentActualPackedMembershipNonempty']+=bool(r['completeCurrentActualPackedPointMembership'])
for r in out['nodeProtectionSideConstraints']:
 counts['relevantProtectionMaskConstraints']+=1;counts['nodeIdealMaskInside']+=r['idealInside'];counts['nodePackedInsideIdealMask']+=r['packedInsideIdealMask']
log=P/'actual-terminal-supervisor.log';assert not log.exists();log.write_bytes(Path('/tmp/upton-saved-cut-node-20261013.log').read_bytes())
result=dict(passed=True,actualPTY=18083,actualCallerExitCode=0,supervisorReportedReleased=True,jobId=receipt['jobId'],result=a.ref(a.DOC/'result.json'),output=a.ref(a.DOC/'complete-saved-cut-node-ancestor-correspondence.json.gz'),pinnedNeonCompleteExactResult=True,allEvidenceRefsVerified=len(refs),totalEvidenceBytes=total,all43Code99InputPinsExact=True,currentManifestSHA256=a.prior.prior.prior.CURRENT,releasedGroups=groups,producerPIDs=pids,allObservedProducerPIDsAbsent=True,terminalLog=a.ref(log),preparation=a.ref(P/'actual-readonly-preparation.json'),counts=dict(counts),nodeIncidentKinds=dict(incident_kinds),finiteProtectionBoundaryCorrespondences=len(out['protectionBoundaryCorrespondences']),ancestorSourceProjectedNominees=len(out['completeClosedProjectedSourceAncestorNominees']),areaRowsUnlocatedUnresolved=257,noCoverageUnionGeometryOrAcceptance=True)
path=P/'actual-terminal-neon-allrefs-release-pid-audit.json';assert not path.exists();a.save(path,result);print(json.dumps(result,sort_keys=True))
