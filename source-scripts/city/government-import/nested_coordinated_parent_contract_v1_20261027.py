"""Bind one exact nested native replacement and one appended finite mate.

No changes to the existing standalone coordinated protocol. The complete prior
parent stays hash-bound. Every unrelated child, grid value and metadata field
must survive byte-for-value; both exact new member bodies must be present.
"""
from copy import deepcopy

POLICY = 'exact-nested-native-replacement-and-mate-v1'


def targets(node):
    result = set(node['meta'].get('targetUids', []))
    for child in node.get('patches', []):
        result.update(targets(child))
    return result


def verify_parent(prior, successor, proof, own_marker, reference, canonical_sha):
    binding = proof['parentBinding']
    assert set(binding) == {'policy', 'retainedMember', 'retainedChildIndex', 'newMember', 'newTargetUids'}
    assert binding['policy'] == POLICY
    assert prior.get('patches') and not prior.get('nativeMesh') and not prior.get('hydro')
    assert successor.get('patches') and not successor.get('nativeMesh') and not successor.get('hydro')
    retained, new = binding['retainedMember'], binding['newMember']
    assert retained != new and set(proof['members']) == {retained, new}
    index = binding['retainedChildIndex']
    assert type(index) is int and 0 <= index < len(prior['patches'])
    assert len(successor['patches']) == len(prior['patches'])+1, 'A pair member or retained child is missing'
    old = prior['patches'][index]
    assert old.get('nativeMesh') and not old.get('patches')
    wanted = binding['newTargetUids']
    assert isinstance(wanted, list) and wanted and len(wanted) == len(set(wanted)) <= 8
    assert all(isinstance(uid, str) and uid.startswith('landsd/') for uid in wanted)
    assert not set(wanted) & targets(prior), 'New model already belongs to prior group'
    # Rebinding the historical before-node to the exact current parent changes
    # only these two provenance fields. Its geometry and all other fields stay.
    before = reference(proof['members'][retained]['before'])
    rebound = deepcopy(old)
    rebound['meta']['parentTerrain'] = before['meta']['parentTerrain']
    rebound['meta']['parentSha256'] = before['meta']['parentSha256']
    assert rebound == before, 'Historical retained geometry or metadata changed'
    actual = {retained: successor['patches'][index], new: successor['patches'][-1]}
    candidates = {name: reference(proof['members'][name]['candidate']) for name in [retained, new]}
    for name in [retained, new]:
        member = proof['members'][name]
        assert canonical_sha(candidates[name]) == member['canonicalSHA256']
        assert canonical_sha(actual[name]) == member['canonicalSHA256'], 'An exact effective pair member changed'
        marker = actual[name].get('nativeMesh', {}).get('source', {}).get('coordinatedBoundary')
        assert marker == dict(policy=own_marker['policy'], proof=own_marker['proof'], member=name), 'Pair markers do not bind the same proof'
    assert set(candidates[retained]['meta']['targetUids']) == targets(old) | set(wanted)
    assert set(candidates[new]['meta']['targetUids']) == set(wanted)
    expected = deepcopy(prior)
    expected['patches'][index] = actual[retained]
    expected['patches'].append(actual[new])
    expected['meta']['targetUids'] = sorted(targets(prior) | set(wanted))
    assert successor == expected, 'Retained parent grid, child order or unrelated metadata changed'
    return dict(retainedChildren=len(prior['patches'])-1, replacedChildIndex=index,
                bothExactMembersPresent=True, allParentGridValuesUnchanged=True,
                sourceGeometryApproval=False, installationApproved=False)
