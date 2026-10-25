"""Exact availability graph for originals that retain surveyed BASIC podiums."""

def expected_dependencies(models, bindings, replacements, *, include_basic):
    by_uid = {model['uid']: model for model in models}
    by_binding = {binding['uid']: binding for binding in bindings}
    assert len(by_uid) == len(models) == len(by_binding) == len(bindings)
    assert set(by_uid) == set(by_binding)
    assert set(replacements) <= set(by_uid)
    assert set(replacements.values()) <= set(by_uid)
    for uid, binding in by_binding.items():
        assert binding['sourceSHA256'] == by_uid[uid]['sha256']
        assert binding['supportUid'] not in by_uid
        assert binding['mustRemainBasicAndUnsuppressed'] is True
        assert binding['futureReplacementRequiresDependentRevalidation'] is True
    for uid in by_uid:
        seen = set()
        at = uid
        while at in replacements:
            assert at not in seen, 'Cyclic original availability dependency'
            seen.add(at)
            at = replacements[at]
    result = {}
    for uid in by_uid:
        dependencies = []
        parent = replacements.get(uid)
        if parent:
            target = by_uid[parent]
            dependencies.append(dict(uid=parent, state='installed',
                                     buildingCSUID=target['buildingCSUID'], sha256=target['sha256']))
        if include_basic:
            dependencies.append(dict(uid=by_binding[uid]['supportUid'], state='surveyed-footprint-fallback'))
        result[uid] = dependencies
    return result
