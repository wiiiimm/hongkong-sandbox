"""Bind exact eight-source physical interpretation to current ordinary validation."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-lai-chi-kok-functional-applicability-v1-20261019';DOC=BASE/BATCH
def folder(n):return BASE/('government-xl-lai-chi-kok-'+n+'-20261019')
def main():
    assert not DOC.exists();refs=[Path(__file__),HERE/'acceptance-policy.py'];pins={}
    names=['platform-grade-review-v1','v5-identity-support-review','ordinary-validation-v1','component-identity-review-v1','original-component-checks-v1']
    with connect()as c:
        c.execute('SET TRANSACTION READ ONLY')
        for name in names:
            p=folder(name)/'result.json';r=read(p);assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(p)
            for e in r['evidenceRefs']:
                assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
    for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
    validation=read(folder('ordinary-validation-v1')/'validation.json');assert validation['models']==validation['loaderAccepted']==validation['checksPassed']==8 and validation['exceptions']==0
    grade=read(folder('platform-grade-review-v1')/'ROOT-GRADE-REVIEW.json');review=read(folder('v5-identity-support-review')/'ROOT-IDENTITY-SUPPORT-REVIEW.json');identities=read(folder('component-identity-review-v1')/'ROOT-IDENTITY-REVIEW.json')
    assert grade['originalGradeInterpretationAccepted']and review['platformIdentityAccepted']and review['sourceSpecificComponentSupportInterpretationAccepted']
    sources=review['requiredAssemblySources'];assert len(sources)==8
    identity_accepted={r['uid']for r in identities['rows']if r['identityAccepted']}|{review['uid']}
    for uid in set(sources)-identity_accepted:
        proof=read(folder('original-component-checks-v1')/(uid.split('/')[1]+'-identity.json'));assert proof['sourceSHA256']==sources[uid]and proof['passed'];identity_accepted.add(uid)
    assert identity_accepted==set(sources)
    metrics=read(folder('eight-runtime-v2')/'metrics.json');policy=module('lai_actual_policy',HERE/'acceptance-policy.py');bindings=[];raw_reasons={}
    triangles={r['uid']:r['triangles']for r in read(folder('eight-runtime-v2')/'selection.json.gz')['rows']}
    for metric in metrics['rows']:
        uid=metric['uid'];assert metric['sourceSHA256']==sources[uid]and metric['sourcePreserved']and metric['missingTerrain']==0 and metric['maxSamplerDelta']==0
        # Exact identifiers/unique routing have been separately qualified in the bound reviews.
        proof=dict(exactObjectId=True,exactBuildingCSUID=True,uniqueViewerMatch=True,identityAccepted=uid in identity_accepted)
        reasons=policy.reasons(dict(state='runtime-validated-awaiting-acceptance',sourceSHA256=sources[uid],identityProof=proof),metric,metrics['profiles']['mobile'])
        assert set(reasons)<={'terrain-intersects-source-over-0.5m','ground-contact-unresolved'},(uid,reasons)
        raw_reasons[uid]=reasons
        for mode in ['original','literal','explicitLeftF32','explicitBalancedF32']:
            f=read(folder('eight-foundations-v2')/(uid.split('/')[1]+'-'+mode+'.json'));assert f['sourceSHA256']==sources[uid]and f['foundation']['completeTerrainTriangles']==f['foundation']['triangles']==triangles[uid]
            bindings.append(dict(uid=uid,mode=mode,sourceSHA256=sources[uid],wholeWorldSHA256=f['wholeWorldSHA256']))
    native=read(folder('eight-neighbours-v2')/'native-neighbour-checks.json');near=read(folder('eight-neighbours-v2')/'summary.json');assert near['forms']==262 and not near['basicReasons']and not near['unresolvedNatives']and all(r['passed']for r in native['rows'])
    q=dict(uids=sorted(sources),sourceBindings=bindings,sourceSHA256ByUid=sources,sourceScopedApplicabilityAccepted=True,remainingPhysicalReasons=[],rawPolicyReasons=raw_reasons,rawDiagnosticConcerns=[dict(uid=r['uid'],concerns=r.get('concerns',[]))for r in validation['results']],rawNumericalFailuresRemainFailed=True,mainPlatformGradeReview=dict(path=str((folder('platform-grade-review-v1')/'ROOT-GRADE-REVIEW.json').relative_to(ROOT)),sha256=digest((folder('platform-grade-review-v1')/'ROOT-GRADE-REVIEW.json').read_bytes())),currentIdentityAndCompanionSupportReview=dict(path=str((folder('v5-identity-support-review')/'ROOT-IDENTITY-SUPPORT-REVIEW.json').relative_to(ROOT)),sha256=digest((folder('v5-identity-support-review')/'ROOT-IDENTITY-SUPPORT-REVIEW.json').read_bytes())),sourceGeometryChanges=0,sourcePoseChanges=0,aiGeometryModelling=False,publicationApproved=False,installationApproved=False,stagedAndLiveBrowserStillRequired=True,qualification='Only this exact eight-source assembly, repaired V5terrain, current renderer/forms and 262-form/three-native neighbour domain. Raw terrain and low-rim warnings are interpreted by the bound source-specific reviews, never numerically relabelled passing. Any unqualified identity, integrity, coverage, sampler or budget reason fails this adapter.')
    save(DOC/'qualification.json',q)
    module('lai_applicability_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-eight-original-functional-applicability',list(dict.fromkeys(refs)),dict(uids=sorted(sources),sourceScopedApplicabilityAccepted=True,installationApproved=False))
    print(raw_reasons,flush=True)
if __name__=='__main__':main()
