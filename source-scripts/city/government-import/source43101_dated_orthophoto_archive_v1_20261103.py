"""Acquire one official dated primary raster archive under a hard transfer cap.

No geometry, identity, placement or installation approval. Large immutable bytes
stay in the ignored component-local cache; hashes/provenance are frozen in Neon.
"""
import json
import shutil
import ssl
import subprocess
import sys
import urllib.request
import uuid
import zipfile
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from observed_reserved_runner_v2_20261103 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
from bounded_response_file_v1_20261103 import receive

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-source43101-dated-orthophoto-archive-v1-20261103'
INDEX = 'government-xl-source43101-dated-orthophoto-index-v1-20261103'
HEADERS = 'government-xl-source43101-dated-orthophoto-header-v4-20261103'
CAP = 750_000_000


def owned():
    local, out = HERE / 'local' / BATCH, BASE / BATCH
    lease = read(local / 'reservation.json')
    assert reservations.owns(lease) and shutil.disk_usage(local.parent).free > 2_000_000_000
    refs = [Path(__file__), HERE / 'bounded_response_file_v1_20261103.py']
    def take(batch, name, structured=True):
        _, pins = authenticate(BASE / batch)
        path = BASE / batch / name
        assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
        refs.extend([BASE / batch / 'result.json', path])
        return read(path) if structured else path
    index = take(INDEX, 'summary.json')
    headers = take(HEADERS, 'summary.json')
    attrs = index['coveringFeatures'][0]['attributes']
    assert len(index['coveringFeatures']) == 1 and attrs['YEAR_OF_RELEASE'] == 2025 and attrs['SHEETNO'] == 'T8-SW-C'
    url = attrs['DOWNLOAD_LINK']
    assert url == headers['downloadURL'] and headers['observedResponse']['httpStatus'] == 200
    cert = take(HEADERS, 'official-intermediate.pem', False)
    trust = Path(ssl.get_default_verify_paths().cafile)
    subprocess.run(['openssl', 'verify', '-CAfile', str(trust), str(cert)], check=True)
    context = ssl.create_default_context()
    context.load_verify_locations(cafile=str(cert))
    assert context.check_hostname and context.verify_mode == ssl.CERT_REQUIRED
    opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=context))
    archive = local / 'TDOP_TIFF_8SWC.zip'
    transfer = dict(url=url, capBytes=CAP, reservedBytes=CAP, receivedBytes=0, status='reserved', bodyRetries=0,
                    tlsHostnameVerification=True, certificateVerification='CERT_REQUIRED', systemTrustStoreSHA256=digest(trust.read_bytes()))
    save(out / 'transfer.json', transfer)
    try:
        with opener.open(urllib.request.Request(url), timeout=60) as response:
            assert response.status == 200 and response.url == url
            assert response.headers.get('Content-Disposition') == 'attachment; filename="TDOP_TIFF_8SWC.zip"'
            assert 'zip' in response.headers.get('Content-Type', '')
            length = response.headers.get('Content-Length')
            assert length is None or 0 < int(length) <= CAP
            transfer['responseHeaders'] = dict(response.headers.items())
            def checkpoint(count):
                transfer['receivedBytes'] = count
                save(out / 'transfer.json', transfer)
            result = receive(response, archive, CAP, checkpoint)
        assert reservations.owns(lease)
        with zipfile.ZipFile(archive) as z:
            members = z.infolist()
            assert 1 <= len(members) <= 100 and len({m.filename for m in members}) == len(members)
            assert all(not m.flag_bits & 1 and not Path(m.filename).is_absolute() and '..' not in Path(m.filename).parts for m in members)
            assert sum(m.file_size for m in members) <= 2_000_000_000
            inventory = [dict(name=m.filename, compressedBytes=m.compress_size, rawBytes=m.file_size, compression=m.compress_type, crc32=m.CRC) for m in members]
        transfer.update(result, status='complete', archive=str(archive.relative_to(ROOT)), archiveDirectoryComplete=True)
        save(out / 'transfer.json', transfer)
        summary = dict(uids=index['uids'], sourceSHA256=index['sourceSHA256'], officialIndexAttributes=attrs,
                       originalArchive=transfer, archiveMembers=inventory, completeMemberCRCsChecked=False,
                       rasterPixelsDecoded=False, sourceGeometryChanges=0, sourcePoseChanges=0,
                       identityAccepted=False, installationApproved=False, publication=False, permanentRejection=False,
                       qualification='One exact official dated orthophoto sheet acquired under750MB cap after bounded range refusal. ZIP directory validated; member CRC/raster georeference and pixels still require independent checks. The index date is not transferred to unrelated XYZ images. No model acceptance.')
        save(out / 'summary.json', summary)
        refs.extend(p for p in out.iterdir() if p.is_file())
        module('source43101_dated_archive_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH, 'bounded-official-dated-orthophoto-archive-acquisition', refs, summary)
        print(json.dumps(dict(complete=True, receivedBytes=result['receivedBytes'], members=inventory)), flush=True)
    except Exception as error:
        transfer.update(status='failed-partial-preserved-no-retry', errorClass=type(error).__name__, error=str(error),
                        retainedPartialBytes=archive.stat().st_size if archive.exists() else 0)
        save(out / 'transfer.json', transfer)
        raise


if __name__ == '__main__':
    if '--owned' in sys.argv:
        owned()
    else:
        assert not (BASE / BATCH).exists() and not (HERE / 'local' / BATCH).exists()
        claim = reservations.claim('source43101-dated-archive-' + str(uuid.uuid4()), ['building:landsd/43101:0', 'immutable-source-proof:' + BATCH], batch=BATCH, ttl=3600)
        assert claim['ok'], 'Source reservation unavailable'
        execute_reserved(claim['reservation'], HERE / 'local' / BATCH / 'reservation.json', [sys.executable, __file__, '--owned'])
