"""Capture advertised public schemas only; no feature queries or model processing."""
import concurrent.futures
import datetime
import hashlib
import json
import pathlib
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = ROOT / 'docs/astra-city/government-import/government-xl-unmapped-provider-history-schema-v1-20261013'
BASE = 'https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1637211194312_35158/MapServer'

def capture(item):
    name, url = item
    req = urllib.request.Request(url, headers={'User-Agent': 'HongKongSandbox-Astra/public-schema-audit'})
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    with urllib.request.urlopen(req, timeout=25) as response:
        raw = response.read()
        headers = {k: response.headers[k] for k in ('Date', 'ETag', 'Last-Modified', 'Content-Type') if response.headers.get(k)}
    value = json.loads(raw)
    if value.get('error'):
        raise ValueError(value['error'])
    (OUT / name).write_bytes(raw)
    receipt = {'url': url, 'startedAtUTC': started, 'retrievedAtUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw), 'responseHeaders': headers}
    (OUT / (name + '.request.json')).write_text(json.dumps(receipt, indent=2) + '\n')
    return name, value, receipt

def main():
    OUT.mkdir(parents=True, exist_ok=False)
    names = [('service.json', BASE + '?f=pjson')]
    names += [(f'layer-{i}.json', BASE + f'/{i}?f=pjson') for i in (0, 1000, 1001, 1002, 1003, 1004, 1005)]
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        results = list(pool.map(capture, names))
    service = results[0][1]
    advertised = {x['id'] for k in ('layers', 'tables') for x in service.get(k, [])}
    expected = {0, 1000, 1001, 1002, 1003, 1004, 1005}
    assert advertised == expected, ('Unexpected advertised schema; inspect before declaring audit complete', advertised)
    rows = []
    for name, value, receipt in results[1:]:
        fields = [f['name'] for f in value.get('fields', [])]
        rows.append({'id': value['id'], 'name': value['name'], 'fields': fields, 'relationships': value.get('relationships', []), 'archivingInfo': value.get('archivingInfo'), 'isDataArchived': value.get('isDataArchived'), 'isDataVersioned': value.get('isDataVersioned'), 'lineageFields': [f for f in fields if f.lower() in ('o_bldg_csuid', 'o_geo_refno', 'operation', 'previousbuildingcsuid', 'oldbuildingcsuid')], 'source': receipt})
    report = {'scope': 'Every advertised layer/table in this one public Building MapServer, not all government datasets', 'modelProcessing': False, 'featureQueries': False, 'databaseWrites': False, 'schemas': rows, 'qualification': 'Missing exposed historical-ID fields or archival query support is a public-interface limitation. It does not prove demolition, corruption, permanent non-installability, or a nearby model identity.'}
    (OUT / 'schema-audit.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'schemas': len(rows), 'lineageFieldTables': [r['id'] for r in rows if r['lineageFields']], 'output': str(OUT.relative_to(ROOT))}))

if __name__ == '__main__':
    main()
