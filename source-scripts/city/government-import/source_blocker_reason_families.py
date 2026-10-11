"""Report actual failed contracts; a runtime footprint error is not a budget failure."""
def reason_families(reasons):
    families=set()
    for raw in reasons:
        reason=raw.lower()
        if any(s in reason for s in ('identity','spatial-bound','footprint-fit','georef','exact-current-component','sourceexcess','targetcovered','source-coverage','source-integrity')):
            families.add('identity-or-component-coverage')
        if any(s in reason for s in ('terrain-intersects','foundation','ground-contact','ground-gap','terrain-above','sampler','terrain-construction','terrain-coverage','low-rim')):
            families.add('terrain-or-foundation')
        if any(s in reason for s in ('support','interface','strict-rim-gap')):
            families.add('component-support')
        if 'neighbour' in reason or 'neighbor' in reason:
            families.add('neighbour-impact')
        if any(s in reason for s in ('mobile-runtime-budget','triangle-budget','terrain-budget','exceeds-budget','exceeds-runtime-budget')):
            families.add('runtime-budget')
        if any(s in reason for s in ('source-member-absent','source-model-missing','source-cache-missing','source-member-missing')):
            families.add('missing-government-source')
        if 'pending-explicit-approval' in reason:
            families.add('explicit-approval-pending')
    return sorted(families or {'other-validation-failure'})
