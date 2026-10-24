"""Read complete bounded official permit membership; never approve a source."""
import argparse
import gzip
import sys
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
sys.path.insert(0, str(HERE.parent / 'landsd-territory'))
from source import request
from selected_original_primary_records_v1_20261025 import URL


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for key in ['batch', 'primary', 'permit']:
        p.add_argument('--' + key, required=True)
    a = p.parse_args()
    assert all(n.startswith('government-xl-') and '/' not in n for n in [a.batch, a.primary])
    assert 0 < len(a.permit) <= 100 and not any(ord(c) < 32 for c in a.permit)
    base = ROOT / 'docs/astra-city/government-import'
    doc, primary = base / a.batch, base / a.primary
    assert not doc.exists()
    _, pins = authenticate(primary)
    refs = [__file__, HERE / 'selected_original_primary_records_v1_20261025.py', HERE.parent / 'landsd-territory/source.py', primary / 'result.json']
    def take(name):
        path = primary / name
        assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)
    summary = take('summary.json')
    footprints = take('footprints.json')['features']
    current_structures = take('structures.json')['features']
    assert current_structures and all(r['attributes']['OPNo'] == a.permit for r in current_structures)
    expected = {r['attributes']['BuildingCSUID'] for r in footprints}
    assert expected == set(summary['requestedCSUIDs']) and not summary['missingRequestedCSUIDs']
    doc.mkdir()
    def query(name, table, where):
        params = dict(f='json', where=where, outFields='*', returnGeometry='false', resultRecordCount='1000', orderByFields='OBJECTID')
        raw, receipt = request(URL + '/' + str(table) + '/query', params, json_expected=False)
        decoded = gzip.decompress(raw) if raw.startswith(b'\x1f\x8b') else raw
        (doc / (name + '.json')).write_bytes(decoded)
        save(doc / (name + '-request.json'), dict(**receipt, decodedSHA256=digest(decoded), gzipDecoded=raw != decoded))
        if raw != decoded:
            (doc / (name + '-original.gz')).write_bytes(raw)
        result = read(doc / (name + '.json'))
        assert not result.get('error') and not result.get('exceededTransferLimit')
        return result['features']
    structures = query('complete-permit-structures', 1003, "OPNo = '" + a.permit.replace("'", "''") + "'")
    ids = sorted({int(r['attributes']['BuildingStructureID']) for r in structures})
    assert ids and all(r['attributes']['OPNo'] == a.permit for r in structures)
    relations = query('complete-permit-relations', 1002, 'BuildingStructureID IN (' + ','.join(map(str, ids)) + ')')
    complete = {r['attributes']['BuildingCSUID'] for r in relations}
    result = dict(uids=summary['uids'], permit=a.permit, completeStructureIDs=ids,
                  completePermitCSUIDs=sorted(complete), selectedCSUIDs=sorted(expected),
                  exactSelectedPermitMembership=complete == expected,
                  extraPermitCSUIDs=sorted(complete - expected), missingSelectedCSUIDs=sorted(expected - complete),
                  identityAccepted=False, installationApproved=False, publication=False, sourceGeometryChanges=0,
                  qualification='Complete non-truncated official structure query for the exact permit, then all relations for those structure IDs. This records source membership only; geometry, placement, support, collision, visual and publication checks remain separate.')
    save(doc / 'summary.json', result)
    from pathlib import Path
    module('selected_permit_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch, 'complete-explicit-original-official-permit-membership', [Path(r) for r in refs], result)
    print(dict(exactSelectedPermitMembership=result['exactSelectedPermitMembership'], structures=len(ids), permitCSUIDs=len(complete)), flush=True)


if __name__ == '__main__':
    main()
