"""Fetch bounded fresh official records for an explicit original source selection.

No identity or placement approval; preserve raw current records for later review.
"""
import argparse
import gzip
import sys
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
sys.path.insert(0, str(HERE.parent / 'landsd-territory'))
from source import request

URL = 'https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1637211194312_35158/MapServer'


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--batch', required=True)
    p.add_argument('--capture', required=True)
    a = p.parse_args()
    assert all(n.startswith('government-xl-') and '/' not in n for n in [a.batch, a.capture])
    base = ROOT / 'docs/astra-city/government-import'
    doc, cap = base / a.batch, base / a.capture
    assert not doc.exists()
    _, pins = authenticate(cap)
    selection_path = cap / 'selection.json.gz'
    assert digest(selection_path.read_bytes()) == pins[str(selection_path.relative_to(ROOT))]
    selection = read(selection_path)
    rows = selection['rows']
    assert 0 < len(rows) <= 40 and len({r['uid'] for r in rows}) == len(rows)
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == selection['manifestSHA256']
    csuids = sorted({r['source']['building']['buildingCSUID'] for r in rows})
    assert all(s.isalnum() for s in csuids)
    doc.mkdir()
    def query(name, table, where, geometry):
        raw, receipt = request(URL + '/' + str(table) + '/query', dict(
            f='json', where=where, outFields='*', returnGeometry='true' if geometry else 'false',
            outSR='2326', resultRecordCount='1000', orderByFields='OBJECTID'), json_expected=False)
        decoded = gzip.decompress(raw) if raw.startswith(b'\x1f\x8b') else raw
        (doc / (name + '.json')).write_bytes(decoded)
        save(doc / (name + '-request.json'), dict(**receipt, decodedSHA256=digest(decoded), gzipDecoded=decoded != raw))
        if decoded != raw:
            (doc / (name + '-original.gz')).write_bytes(raw)
        result = read(doc / (name + '.json'))
        assert not result.get('error') and not result.get('exceededTransferLimit')
        return result['features']
    where = 'BuildingCSUID IN (' + ','.join("'" + s + "'" for s in csuids) + ')'
    footprints = query('footprints', 0, where, True)
    relations = query('relations', 1002, where, False)
    ids = sorted({int(r['attributes']['BuildingStructureID']) for r in relations})
    structures = query('structures', 1003, 'BuildingStructureID IN (' + ','.join(map(str, ids)) + ')', False) if ids else []
    returned = {r['attributes']['BuildingCSUID'] for r in footprints}
    assert returned <= set(csuids)
    assert digest(manifest.read_bytes()) == selection['manifestSHA256']
    result = dict(uids=sorted(r['uid'] for r in rows), requestedCSUIDs=csuids,
                  missingRequestedCSUIDs=sorted(set(csuids) - returned), footprints=len(footprints),
                  relations=len(relations), structureIDs=ids, structures=len(structures),
                  currentManifestSHA256=selection['manifestSHA256'], identityAccepted=False,
                  installationApproved=False, publication=False, sourceGeometryChanges=0,
                  qualification='Fresh exact selected-CSUID footprints, relations and structure records only. Completeness of a permit, common source identity, support, geometry and publication are not inferred; missing live records remain explicit.')
    save(doc / 'summary.json', result)
    refs = [__file__, HERE.parent / 'landsd-territory/source.py', cap / 'result.json', selection_path, manifest]
    from pathlib import Path
    module('selected_primary_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch, 'fresh-explicit-original-official-primary-records', [Path(r) for r in refs], result)
    print(dict(footprints=len(footprints), relations=len(relations), structures=len(structures), missing=result['missingRequestedCSUIDs']), flush=True)


if __name__ == '__main__':
    main()
