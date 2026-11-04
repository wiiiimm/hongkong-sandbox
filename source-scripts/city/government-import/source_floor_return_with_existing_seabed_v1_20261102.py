"""Existing single-domain floor return, retaining pre-existing seabed verbatim.

This selects the existing kernel whose1.2m rule applies to newly derived land.
It does not call or modify the different all-land multi-domain constructor.
"""
import numpy as np
import bounded_original_upward_floor_return_v3_20261102 as kernel
import exact_affine_halfplane_clip_v2_20261102 as clipping

def inset(terrain,source):
    terrain=np.asarray(terrain,dtype='<f8');source=np.asarray(source,dtype='<f8')
    previous=kernel.lower_region;clipping.REPAIRS.clear();kernel.lower_region=clipping.lower_region
    try:after,proof=kernel.inset(terrain,source,1.,3.)
    finally:kernel.lower_region=previous
    rows=proof['outputLineage'];assert len(rows)==len(after)
    untouched={r['parentFace']:i for i,r in enumerate(rows)if r['kind']=='unchanged'}
    assert all(np.array_equal(after[i],terrain[parent])for parent,i in untouched.items())
    assert {i for i,t in enumerate(terrain)if t[:,1].max()<1.2}<=set(untouched)
    assert all(after[i,:,1].min()>=1.2 for i,r in enumerate(rows)if r['kind']in ['ramp-plane-core','ramp-derived-return'])
    assert proof['sourceClearanceM']==.05 and proof['sourceDerivedMinimumTerrainY']>=1.2
    return after,{**proof,'unchangedSeabedFacesRetained':True,'boundedAffineClipRepairs':list(clipping.REPAIRS),'genericThresholdChanges':0}
