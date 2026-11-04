"""Fetch bounded fresh official records for explicit current forms within a completed scene scope.

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
    p.add_argument('--scope', required=True)
    p.add_argument('--uid', action='append', required=True)
    a = p.parse_args()
    assert all(n.startswith('government-xl-') and '/' not in n for n in [a.batch, a.scope])
    base = ROOT / 'docs/astra-city/government-import'
    doc, cap = base / a.batch, base / a.scope
    assert not doc.exists()
    _, pins = authenticate(cap)
    selection_path = cap / 'form-obligations.json.gz'
    scope_refs = []
    if selection_path.exists():
        assert digest(selection_path.read_bytes()) == pins[str(selection_path.relative_to(ROOT))]
        forms = read(selection_path)
    else:
        selection_path = cap / 'summary.json'
        assert digest(selection_path.read_bytes()) == pins[str(selection_path.relative_to(ROOT))]
        scope = read(selection_path)
        assert scope['status'] == 'model-only-current-collision-scope'
        assert scope['terrainEdits'] is False and scope['installationApproved'] is False
        by_uid = {}
        for row in scope['rows']:
            path = cap / (row['uid'].split('/')[1] + '-forms.json.gz')
            assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
            scope_refs.append(path)
            for item in read(path):
                form = item['building']
                uid = form['uid']
                assert uid not in by_uid or by_uid[uid] == form
                tile = ROOT / '3d-viewer' / item['tile']
                assert digest(tile.read_bytes()) == item['tileSHA256'] == scope['currentFormTileHashes'][str(tile.relative_to(ROOT))]
                assert next(f for f in read(tile)['buildings'] if f['uid'] == uid) == form
                scope_refs.append(tile)
                by_uid[uid] = form
        forms = list(by_uid.values())
        assert scope['currentManifestSHA256'] == pins['3d-viewer/city/data/manifest.json']
    wanted=set(a.uid);assert 0<len(wanted)==len(a.uid)<=40
    rows=[dict(uid=f['uid'],source=dict(building=f))for f in forms if f['uid']in wanted];assert {r['uid']for r in rows}==wanted
    selection=dict(manifestSHA256=pins['3d-viewer/city/data/manifest.json'])
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
    refs = [__file__, HERE.parent / 'landsd-territory/source.py', cap / 'result.json', selection_path, manifest, *scope_refs]
    from pathlib import Path
    module('selected_primary_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch, 'fresh-explicit-current-form-official-primary-records', [Path(r) for r in refs], result)
    print(dict(footprints=len(footprints), relations=len(relations), structures=len(structures), missing=result['missingRequestedCSUIDs']), flush=True)


if __name__ == '__main__':
    main()
