"""Resolve formerly unmapped fixed sources by explicit, byte-exact reviewed provenance."""
def resolve_uid(prior, models):
    if prior['uid'] is not None:
        return prior['uid']
    matches = [m for m in models if m.get('originalSourceKey') == prior['sourceKey']]
    if not matches:
        return None
    assert len(matches) == 1, 'Ambiguous fixed-source runtime binding'
    model = matches[0]
    assert model['sha256'] == prior['indexedSourceSHA256'], 'Fixed-source bytes changed'
    assert model['modelId'] == prior['sourceKey'].rsplit('/', 1)[1], 'Fixed-source model ID changed'
    assert all(model.get(k) is True for k in ('sourceIdentityReviewed', 'identityReviewApproved', 'placementReviewed', 'publicationApproved')), 'Source binding lacks explicit acceptance'
    assert isinstance(model.get('uid'), str) and model['uid'].startswith('landsd/')
    return model['uid']
