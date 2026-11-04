"""Bound one reviewed original and one unsurveyed duplicate BASIC canopy."""
import hashlib
import json


def form_sha(form):
    return hashlib.sha256(json.dumps(form,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()


def verify(models,review,physical,lifecycle,feature,forms):
    assert len(models)==1
    model=models[0];uid=model['uid'];sha=model['sha256']
    sources={uid:sha}
    for decision in [review,physical]:
        assert decision['sourceSHA256ByUid']==sources
        assert all(decision[k]is True for k in ['identityAccepted','sourceSpecificPhysicalInterpretationAccepted','completeNeighbourInterpretationAccepted','visualAcceptance'])
        assert decision['sourceGeometryChanges']==decision['sourcePoseChanges']==0
    assert review['currentManifest']==physical['currentManifest']==feature['currentManifest']
    replacement=review['conditionalCanopyReplacement']
    assert replacement==physical['conditionalCanopyReplacement']
    assert set(replacement)=={'sourceUid','basicUid','sourceSHA256','sourceFormSHA256','basicFormSHA256','onlyWhileExactOwnerActive','approved'}
    basic=replacement['basicUid']
    assert replacement['sourceUid']==uid and replacement['sourceSHA256']==sha and basic!=uid
    assert replacement['onlyWhileExactOwnerActive']is True and replacement['approved']is True
    assert forms[uid]['uid']==uid and forms[basic]['uid']==basic
    assert replacement['sourceFormSHA256']==form_sha(forms[uid])and replacement['basicFormSHA256']==form_sha(forms[basic])
    b=forms[basic]
    assert b==feature['exactBasicForm']and b['structureType']=='Open-sided Structure'
    assert b['heightSource']=='estimated'and b['baseHeightHKPD']is None and b['topHeightHKPD']is None
    assert feature['privateCanopyExperimentApproved']is True and feature['publication']is False and feature['installationApproved']is False
    assert feature['sourceUid']==uid and feature['basicUid']==basic and feature['sourceSHA256']==sha
    assert model['suppressesBuildingUids']==[basic]and model['proceduralWindows']is False
    assert not model.get('supportDependencies')and not model.get('activationGroup')
    assert all(model[k]is False for k in ['publicationApproved','placementReviewed','identityReviewApproved','sourceIdentityReviewed'])
    assert lifecycle['passed']is True and not lifecycle['pageErrors']and lifecycle['publication']is False
    cases=lifecycle['cases'];assert len(cases)==2 and {(r['width'],r['failedUid'])for r in cases}=={(1280,None),(390,uid)}
    for case in cases:
        assert case['completeGroupEvicted']and case['baseOnlyRestoredCompleteGroup']and not case['audit']['violations']
        assert case['sources']==[dict(uid=uid,sha256=sha,triangles=model['triangles'],active=True)]
        phases={r['phase']:r for r in case['canopyLifecycle']}
        expected={'original-active','base-only','auto-restored','evicted-return-base-only'}|({'failed-download'}if case['failedUid']else set())
        assert set(phases)==expected and len(phases)==len(case['canopyLifecycle'])
        for phase,row in phases.items():
            active=phase in ['original-active','auto-restored']
            assert row['ownerActive']is active and row['basicCanopyVisible']is not active
        if case['failedUid']:assert case['failureKeptAllBasics']
    return dict(sourceUid=uid,basicUid=basic,sourceSHA256=sha,exactCanopyFeatureBound=True,completeLifecycleVerified=True,publication=False)
