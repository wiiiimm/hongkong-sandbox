"""Private preview contract for a proven non-effect hierarchical terrain successor.

This grants no source, visual, physical or publication acceptance. Existing
publishers remain unchanged and their complete dry run is separately mandatory.
"""
from hierarchical_original_terrain_binding_v1_20261026 import verify_successor


def verify_context(prior, successor, owners, replacement, proof, forms, scope):
    retention = verify_successor(prior, successor, owners)
    assert replacement['retainedUids'] == retention['retainedUids'] == proof['retainedGroupUids']
    assert proof['originalGroupChildrenAndOldGridExact'] is True
    assert proof['allCurrentInstalledAssetBytesVerified'] is True
    assert proof['allExistingNativeWholeSourceTerrainUnaffectedProved'] is True
    assert proof['affectedNativeUids'] == proof['affectedRegisteredBasicSupportUids'] == []
    assert type(proof['allRegisteredBasicSupportsAccounted']) is int
    assert proof['allRegisteredBasicSupportsAccounted'] >= 0
    assert proof['existingNativeReaccepted'] is False and proof['rawLegacyApprovalsChanged'] is False
    assert proof['installationApproved'] is False and proof['publication'] is False
    assert forms['flagged'] == [] and forms['ordinaryFlagged'] == 0
    assert forms['forms'] > 0
    assert scope['rows'] and len({r['uid'] for r in scope['rows']}) == len(scope['rows'])
    assert all(r['currentNativeActorsChecked'] == proof['completeInstalledActorsAccounted']
               and r['nearbyNativeActors'] == [] for r in scope['rows'])
    assert set(owners) <= set(scope['uids'])
    return retention
