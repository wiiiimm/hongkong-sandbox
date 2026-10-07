"""Resolve remote footprint/global-bottom diagnostics using complete contact proof.

Low-edge gaps, minimum surface clearance, source integrity, sampler agreement
and complete solid foundation guards retain their existing strict limits.
"""
from terrain_diagnostic_resolution import resolve_global_bottom_warning

GAP = 'sampled-ground-gap-below-model-bottom'
ABOVE = 'sampled-terrain-above-model-bottom'
POLICY = 'complete-source-contact-resolves-global-footprint-extrema-v1'

def resolve_footprint_extrema(validation_row, metric, foundation_row):
    result = resolve_global_bottom_warning(validation_row, metric, foundation_row)
    # Exactly the existing same-source full physical predicate, without
    # changing the supplied measurements or accepting any actual contact gap.
    strict = resolve_global_bottom_warning({**validation_row, 'concerns': [ABOVE]}, metric, foundation_row)
    if GAP in result['remaining'] and strict['resolved'] == [ABOVE]:
        result['resolved'].append(GAP)
        result['remaining'].remove(GAP)
    result['policy'] = POLICY
    result['qualification'] = ('Only footprint-wide/global-bottom extrema warnings may resolve with '
        'unchanged strict low-edge contact, source preservation, rendered sampler and complete '
        'solid foundation proof. Unknown warnings, identity and all neighbor/browser checks remain required.')
    return result
