"""Use literal recorded HKPD fields instead of re-adding derived base + height.

Only arithmetic roundoff is recoverable here. Material source mismatches reject.
No geometry, root, base/top coordinate or acceptance rule is changed.
"""
import math


def bind_source_levels(entry, building):
    for key in ('uid', 'objectId', 'buildingCSUID'):
        if entry.get(key) != building.get(key):
            raise ValueError('Different original source identity: ' + key)
    corrected = dict(entry)
    changes = []
    for key, source_key, derived in [
        ('recordedBaseHeight', 'baseHeightHKPD', building['base']),
        ('recordedTopHeight', 'topHeightHKPD', building['base'] + building['height']),
    ]:
        literal, old = building[source_key], entry[key]
        if any(not isinstance(v, (float, int)) or isinstance(v, bool) or not math.isfinite(v)
               for v in (literal, old, derived)):
            raise ValueError('Invalid recorded source level: ' + key)
        if old == literal:
            continue
        # Rebind only our exact derived arithmetic result, within two ULPs of
        # the original literal. A rounded or otherwise changed value rejects.
        if old != derived or abs(old - literal) > 2 * max(math.ulp(old), math.ulp(literal)):
            raise ValueError('Material recorded source mismatch: ' + key)
        corrected[key] = literal
        changes.append({'field': key, 'sourceField': source_key, 'previous': old,
                        'originalLiteral': literal, 'differenceM': old - literal})
    return corrected, changes
