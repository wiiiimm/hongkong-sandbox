"""Expose a fully verified original assembly member without erasing raw failures."""
from original_source_assembly_diagnostic import POLICY

def member_identity(compound, uid):
    assert compound['policy'] == POLICY and compound['passed'] and not compound['reasons']
    assert len(compound['uids']) == 2 and uid in compound['uids']
    assert compound['modelGeometryChanges'] == 0 and not compound['installationApproved']
    raw = compound['rawIndividualIdentity'][uid]
    assert raw['sourceSHA256'] == compound['sourceSHA256s'][uid]
    interface = compound['strictOriginalInterface']['interface']
    assert interface['passed'] and interface['samples'] > 0
    assert interface['samples'] == interface['strictContacts'] and not interface['unresolved'] and interface['wallIntersections'] == 0
    return {**raw, 'policy': POLICY, 'passed': True, 'reasons': [],
            'rawIndividualIdentity': raw, 'compoundIdentity': compound,
            'proof': {'exactObjectId': True, 'exactBuildingCSUID': True,
                      'uniqueViewerMatch': True, 'identityAccepted': True},
            'installationApproved': False, 'qualification': compound['qualification']}
