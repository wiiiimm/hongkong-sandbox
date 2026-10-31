"""Recover exact originals from public government ZIP ranges when R2 is unavailable."""
import importlib.util
import json
import sys
import uuid
import zipfile
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from run import ROOT, HERE, read, save, digest, connect, reservations

spec = importlib.util.spec_from_file_location('component_recovery_receipts', HERE / 'xl-held-component-recovery.py')
driver = importlib.util.module_from_spec(spec); spec.loader.exec_module(driver)
DOC, LOCAL, BATCH, ref, persist = driver.DOC, driver.LOCAL, driver.BATCH, driver.ref, driver.persist
sys.path.insert(0, str(HERE.parent / 'enhancement-screening'))
from shape_prepare import canonical_bytes
from discover import scan
from download import acquire
from convert import _convert_one


def main():
    frozen = read(DOC / 'selection.json.gz'); original = read(DOC / 'restoration.json')
    assert not (DOC / 'government-recovery.json').exists()
    assert digest((ROOT / '3d-viewer/city/data/manifest.json').read_bytes()) == frozen['manifestSHA256']
    with connect() as con:
        assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (original['jobId'],)).fetchone() == ('complete', original)
        directories = dict(con.execute("SELECT DISTINCT ON(sheet) sheet,result-'models' FROM astra_modelling.city_source_directories WHERE sheet=ANY(%s) ORDER BY sheet,created_at DESC", ([r['native']['sheet'] for r in frozen['rows']],)))
    done = {r['uid']: r for r in original['rows'] if r['state'] == 'exact-source-ready'}
    groups = defaultdict(list)
    for row in frozen['rows']:
        if row['uid'] in done:
            assert ref(ROOT / done[row['uid']]['asset']['path']) == done[row['uid']]['asset']
        else: groups[row['native']['sheet']].append(row)
    claim = reservations.claim('codex-xl-original-public-recovery-' + str(uuid.uuid4()), ['building:' + r['uid'] for r in frozen['rows']], ttl=3600, batch=BATCH)
    assert claim['ok'], claim
    lease = claim['reservation']

    def one(sheet, rows):
        folder = LOCAL / 'government-source' / sheet
        prior = directories.get(sheet)
        if not prior:
            return [{'uid': r['uid'], 'sourceSHA256': r['sourceSHA256'], 'state': 'held-official-directory-unavailable'} for r in rows]
        try:
            directory, _ = scan({'SHEETNO': sheet, 'Format_glTF': prior['sourceURL'], 'REVISIONDATE': prior['revision']}, folder / 'directory')
            assert directory['etag'] == prior['etag'] and directory['directorySHA256'] == prior['directorySHA256'], 'Pinned source revision changed'
            wanted = {r['modelId'] for r in rows}; directory['models'] = [m for m in directory['models'] if m['modelId'] in wanted]
            assert {m['modelId'] for m in directory['models']} == wanted, 'Pinned official source model missing'
            download = acquire(directory, folder / 'directory/zip-directory.bin', folder / 'original')
            packed = folder / 'packed'; packed.mkdir(exist_ok=True)
            result = []
            with zipfile.ZipFile(folder / 'original' / (sheet + '.zip')) as archive:
                for row in rows:
                    try:
                        model = row['native']['model']; sha = row['sourceSHA256']
                        converted = _convert_one(archive, archive.getinfo(model['sourceEntry']), folder / 'decoded', packed, {}, {'modelId': row['modelId']})
                        raw = canonical_bytes((packed / converted['asset']['asset']).read_bytes(), sha)
                        assert len(raw) == model['asset']['bytes']
                        target = ROOT / row['candidate']['path']; target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(raw)
                        result.append({'uid': row['uid'], 'sourceSHA256': sha, 'state': 'exact-source-ready', 'method': 'verified-government-original-recovery', 'asset': ref(target)})
                    except Exception as error:
                        result.append({'uid': row['uid'], 'sourceSHA256': row['sourceSHA256'], 'state': 'held-original-byte-recovery-failed', 'errorType': type(error).__name__})
            receipt = folder / 'recovery.json'; save(receipt, {'sheet': sheet, 'directorySHA256': directory['directorySHA256'], 'download': download, 'rows': result})
            for row in result: row['sourceRecovery'] = ref(receipt)
            return result
        except Exception as error:
            return [{'uid': r['uid'], 'sourceSHA256': r['sourceSHA256'], 'state': 'held-official-source-recovery-unavailable', 'errorType': type(error).__name__} for r in rows]

    try:
        print({'governmentSheets': len(groups), 'localReady': len(done)}, flush=True)
        with ThreadPoolExecutor(max_workers=3) as pool:
            futures = [pool.submit(one, sheet, rows) for sheet, rows in groups.items()]
            for future in as_completed(futures):
                rows = future.result(); done.update({r['uid']: r for r in rows})
                assert reservations.heartbeat(lease, ttl=3600)
                save(DOC / 'government-recovery-checkpoint.json', {'rows': list(done.values()), 'expected': len(frozen['rows'])})
                print({'processed': len(done), 'expected': len(frozen['rows']), 'last': dict(Counter(r['state'] for r in rows))}, flush=True)
        assert set(done) == {r['uid'] for r in frozen['rows']}
        result = persist('exact-xl-original-government-recovery-v1', {'previousRestorationJobId': original['jobId'], 'selection': ref(DOC / 'selection.json.gz'), 'runner': ref(Path(__file__).resolve())}, {'rows': list(done.values()), 'counts': dict(Counter(r['state'] for r in done.values())), 'sourceGeometryChanges': 0}, lease)
        save(DOC / 'government-recovery.json', result); save(DOC / 'neon-government-recovery-sync.json', {'jobId': result['jobId'], 'resultVerified': True})
        print({'counts': result['counts'], 'jobId': result['jobId']}, flush=True)
    finally: assert reservations.release(lease)


if __name__ == '__main__': main()
