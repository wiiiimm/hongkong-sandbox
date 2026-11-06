"""Recover unattempted peers after a current source directory omitted one model.

Directory membership is nomination only. The existing original-source helper
repeats all current source/CRC/byte identity checks under fresh leases. Missing
authored IDs retain explicit exceptions; no substitute geometry is fabricated.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import subprocess
import sys
from islands_direct_stage import ROOT, HERE, read, save, sha, rel
import islands_cheung_chau_resume as campaign


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--attempt', type=int, required=True)
    a = p.parse_args(); assert 1 <= a.attempt <= 9
    out = campaign.DOC / f'repair-{a.attempt}'
    assert not out.exists()
    selected = campaign.verify_frozen()
    sources = {r['uid']: r for r in selected['rows']}
    plan = read(campaign.DOC / 'recovery-plan.json')
    results = {r['batch']: r for p in (campaign.DOC / 'groups').glob('*.json') for r in [read(p)]}
    index = campaign.asset_index(selected['rows'])
    nominations, absent = [], []
    for group in plan['groups']:
        if group['batch'] not in results or results[group['batch']]['exitCode'] == 0:
            continue
        local = HERE / 'local' / group['batch']
        wanted = []
        for uid in group['uids']:
            row = sources[uid]
            if row['sourceSHA256'] in index:
                continue
            directories = list((HERE / 'local').glob(
                'government-xl-islands-cheung-current-v2-*/sheets/' + row['native']['sheet'] + '/directory/result.json'))
            if not directories:
                wanted.append(uid)
                continue
            directory = max(directories, key=lambda p: p.stat().st_mtime_ns)
            snapshot = read(directory)
            assert sha(directory.parent / 'zip-directory.bin') == snapshot['directorySHA256']
            model = row['modelId']
            if model in {m['modelId'] for m in snapshot['models']}:
                wanted.append(uid)
            else:
                absent.append({'uid': uid, 'expectedOriginalModelId': model, 'sheet': row['native']['sheet'],
                    'directory': {'path': rel(directory), 'sha256': sha(directory)},
                    'sameGeoRefModels': [m['modelId'] for m in snapshot['models'] if m['modelId'][1:11] == model[1:11]],
                    'reason': 'Expected original model ID absent from this captured current archive; investigate source/profile revision',
                    'governmentWideAbsenceEstablished': False, 'sourceCorruptionEstablished': False})
        if wanted:
            nominations.append({'batch': group['batch'] + f'-repair-{a.attempt}', 'uids': wanted})
    save(out / 'plan.json', {'groups': nominations, 'sourceExceptions': absent,
                             'currentManifestSHA256': selected['manifestSHA256'], 'publication': False})
    def one(group):
        assert not (HERE / 'local' / group['batch']).exists()
        log = out / (group['batch'] + '.log')
        with log.open('x') as stream:
            code = subprocess.run([sys.executable, '-u', HERE / 'acquire_current_original_sources_v1_20261024.py',
                '--batch', group['batch'], *[v for uid in group['uids'] for v in ('--uid', uid)]],
                cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT).returncode
        result = {'batch': group['batch'], 'models': len(group['uids']), 'exitCode': code, 'log': rel(log)}
        save(out / 'groups' / (group['batch'] + '.json'), result)
        print(result, flush=True)
        return result
    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(one, nominations))
    campaign.verify_frozen()
    save(out / 'summary.json', {'groups': outcomes, 'sourceExceptions': absent,
                                'sourceGeometryChanges': 0, 'newlyInstalled': 0, 'aiCalls': 0})


if __name__ == '__main__':
    main()
