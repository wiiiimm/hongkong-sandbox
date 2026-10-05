"""Separate actual installed native models from declared terrain target forms.

Terrain target metadata is coverage/provenance, not an installation ledger. Every
declared target must still exist in the frozen neighbour inputs. Uninstalled
targets require the ordinary basic-neighbour gates, never native acceptance.
"""


def retained_scope(target_uids, installed_entries, neighbour_forms):
    declared = set(target_uids)
    assert declared, 'Retained terrain must declare its source targets'
    forms = {b['uid']: b for b in neighbour_forms}
    assert declared <= set(forms), 'Declared terrain target missing from neighbour inputs'
    native = declared & set(installed_entries)
    basic = declared - native
    assert native, 'No installed native source to retain; use a separate terrain review'
    assert all(not forms[u].get('modelGeometry') for u in basic), 'Inline native geometry requires its own full source check'
    return {'nativeUids': sorted(native), 'basicUids': sorted(basic),
            'declaredTargetUids': sorted(declared)}
