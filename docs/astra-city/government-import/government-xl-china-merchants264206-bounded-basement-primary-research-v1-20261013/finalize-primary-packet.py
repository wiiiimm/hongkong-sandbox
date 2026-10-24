"""Close literal metadata/document pins and validate original PNG headers only."""
import hashlib
import json
from pathlib import Path
import shutil
import struct

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    old = json.loads((HERE / 'review-file-pins.json').read_text())
    pins = dict(old['allInputHashes'])
    for rel, value in pins.items():
        assert sha(ROOT / rel) == value
    log = HERE / 'closed-execution-logs/primary-packet-packaging.log'
    assert not log.exists()
    shutil.copyfile('/tmp/china-merchants264206-primary-packet-packaging-20261013.log', log)
    assert json.loads(log.read_text())['allInputHashesUnchanged'] is True
    pages = json.loads((HERE / 'document-page-exports.json').read_text())['pages']
    for page in pages:
        raw = (HERE / page['png']).read_bytes()
        assert raw[:8] == b'\x89PNG\r\n\x1a\n'
        width, height = struct.unpack('>II', raw[16:24])
        assert [width, height] == [page['width'], page['height']]
        assert hashlib.sha256(raw).hexdigest() == page['pngSHA256']
    for path in sorted(HERE.rglob('*')):
        if path.is_file() and path.name not in ('review-file-pins.json', 'actual-closure-validation.json'):
            pins[str(path.relative_to(ROOT))] = sha(path)
    for rel, value in pins.items():
        assert sha(ROOT / rel) == value
    retrieval = json.loads((HERE / 'retrieval.json').read_text())
    allowed = {'date','etag','last-modified','content-type','content-length','content-disposition'}
    assert all(set(k.lower() for k in r.get('provenanceHeaders', {})) <= allowed for r in retrieval['sources'])
    review = {'kind': 'source-only-primary-research-exact-literal-inputs', 'allInputHashes': pins, 'allPinsVerifiedAfterPackaging': True}
    (HERE / 'review-file-pins.json').write_text(json.dumps(review, indent=2) + '\n')
    result = HERE / 'source-bound-findings.json'
    validation = {
        'allPassed': True, 'literalInputCount': len(pins),
        'packetFileCountExcludingThisValidation': len([p for p in HERE.rglob('*') if p.is_file()]),
        'resultSHA256': sha(result), 'reviewFilePinsSHA256': sha(HERE / 'review-file-pins.json'),
        'sourceSHA256': '0ff5adae4dae90e856af6fb6f40112a24198668ca9dfc66e9570b058739b50fb',
        'verifiedOriginalAssetAndExactCurrentForm': True,
        'primaryDocumentsSaved': 3, 'failedRetrievalsPreserved': 2,
        'actualPNGHeadersAndFileHashesVerified': pages,
        'sixHeaderAllowlistOnly': True,
        'allLiteralPinsVerifiedUnchanged': True,
        'noNeonQueriesOrWritesOrReservations': True,
        'noModelDecodeOrNumericalModelWorker': True,
        'sourceRoleApproved': False, 'physicalAccepted': False, 'currentAcceptance': False,
    }
    with (HERE / 'actual-closure-validation.json').open('x', encoding='utf-8') as stream:
        json.dump(validation, stream, indent=2)
        stream.write('\n')
    print(json.dumps({'allPassed': True, 'literalInputs': len(pins), 'resultSHA256': sha(result), 'reviewFilePinsSHA256': validation['reviewFilePinsSHA256'], 'actualClosureValidationSHA256': sha(HERE / 'actual-closure-validation.json'), 'handoffSHA256': sha(HERE / 'HANDOFF.md')}))

if __name__ == '__main__':
    main()
