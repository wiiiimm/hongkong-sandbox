"""Require the viewer's actual nested-patch schema before the frozen point proof."""
from original_terrain_point_contact_v1_20261025 import verify as frozen_verify


def verify(scope, candidate, root, old_by_url):
    # The viewer uses `patches`; `children` is also rejected by the numerical
    # V1 contract. No nested geometry may escape the complete domain proof.
    assert not candidate.get('patches'), 'Nested candidate patches need separate proof'
    assert all(not node.get('patches') for node in old_by_url.values()), 'Nested old patches need separate proof'
    return frozen_verify(scope, candidate, root, old_by_url)
