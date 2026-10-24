"""Correct saved-census provenance labels; unchanged v1 numerical attribution."""
from foundation_source_face_attribution_adapter_v1_20261013 import attribute as _attribute
from foundation_source_face_attribution_adapter_v1_20261013 import canonical_pin


def attribute(function, triangles, terrain, target_polygon, complete_saved_components, **kwargs):
    result = _attribute(function, triangles, terrain, target_polygon, complete_saved_components, **kwargs)
    result.pop('savedTrueEdgeBodyInventoryRecomputed')
    result['savedComponentConnectivityRecomputed'] = False
    result['savedComponentConnectivity'] = 'Caller-bound diagnostic census; no true-edge or architectural-body certification'
    result['completeSavedDiagnosticComponentInventory'] = result.pop('completeSavedBodyInventoryVerbatim')
    for group in result['failureGroupsInCanonicalDelegateOrder']:
        group['intersectionsWithEverySavedDiagnosticComponent'] = group.pop('intersectionsWithEveryCompleteSavedBody')
    return result
