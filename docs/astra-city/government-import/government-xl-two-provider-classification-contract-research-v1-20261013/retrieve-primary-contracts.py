"""Bounded official document retrieval only; no project imports or model work."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import urllib.request

HERE = Path(__file__).resolve().parent
PROVENANCE_HEADERS = frozenset({'date', 'etag', 'last-modified', 'content-type', 'content-length', 'content-disposition'})
SOURCES = [
    ('b1000-metadata.html', 'https://www.hkmapmeta.gov.hk/mcs/home/web/data/lands/b1000.faq.html'),
    ('building-current-metadata.html', 'https://portal.csdi.gov.hk/csdi-webpage/metadata/landsd_rcd_1637211194312_35158/html'),
    ('building-sds.json', 'https://static.csdi.gov.hk/csdi-webpage/view/common/e7924089e0acf0cab097d25225b4ebf00ca961828f282d2232b4e97443cd1d9f'),
    ('building-other-73918.raw', 'https://static.csdi.gov.hk/csdi-webpage/download/common/73918cfc315886f9d2e0a64891fb6b9363db38b34c23ba16ba8a682ac5bc41bc'),
]

def main():
    output = HERE / 'raw-primary'
    output.mkdir(exist_ok=False)
    rows = []
    for name, url in SOURCES:
        started = datetime.now(timezone.utc).isoformat()
        record = {'name': name, 'requestedURL': url, 'requestedAtUTC': started}
        try:
            request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (source-contract-research)'})
            with urllib.request.urlopen(request, timeout=60) as response:
                raw = response.read(15_000_001)
                assert len(raw) <= 15_000_000, 'Document retrieval scope exceeded'
                record.update({'status': response.status, 'finalURL': response.url,
                               'headers': [(k, v) for k, v in response.headers.items() if k.lower() in PROVENANCE_HEADERS], 'byteCount': len(raw),
                               'SHA256': hashlib.sha256(raw).hexdigest()})
            with (output / name).open('xb') as stream:
                stream.write(raw)
        except Exception as error:
            record.update({'errorType': type(error).__name__, 'error': str(error)})
        record['completedAtUTC'] = datetime.now(timezone.utc).isoformat()
        rows.append(record)
        print(json.dumps({k: v for k, v in record.items() if k != 'headers'}), flush=True)
    with (HERE / 'raw-retrieval.json').open('x') as stream:
        json.dump({'scope': 'official classification contract documents only', 'documents': rows,
                   'projectImports': False, 'geometryProcessing': False, 'databaseAccess': False,
                   'leases': False, 'acceptanceCredit': False}, stream, indent=2)
        stream.write('\n')

if __name__ == '__main__':
    main()
