"""Probe both exact unmatched fixed XL source keys, without assigning viewer IDs."""
import argparse
import gzip
import subprocess
import sys
import uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, connect, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
sys.path.insert(0, str(HERE.parent / 'landsd-territory'))
from source import request

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-two-unmatched-current-primary-probe-v1-20261028'
PRIOR = BASE / 'government-xl-after-north-pair-unfinished-exact-source-inventory-v1-20261028'
URL = 'https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1637211194312_35158/MapServer/0/query'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--owned', action='store_true')
    args = parser.parse_args()
    out, local = BASE / BATCH, HERE / 'local' / BATCH
    leasepath = local / 'reservation.json'
    assert not out.exists()
    _, pins = authenticate(PRIOR)
    priorpath = PRIOR / 'summary.json'
    assert digest(priorpath.read_bytes()) == pins[str(priorpath.relative_to(ROOT))]
    rows = [r for r in read(priorpath)['rows'] if r['uid'] is None]
    assert len(rows) == 2
    if not args.owned:
        assert not local.exists()
        claim = reservations.claim('unmatched-primary-probe-' + str(uuid.uuid4()),
            ['identity-probe:' + r['sourceKey'] for r in rows], batch=BATCH, ttl=1800)
        assert claim['ok']
        return execute_reserved(claim['reservation'], leasepath, [sys.executable, __file__, '--owned'])
    lease = read(leasepath)
    assert reservations.owns(lease)
    refs = [Path(__file__), PRIOR / 'result.json', priorpath, HERE.parent / 'landsd-territory/source.py']
    georefs = [r['sourceKey'].split('/')[1][1:11] for r in rows]
    assert all(g.isdigit() and len(g) == 10 for g in georefs)
    params = dict(f='json', where='GeoRefNo IN (' + ','.join("'" + g + "'" for g in georefs) + ')',
                  outFields='*', returnGeometry='true', outSR='2326', resultRecordCount='1000', orderByFields='OBJECTID')
    raw, receipt = request(URL, params, json_expected=False)
    decoded = gzip.decompress(raw) if raw.startswith(b'\x1f\x8b') else raw
    out.mkdir()
    (out / 'current-footprints.json').write_bytes(decoded)
    save(out / 'current-footprints-request.json', dict(receipt, decodedSHA256=digest(decoded), gzipDecoded=decoded != raw))
    primary = read(out / 'current-footprints.json')
    assert not primary.get('error') and not primary.get('exceededTransferLimit')
    # Exact string-prefix nominations only; geometry and identity acceptance stay separate.
    command = ['rg', '-l', '--glob', '*.json']
    for g in georefs:
        command += ['-e', g]
    command += ['3d-viewer/city/data/tiles']
    matches = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    assert matches.returncode in [0, 1]
    forms = []
    for relative in matches.stdout.splitlines():
        path = ROOT / relative
        refs.append(path)
        forms.extend(dict(tile=relative, building=b) for b in read(path)['buildings']
                     if str(b.get('buildingCSUID', ''))[:10] in georefs)
    resultrows = []
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        for row in rows:
            cache, modelid = row['sourceKey'].split('/')
            native = db.execute("SELECT r.result_sha,m.model FROM astra_modelling.native_stage_results r CROSS JOIN LATERAL jsonb_array_elements(r.result->'models') AS m(model) WHERE r.cache_key=%s AND m.model->>'modelId'=%s", (cache, modelid)).fetchall()
            assert len(native) == 1 and native[0][0] == row['nativeResultSHA256']
            model = native[0][1]
            assert model['asset']['sha256'] == row['indexedSourceSHA256']
            georef = modelid[1:11]
            wantedtype = 'Tower' if modelid[11:13] == '01' else 'Podium'
            official = [f for f in primary['features'] if str(f['attributes']['GeoRefNo']) == georef]
            typed = [f for f in official if f['attributes']['BuildingBlockType'] == wantedtype]
            resultrows.append(dict(sourceKey=row['sourceKey'], indexedSourceSHA256=row['indexedSourceSHA256'],
                nativeResultSHA256=native[0][0], originalNativeModel=model, georef=georef, sourceType=wantedtype,
                currentOfficialFeatures=official, currentTypedFeatures=typed,
                viewerFormNominations=[f for f in forms if str(f['building'].get('buildingCSUID', ''))[:10] == georef],
                viewerUidAssigned=None, identityAccepted=False, installationApproved=False))
    summary = dict(uids=[], sourceKeys=[r['sourceKey'] for r in rows], rows=resultrows,
        primaryFeatureCount=len(primary['features']), sourceGeometryChanges=0, originalModelPayloadDownloads=0,
        qualification='Both fixed source keys remain intact. Fresh exact GeoRef/type primary records and static CSUID-prefix viewer forms are nominations only, not replacement IDs, coverage/placement approval, absence or corruption declarations. No current inventory, model or review row changed.',
        installationApproved=False, publication=False)
    save(out / 'summary.json', summary)
    assert reservations.owns(lease)
    module('unmatched_primary_probe_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'two-exact-unmatched-source-current-primary-and-viewer-form-probe', refs, read(out / 'summary.json'))
    print([dict(sourceKey=r['sourceKey'], official=len(r['currentTypedFeatures']), viewerNominations=len(r['viewerFormNominations'])) for r in resultrows], flush=True)


if __name__ == '__main__':
    main()
