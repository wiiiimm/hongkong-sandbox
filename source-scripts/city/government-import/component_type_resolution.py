"""Resolve component metadata by exact government IDs; never approve geometry."""
from government_georef_cell_identity import geographic_cell


def resolve(model, sources):
    matches = []
    for source in sources:
        form = source['building']
        try:
            geographic_cell(model['modelId'], form['buildingCSUID'], form['structureType'])
        except (ValueError, KeyError):
            continue
        matches.append(source)
    if len(matches) != 1:
        return {'qualified': False, 'reasons': ['no-exact-current-component' if not matches else 'ambiguous-exact-current-components'],
                'candidateUids': [s['building']['uid'] for s in matches]}
    source = matches[0]; form = source['building']
    official = [m for m in model['matching']['officialCandidates']
                if m.get('objectId') == form['objectId'] and m.get('buildingCSUID') == form['buildingCSUID']]
    if len(official) != 1:
        return {'qualified': False, 'reasons': ['no-unique-exact-official-component'], 'candidateUids': [form['uid']]}
    return {'qualified': True, 'reasons': [], 'uid': form['uid'], 'source': source, 'official': official[0],
            'basis': 'exact-model-georef-tower-podium-type-current-CSUID-and-official-object-id',
            'identityAccepted': False, 'installationApproved': False,
            'qualification': 'Metadata routing only. Original graph, complete projection, contact, foundation, runtime and browser checks remain required.'}
