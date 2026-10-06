"""Reuse installed identity only for identical original bytes, form and catalogue."""
import hashlib
import json


def canonical_sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def reuse_identity(*, current_form, accepted_form, candidate, installed_model,
                   catalogue_sha, acceptance, acceptance_sha, review):
    uid=current_form['uid'];sha=candidate['sha256']
    assert current_form==accepted_form, 'Accepted source form changed'
    assert review['uid']==uid and review['review_state']=='installed-verified'
    assert review['source_sha256']==sha and review['result']['source_sha256']==sha
    assert review['result']['sha256']==acceptance_sha, 'Installed acceptance receipt changed'
    assert acceptance['uid']==uid and acceptance['sourceSHA256']==sha
    assert acceptance['catalogueSHA256']==catalogue_sha, 'Installed catalogue changed'
    assert installed_model['sourceIdentityReviewed'] and installed_model['identityReviewApproved'] and installed_model['placementReviewed']
    for key in ('uid','objectId','buildingCSUID','modelId','sha256','worldBounds','rootTranslation','recordedBaseHeight','recordedTopHeight'):
        assert candidate[key]==installed_model[key], 'Installed model identity/placement changed: '+key
    assert candidate['uid']==uid and candidate['objectId']==current_form['objectId'] and candidate['buildingCSUID']==current_form['buildingCSUID']
    return {'uid':uid,'sourceSHA256':sha,'reviewSnapshot':review['snapshot_id'],
            'installedAcceptanceSHA256':acceptance_sha,'catalogueSHA256':catalogue_sha,
            'sourceFormSHA256':canonical_sha(current_form),'identityAccepted':True,
            'basis':'exact-unchanged-installed-source-form-transform-and-acceptance',
            'qualification':'Identity reuse only. New source/support contacts, terrain, neighbours and runtime gates remain mandatory.'}
