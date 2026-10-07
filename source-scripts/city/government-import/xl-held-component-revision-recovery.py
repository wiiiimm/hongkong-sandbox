"""Recover unchanged model bytes from revised archives without changing source identity."""
import importlib.util
import sys
import uuid
import zipfile
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from run import ROOT, HERE, read, save, digest, reservations

def module(name, file):
    spec = importlib.util.spec_from_file_location(name, HERE / file)
    result = importlib.util.module_from_spec(spec); spec.loader.exec_module(result)
    return result

driver = module('revised_component_receipts', 'xl-held-component-recovery.py')
DOC, LOCAL = driver.DOC, driver.LOCAL
sys.path.insert(0, str(HERE.parent / 'enhancement-screening'))
from shape_prepare import canonical_bytes
from download import acquire
from convert import _convert_one

def main():
    previous = read(DOC / 'government-recovery.json')
    frozen = read(DOC / 'selection.json.gz')
    assert not (DOC / 'revised-archive-recovery.json').exists()
    assert digest((ROOT / '3d-viewer/city/data/manifest.json').read_bytes()) == frozen['manifestSHA256']
    held = {r['uid'] for r in previous['rows'] if r['state'] != 'exact-source-ready'}
    rows = [r for r in frozen['rows'] if r['uid'] in held]
    claim = reservations.claim('codex-xl-revised-archive-recovery-' + str(uuid.uuid4()),
        ['building:' + r['uid'] for r in rows], ttl=3600, batch=driver.BATCH)
    assert claim['ok'], claim
    lease = claim['reservation']
    groups = defaultdict(list)
    for row in rows: groups[row['native']['sheet']].append(row)

    def one(sheet, members):
        folder = LOCAL / 'government-source' / sheet
        directory_path = folder / 'directory/result.json'
        directory = read(directory_path)
        assert digest((folder / 'directory/zip-directory.bin').read_bytes()) == directory['directorySHA256']
        wanted = {r['modelId'] for r in members}
        directory['models'] = [m for m in directory['models'] if m['modelId'] in wanted]
        assert {m['modelId'] for m in directory['models']} == wanted
        try:
            transfer = acquire(directory, folder / 'directory/zip-directory.bin', folder / 'revised-original')
            results = []
            packed = folder / 'revised-packed'; packed.mkdir(exist_ok=True)
            with zipfile.ZipFile(folder / 'revised-original' / (sheet + '.zip')) as archive:
                for row in members:
                    try:
                        model = row['native']['model']
                        converted = _convert_one(archive, archive.getinfo(model['sourceEntry']), folder / 'revised-decoded', packed, {}, {'modelId': row['modelId']})
                        raw = canonical_bytes((packed / converted['asset']['asset']).read_bytes(), row['sourceSHA256'])
                        assert len(raw) == model['asset']['bytes']
                        target = ROOT / row['candidate']['path']; target.write_bytes(raw)
                        results.append({'uid': row['uid'], 'sourceSHA256': row['sourceSHA256'],
                            'state': 'exact-source-ready', 'asset': driver.ref(target),
                            'method': 'revised-archive-exact-original-model-bytes',
                            'currentDirectory': driver.ref(directory_path)})
                    except Exception as error:
                        results.append({'uid': row['uid'], 'sourceSHA256': row['sourceSHA256'],
                            'state': 'held-revised-source-bytes-not-proven', 'errorType': type(error).__name__,
                            'currentDirectory': driver.ref(directory_path)})
            receipt = folder / 'revised-recovery.json'
            save(receipt, {'directory': driver.ref(directory_path), 'transfer': transfer, 'rows': results})
            for result in results: result['recoveryEvidence'] = driver.ref(receipt)
            return results
        except Exception as error:
            return [{'uid': r['uid'], 'sourceSHA256': r['sourceSHA256'], 'state': 'held-revised-archive-download-failed',
                'errorType': type(error).__name__, 'currentDirectory': driver.ref(directory_path)} for r in members]
    try:
        results = []
        with ThreadPoolExecutor(max_workers=3) as pool:
            for future in as_completed([pool.submit(one, s, rs) for s, rs in groups.items()]):
                results.extend(future.result()); assert reservations.heartbeat(lease, ttl=3600)
                save(DOC / 'revised-archive-checkpoint.json', {'rows': results, 'expected': len(rows)})
                print({'checked': len(results), 'counts': dict(Counter(r['state'] for r in results))}, flush=True)
        assert {r['uid'] for r in results} == held
        result = driver.persist('revised-xl-archive-exact-original-recovery-v1',
            {'previousRecoveryJobId': previous['jobId'], 'runner': driver.ref(HERE / 'xl-held-component-revision-recovery.py')},
            {'rows': results, 'counts': dict(Counter(r['state'] for r in results)),
             'qualification': 'A revised archive never inherits the old archive identity. Only exact packed original model hash and byte length permit reuse; frozen native inventory is unchanged.'}, lease)
        save(DOC / 'revised-archive-recovery.json', result)
        print({'jobId': result['jobId'], 'counts': result['counts']}, flush=True)
    finally: assert reservations.release(lease)

if __name__ == '__main__': main()
