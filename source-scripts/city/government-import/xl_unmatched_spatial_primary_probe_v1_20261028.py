"""Nominate current records intersecting two unmatched originals' full extents.

Spatial proximity never assigns a replacement UID or transfers source approval.
"""
import argparse
import gzip
import json
import subprocess
import sys
import uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
sys.path.insert(0, str(HERE.parent / 'landsd-territory'))
from source import request

BASE = ROOT / 'docs/astra-city/government-import'
PRIOR = BASE / 'government-xl-two-unmatched-current-primary-probe-v1-20261028'
BATCH = 'government-xl-two-unmatched-spatial-primary-probe-v1-20261028'
URL = 'https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1637211194312_35158/MapServer/0/query'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--owned', action='store_true')
    args = parser.parse_args()
    out, local = BASE / BATCH, HERE / 'local' / BATCH
    lp = local / 'reservation.json'
    assert not out.exists()
    _, pins = authenticate(PRIOR)
    path = PRIOR / 'summary.json'
    assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
    prior = read(path)
    assert len(prior['rows']) == 2
    if not args.owned:
        assert not local.exists()
        claim = reservations.claim('unmatched-spatial-probe-' + str(uuid.uuid4()),
            ['identity-probe:' + r['sourceKey'] for r in prior['rows']], batch=BATCH, ttl=1800)
        assert claim['ok']
        return execute_reserved(claim['reservation'], lp, [sys.executable, __file__, '--owned'])
    lease = read(lp)
    assert reservations.owns(lease)
    refs = [Path(__file__), PRIOR / 'result.json', path, HERE.parent / 'landsd-territory/source.py']
    rows = []
    for row in prior['rows']:
        georef = row['georef']
        lo, hi = row['originalNativeModel']['worldBounds']
        bounds = dict(xmin=834500 + lo[0], ymin=816500 - hi[2],
                      xmax=834500 + hi[0], ymax=816500 - lo[2])
        georef_e, georef_n = 800000 + int(georef[:5]), 800000 + int(georef[5:])
        assert bounds['xmin'] <= georef_e <= bounds['xmax'] and bounds['ymin'] <= georef_n <= bounds['ymax']
        envelope = dict(xmin=bounds['xmin'] - 20, ymin=bounds['ymin'] - 20,
                        xmax=bounds['xmax'] + 20, ymax=bounds['ymax'] + 20,
                        spatialReference=dict(wkid=2326))
        params = dict(f='json', where="Status = 'Active'", geometry=json.dumps(envelope, separators=(',', ':')),
                      geometryType='esriGeometryEnvelope', spatialRel='esriSpatialRelIntersects',
                      inSR='2326', outSR='2326', outFields='*', returnGeometry='true',
                      resultRecordCount='1000', orderByFields='OBJECTID')
        raw, receipt = request(URL, params, json_expected=False)
        decoded = gzip.decompress(raw) if raw.startswith(b'\x1f\x8b') else raw
        directory = out / georef
        directory.mkdir(parents=True)
        (directory / 'footprints.json').write_bytes(decoded)
        save(directory / 'request.json', dict(receipt, decodedSHA256=digest(decoded), gzipDecoded=decoded != raw))
        data = read(directory / 'footprints.json')
        assert not data.get('error') and not data.get('exceededTransferLimit')
        csuids = {f['attributes']['BuildingCSUID'] for f in data['features']}
        forms = []
        if csuids:
            command = ['rg', '-l', '-F', '--glob', '*.json']
            for csuid in sorted(csuids):
                command += ['-e', csuid]
            command += ['3d-viewer/city/data/tiles']
            found = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
            assert found.returncode in [0, 1]
            for relative in found.stdout.splitlines():
                tile = ROOT / relative
                refs.append(tile)
                forms.extend(dict(tile=relative, tileSHA256=digest(tile.read_bytes()), building=b)
                             for b in read(tile)['buildings'] if b.get('buildingCSUID') in csuids)
        rows.append(dict(sourceKey=row['sourceKey'], sourceSHA256=row['indexedSourceSHA256'],
                         georef=georef, completeOriginalBoundsHK1980=bounds, nominationBufferMetres=20,
                         officialFeatures=data['features'], viewerFormNominations=forms,
                         viewerUidAssigned=None, identityAccepted=False))
    summary = dict(uids=[], sourceKeys=prior['sourceKeys'], rows=rows, sourceGeometryChanges=0,
                   originalModelPayloadDownloads=0, identityAccepted=False, installationApproved=False,
                   qualification='Current Active footprint records in each complete source bounding envelope plus explicit20m nomination buffer. Root/georef conversion cross-checked. The buffer is only a search region, never an acceptance tolerance. All candidates and source keys preserved; proximity/overlap alone cannot assign identity, declare a source corrupt or grant installation.', publication=False)
    save(out / 'summary.json', summary)
    assert reservations.owns(lease)
    module('unmatched_spatial_probe_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'two-exact-unmatched-source-complete-extent-active-primary-nominations', list(dict.fromkeys(refs)), read(out / 'summary.json'))
    print([dict(georef=r['georef'], activePrimaryRecords=len(r['officialFeatures']),
                viewerNominations=len(r['viewerFormNominations'])) for r in rows], flush=True)


if __name__ == '__main__':
    main()
