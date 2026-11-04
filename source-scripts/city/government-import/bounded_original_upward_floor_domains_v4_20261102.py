"""Existing floor-return domains with separately bounded affine repair."""
from copy import deepcopy
import bounded_original_upward_floor_return_v3_20261102 as original
import bounded_original_upward_floor_domains_v3_20261102 as domains
import exact_affine_halfplane_clip_v2_20261102 as clipping


def inset(terrain, ramps, core_margin=1., return_width=3.):
    assert domains.single_inset is original.inset
    previous = original.lower_region
    clipping.REPAIRS.clear()
    original.lower_region = clipping.lower_region
    try:
        after, proof = domains.inset(terrain, ramps, core_margin, return_width)
        return after, {**proof, 'boundedAffineClipRepairs': deepcopy(clipping.REPAIRS),
                       'genericThresholdChanges': 0}
    finally:
        original.lower_region = previous
