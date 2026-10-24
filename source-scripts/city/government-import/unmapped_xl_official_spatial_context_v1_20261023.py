"""Look for official footprint records omitted from the current viewer candidates."""
import gzip
import json
import sys
from pathlib import Path
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
sys.path.insert(0, str(HERE.parent / 'landsd-territory'))
from source import request

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-unmapped-two-official-spatial-context-v1-20261023'
URL = 'https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1637211194312_35158/MapServer/0/query'


def main():
    out = BASE / BATCH
    assert not out.exists()
    prior = BASE / 'government-xl-unmapped-two-original-projection-context-v1-20261023'
    _, pins = authenticate(prior)
    # Exact immutable bytes archived by the active installer, never its mutable manifest.
    manifest = HERE / 'local/government-xl-island-cheong-shing-four-source-coordinated-original-installed-v1-20261023/historical-current/3d-viewer/city/data/manifest.json'
    expected = '2b043c8ac2efb31904495002e8528859955bcd2ed0b873261ef32d4ffec3b578'
    assert digest(manifest.read_bytes()) == expected
    origin = read(manifest)['origin']
    assert read(manifest)['crs'] == 'EPSG:2326'
    refs = [Path(__file__), prior / 'result.json', manifest, HERE.parent / 'landsd-territory/source.py']
    rows = []
    out.mkdir()
    for model in ['B349971856402063C0', 'B352981210001063C0']:
        p = prior / (model + '.json.gz')
        assert digest(p.read_bytes()) == pins[str(p.relative_to(ROOT))]
        refs.append(p)
        source = read(p)
        lo, hi = source['worldBounds']['min'], source['worldBounds']['max']
        envelope = dict(xmin=origin[0] + lo[0], xmax=origin[0] + hi[0], ymin=origin[1] - hi[2], ymax=origin[1] - lo[2], spatialReference=dict(wkid=2326))
        found, offset = [], 0
        for page in range(20):
            params = dict(f='json', where='1=1', geometry=json.dumps(envelope, separators=(',', ':')), geometryType='esriGeometryEnvelope', inSR='2326', outSR='2326', spatialRel='esriSpatialRelIntersects', outFields='*', returnGeometry='true', resultRecordCount='1000', resultOffset=str(offset), orderByFields='OBJECTID')
            raw, receipt = request(URL, params, json_expected=False)
            decoded = gzip.decompress(raw) if raw.startswith(b'\x1f\x8b') else raw
            path = out / (model + '-' + str(page) + '.json')
            path.write_bytes(decoded)
            save(path.with_name(path.stem + '-request.json'), dict(**receipt, decodedSHA256=digest(decoded), gzipDecoded=raw != decoded))
            if raw != decoded:
                path.with_suffix('.wire.gz').write_bytes(raw)
            data = read(path)
            assert not data.get('error'), data.get('error')
            features = data['features']
            found.extend(features)
            if not data.get('exceededTransferLimit') and len(features) < 1000:
                break
            assert features
            offset += len(features)
        else:
            raise AssertionError('Spatial response exceeded bounded pagination')
        ids = [f['attributes']['OBJECTID'] for f in found]
        assert len(ids) == len(set(ids))
        existing = {r['buildingCSUID'] for r in source['currentTargets']}
        additional = [f for f in found if f['attributes']['BuildingCSUID'] not in existing]
        row = dict(modelId=model, sourceKey=source['sourceKey'], sourceSHA256=source['sourceSHA256'], sourceWorldBounds=source['worldBounds'], hk1980Envelope=envelope, officialFeatures=found, currentViewerCandidateCSUIDs=sorted(existing), additionalOfficialRecords=additional, sourceIdentityAccepted=False, installationApproved=False)
        rows.append(row)
        print(dict(modelId=model, officialRecords=len(found), additionalOfficialRecords=len(additional), additionalAttributes=[f['attributes'] for f in additional]), flush=True)
    save(out / 'spatial-context.json.gz', dict(origin=origin, crs='EPSG:2326', rows=rows))
    summary = dict(uids=[], sourceKeys=[r['sourceKey'] for r in rows], rows=[dict(modelId=r['modelId'], officialRecords=len(r['officialFeatures']), additionalOfficialRecords=len(r['additionalOfficialRecords'])) for r in rows], sourceGeometryChanges=0, sourceIdentityAccepted=False, installationApproved=False, permanentRejection=False, newlyInstalled=0, scriptExternalAICalls=0, qualification='Official spatial intersection query over exact complete original-source bounds in HK1980 using immutable pre-installation origin. Returned records and any viewer omissions are correspondence candidates only; no UID assignment, geometry changes, ownership/support/placement acceptance or publication.')
    save(out / 'summary.json', summary)
    module('unmapped_spatial_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH, 'unmapped-xl-official-spatial-record-context', refs, summary)


if __name__ == '__main__':
    main()
