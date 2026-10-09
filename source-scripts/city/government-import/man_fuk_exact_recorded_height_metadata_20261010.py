"""Repair one proved arithmetic metadata mismatch; no geometry/loader waiver."""
import copy
import math
from run import digest

UID = 'landsd/266062:0'
SOURCE_SHA = '22b458321ca483c53324ee152cb27c382e5ac4dfd745974f169b1c551ac8a6c1'


def repair(entry, building, source_bytes):
    assert digest(source_bytes) == SOURCE_SHA == entry['sha256']
    assert entry['uid'] == building['uid'] == UID
    assert entry['objectId'] == building['objectId'] == 266062
    assert entry['buildingCSUID'] == building['buildingCSUID'] == '3644619608P20050726'
    assert building['base'] == building['baseHeightHKPD'] == entry['recordedBaseHeight'] == 32.2
    assert building['height'] == 11.2 and building['topHeightHKPD'] == 43.4
    assert entry['recordedTopHeight'] == building['base'] + building['height'] == math.nextafter(43.4, math.inf)
    out = copy.deepcopy(entry)
    out['recordedTopHeight'] = building['topHeightHKPD']
    assert {k: v for k, v in out.items() if k != 'recordedTopHeight'} == {k: v for k, v in entry.items() if k != 'recordedTopHeight'}
    return out, {
        'uid': UID, 'sourceSHA256': SOURCE_SHA,
        'originalEntry': copy.deepcopy(entry), 'correctedEntry': copy.deepcopy(out),
        'changedFields': ['recordedTopHeight'],
        'arithmeticDerivedTop': building['base'] + building['height'],
        'exactAuthoritativeSourceTop': building['topHeightHKPD'],
        'geometryBytesChanged': False, 'placementChanged': False,
        'loaderSourceEqualityWaived': False, 'physicalAccepted': False,
        'qualification': 'Only the proved one-ULP arithmetic-derived recorded top is copied exactly from the current authoritative source form. Every geometry, transform, footprint and runtime gate remains unchanged.'}
