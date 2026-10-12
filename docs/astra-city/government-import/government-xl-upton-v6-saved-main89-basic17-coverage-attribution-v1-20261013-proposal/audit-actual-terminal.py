from pathlib import Path
import sys,json,hashlib,collections
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT/'source-scripts/city/government-import'))
import upton_v6_saved_coverage_failure_attribution_draft_v1_20261013 as a
P=Path(__file__).parent
receipt=a.read(a.DOC/'result.json');assert receipt['jobId']=='4348f47adf4f17433b6302f5c5e95599fded247a008804c6b1e1f5b208931608'
refs=receipt['evidenceRefs'];total=0
for q in refs:total+=a.check(q).stat().st_size
pins=a.read(P/'draft-pins.json')
for q in pins['codeRefs']+pins['inputRefs']:a.check(q)
with a.connect()as c:
    c.execute('SET TRANSACTION READ ONLY')
    assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
    groups=c.execute('SELECT token,owner,batch,resources,heartbeat_at,lease_until,released_at FROM astra_modelling.reservation_groups WHERE batch=%s ORDER BY released_at',(a.BATCH,)).fetchall()
assert len(groups)==2 and all(g['released_at']is not None for g in groups)
assert sorted(len(g['resources'])for g in groups)==[1,11]
pids=[1625872,1625881,1625982,1626245];assert not any(Path('/proc',str(i)).exists()for i in pids)
assert a.ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==a.CURRENT
output=a.read(a.DOC/'complete-main89-four-world-basic17-saved-attribution.json.gz');rows=output['rows'];assert len(rows)==357
counts=collections.defaultdict(collections.Counter)
for r in rows:
    k=r['uid']+'|'+r['mode'];cc=counts[k];cc['completeSavedFailureRows']+=1
    cc['insideClosedCapturedDomain']+=r['entireSourceProjectionInsideCapturedDomain'];cc['potentialExtractionLimits']+=r['potentialOutsideDomainExtractionLimit']
    cc['coarseBoundAtLeastOrdinary']+=r['coarseBoundAlreadyAtLeastOrdinary'];cc['negativeCoarseBoundNotActualBurialProof']+=r['negativeCoarseBoundIsNotActualBurialProof']
    cc['rawCoverageFailuresRetained']+=r['rawCoverageFailureRetained']
    for g in r['selectedGroundProvenance']:
        cc['selectedGroundEntries']+=1;cc['exactBeforeCurrentMatches']+=bool(g['exactBeforeCurrentDrawFaceIDs']);cc['unmatchedCandidateOrigin']+=g['unmatchedCandidateOriginRemainsExplicit'];cc['ambiguousCandidateOrigins']+=g['candidateOriginAmbiguous']
        for m in g['allExactCandidateFaceOrigins']:
            cc['candidateIndexAdmitted']+=m['indexAdmission']['heightIndexAdmitted'];cc['candidateIndexExcluded']+=not m['indexAdmission']['heightIndexAdmitted']
            cc['kind:'+m['provenance']['kind']]+=1
terminal=P/'actual-terminal-supervisor.log';assert not terminal.exists();terminal.write_bytes(Path('/tmp/upton-saved-main89-basic17-attribution-20261013.log').read_bytes())
out=dict(passed=True,actualPTY=25630,actualCallerExitCode=0,supervisorReportedReleased=True,jobId=receipt['jobId'],result=a.ref(a.DOC/'result.json'),output=a.ref(a.DOC/'complete-main89-four-world-basic17-saved-attribution.json.gz'),pinnedNeonCompleteExactResult=True,allEvidenceRefsVerified=len(refs),totalEvidenceBytes=total,allDeclaredPinsStillExact=True,currentManifestSHA256=a.CURRENT,releasedGroups=groups,producerPIDs=pids,allObservedProducerPIDsAbsent=True,terminalLog=a.ref(terminal),preparation=a.ref(P/'actual-readonly-preparation.json'),countsByUIDAndWorld={k:dict(v)for k,v in counts.items()},noFiniteCoverageReplayOrAcceptance=True)
file=P/'actual-terminal-neon-allrefs-release-pid-audit.json';assert not file.exists();a.save(file,out);print(json.dumps(out,default=str,sort_keys=True))
