"""Bound only the exact reviewed original eastern pier and its misclassified BASIC apron graphic."""
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
    assert review['currentManifest']==physical['currentManifest']
    replacement=review['conditionalApronReplacement']
    assert replacement==physical['conditionalApronReplacement']
    assert set(replacement)=={'sourceUid','basicUid','sourceSHA256','sourceFormSHA256','basicFormSHA256','onlyWhileExactOwnerActive','approved'}
    basic=replacement['basicUid']
    assert replacement['sourceUid']==uid and replacement['sourceSHA256']==sha and basic!=uid
    assert replacement['onlyWhileExactOwnerActive']is True and replacement['approved']is True
    assert forms[uid]['uid']==uid and forms[basic]['uid']==basic
    assert replacement['sourceFormSHA256']==form_sha(forms[uid])and replacement['basicFormSHA256']==form_sha(forms[basic])
    b=forms[basic]
    assert b==feature['exactBasicForm'] and uid=='landsd/75643:0' and basic=='way/334029318:0'
    assert sha=='4c8e577256875f9ecc67fe5728e262113d852748ac743798b804f9b090f0dbc2'
    assert model['modelId']=='B227511866801062G0' and model['buildingCSUID']=='2275118668T20050725' and model['objectId']==75643
    assert model['footprintScope']=='reviewed-original-feature:'+uid and model.get('variantId') is None and model.get('verticalPlacementOffsetHKPD',0)==0
    assert model['reviewedOsmApronGraphic']==dict(policy='exact-original-disneyland-pier-apron-v1',sourceSHA256=sha,basicFormSHA256='d08fe7d950c6efa8ef8afc7d2251770f7d6a5508995004d77b2a25c0ed45cda1',reviewSHA256='d9c2a503febf90dee0d67a14ac19520965c5faf793cf417bd19209091f643c48')
    assert b['heightSource']=='estimated' and b['height']==24 and b['levels'] is None and b['kind']=='yes'
    assert feature['graphicInterpretationAccepted']is True and feature['publication']is False and feature['installationApproved']is False
    assert feature['ownerUid']==uid and feature['basicUid']==basic and feature['sourceSHA256']==sha
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
    return dict(sourceUid=uid,basicUid=basic,sourceSHA256=sha,exactApronFeatureBound=True,completeLifecycleVerified=True,publication=False)
