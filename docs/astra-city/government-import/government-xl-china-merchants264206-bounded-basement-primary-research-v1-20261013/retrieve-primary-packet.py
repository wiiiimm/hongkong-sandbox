"""Bounded primary-document retrieval only; no project imports or model processing."""
import datetime
import hashlib
import json
from pathlib import Path
import urllib.error
import urllib.request

HERE = Path(__file__).resolve().parent
HEADERS = ('Date', 'ETag', 'Last-Modified', 'Content-Type', 'Content-Length', 'Content-Disposition')
SOURCES = (
    ('shun-tak-owner-circular-20200826.pdf', 'https://www1.hkexnews.hk/listedco/listconews/sehk/2020/0826/2020082600921.pdf'),
    ('china-merchants-owner-contact.html', 'https://www.cmhk.com/main/hdjl/'),
    ('shun-tak-owner-portfolio.html', 'https://www.shuntakgroup.com/en/business/property/portfolio/1045'),
    ('hip-hing-builder-project.html', 'https://www.hiphing.com.hk/en/projects/details.php?id=44'),
    ('mtr-sheung-wan-layout.pdf', 'https://www.mtr.com.hk/archive/ch/services/layouts/shw.pdf'),
)

def main():
    out = HERE / 'primary-documents'
    out.mkdir(exist_ok=False)
    rows = []
    for name, url in SOURCES:
        row = {'requestURL': url, 'requestedUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'filename': name}
        try:
            request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (primary-source provenance research)'})
            with urllib.request.urlopen(request, timeout=60) as response:
                data = response.read(32 * 1024 * 1024 + 1)
                assert len(data) <= 32 * 1024 * 1024, 'document exceeds bounded size'
                row.update(status=response.status, finalURL=response.geturl(), provenanceHeaders={k: response.headers[k] for k in HEADERS if k in response.headers})
            with (out / name).open('xb') as stream:
                stream.write(data)
            row.update(bytes=len(data), sha256=hashlib.sha256(data).hexdigest(), saved=True)
        except Exception as error:
            row.update(saved=False, errorType=type(error).__name__, error=str(error))
            if isinstance(error, urllib.error.HTTPError):
                row.update(status=error.code, finalURL=error.geturl(), provenanceHeaders={k: error.headers[k] for k in HEADERS if k in error.headers})
        rows.append(row)
        print(json.dumps(row, ensure_ascii=False), flush=True)
    receipt = {'kind': 'bounded-primary-document-retrieval', 'headerAllowlist': list(HEADERS), 'sources': rows, 'noModelProcessing': True, 'noDatabaseOrReservations': True, 'acceptanceCredit': False}
    with (HERE / 'retrieval.json').open('x', encoding='utf-8') as stream:
        json.dump(receipt, stream, ensure_ascii=False, indent=2)
        stream.write('\n')

if __name__ == '__main__':
    main()
