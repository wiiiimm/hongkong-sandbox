"""Bind only a one-ULP decimal-sum metadata discrepancy to the current record.

No tolerance is applied to model geometry or genuine source-record differences.
"""
import argparse
import copy
from decimal import Decimal
import math
from pathlib import Path
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def exact_recorded_top(entry, building):
    expected = building['topHeightHKPD']
    recorded = entry['recordedTopHeight']
    assert all(isinstance(v, (int, float)) and math.isfinite(v)
               for v in [expected, recorded, building['baseHeightHKPD'], building['height']])
    assert entry['recordedBaseHeight'] == building['baseHeightHKPD']
    if recorded == expected:
        return expected, False
    assert recorded == building['baseHeightHKPD'] + building['height']
    assert Decimal(str(building['baseHeightHKPD'])) + Decimal(str(building['height'])) == Decimal(str(expected))
    assert abs(recorded - expected) == math.ulp(expected)
    return expected, True


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for key in ['batch', 'selection']:
        p.add_argument('--' + key, required=True)
    a = p.parse_args()
    base = ROOT / 'docs/astra-city/government-import'
    out = base / a.batch
    assert a.batch.startswith('government-xl-') and '/' not in a.batch and not out.exists()
    _, pins = authenticate(base / a.selection)
    sp = base / a.selection / 'selection.json.gz'
    assert digest(sp.read_bytes()) == pins[str(sp.relative_to(ROOT))]
    before = read(sp)
    selected = copy.deepcopy(before)
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == selected['manifestSHA256']
    refs, changes = [Path(__file__), base / a.selection / 'result.json', sp, manifest], []
    for row in selected['rows']:
        entry = row['candidate']['entry']
        assert not any(entry.get(k) for k in ['publicationApproved', 'placementReviewed', 'identityReviewApproved', 'sourceIdentityReviewed'])
        tile = ROOT / '3d-viewer' / row['source']['tile']
        assert digest(tile.read_bytes()) == row['source']['tileSHA256']
        building = row['source']['building']
        assert next(f for f in read(tile)['buildings'] if f['uid'] == row['uid']) == building
        asset = ROOT / row['candidate']['path']
        assert digest(asset.read_bytes()) == row['sourceSHA256'] == entry['sha256']
        refs.extend([tile, asset])
        value, changed = exact_recorded_top(entry, building)
        if changed:
            changes.append(dict(uid=row['uid'], field='recordedTopHeight', before=entry['recordedTopHeight'],
                                after=value, exactDecimalBase=str(building['baseHeightHKPD']),
                                exactDecimalHeight=str(building['height']), binaryDifference=entry['recordedTopHeight'] - value,
                                sourceGeometryChanges=0, sourcePoseChanges=0))
            entry['recordedTopHeight'] = value
    assert changes
    restored = copy.deepcopy(selected)
    for change in changes:
        next(r for r in restored['rows'] if r['uid'] == change['uid'])['candidate']['entry']['recordedTopHeight'] = change['before']
    assert restored == before
    assert digest(manifest.read_bytes()) == selected['manifestSHA256']
    save(out / 'selection.json.gz', selected)
    result = dict(uids=[r['uid'] for r in selected['rows']], changes=changes,
                  sourceGeometryChanges=0, sourcePoseChanges=0, installationApproved=False, publication=False,
                  qualification='Only unapproved entry recordedTopHeight is rebound to its exact unchanged current source field when its previous value is the binary base+height sum, the decimal sum exactly equals the current top, and the difference is precisely one ULP. All other input fields and original bytes remain identical. No source acceptance, geometric tolerance, height/pose edit or publication permission.')
    save(out / 'summary.json', result)
    module('record_top_binding_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch, 'exact-current-unapproved-decimal-sum-recorded-top-binding', refs, result)


if __name__ == '__main__':
    main()
