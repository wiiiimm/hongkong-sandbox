"""Resume the authorised Cheung Chau originals without repeating valid recovery.

Fresh output directories bind current immutable source tiles and manifest. Old
captures, failed ZIP-revision attempts and review flags remain untouched. This
only acquires/checks originals; it cannot publish or approve compression.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import shutil
import subprocess
import sys
import uuid
from islands_direct_stage import ROOT, HERE, read, save, sha, rel, module
from run import reservations

BATCH = 'government-islands-cheung-chau-resume-20261106-v2'
DOC = ROOT / 'docs/astra-city/government-import' / BATCH
LOCAL = HERE / 'local' / BATCH


def call(args, log):
    with log.open('w') as stream:
        return subprocess.run([str(x) for x in args], cwd=ROOT, stdout=stream,
                              stderr=subprocess.STDOUT).returncode


def asset_index(rows):
    wanted = {r['sourceSHA256'] for r in rows}
    listing = subprocess.run(['rg', '--files', '--hidden', '--no-ignore', '-g', '*.glb.gz',
                              str(HERE / 'local')], capture_output=True, text=True, check=True)
    found = {}
    for line in listing.stdout.splitlines():
        path = Path(line)
        digest = path.name.removesuffix('.glb.gz')
        if digest in wanted and digest not in found and sha(path) == digest:
            found[digest] = rel(path)
    return found


def freeze():
    assert not DOC.exists() and not LOCAL.exists()
    manifest_path = ROOT / '3d-viewer/city/data/manifest.json'
    manifest = read(manifest_path)
    rows, pins = [], {rel(manifest_path): sha(manifest_path), rel(Path(__file__)): sha(Path(__file__))}
    for offset, count in ((0, 1000), (1000, 1000), (2000, 1000), (3000, 420)):
        p = ROOT / f'docs/astra-city/government-import/government-islands-cheung-chau-{offset:04d}-{count}-20261106/selection.json.gz'
        rows.extend(read(p)['rows']); pins[rel(p)] = sha(p)
    assert len(rows) == len({r['uid'] for r in rows}) == 3420
    installed = {m['uid'] for url in manifest['officialModelCatalogues']
                 for m in read(ROOT / '3d-viewer' / url)['models']}
    assert not installed.intersection(r['uid'] for r in rows)
    for row in rows:
        p = ROOT / '3d-viewer' / row['source']['tile']
        assert sha(p) == row['source']['tileSHA256']
        pins[rel(p)] = row['source']['tileSHA256']
    index = asset_index(rows)
    missing = [r['uid'] for r in rows if r['sourceSHA256'] not in index]
    groups = [{'batch': f'government-xl-islands-cheung-current-v2-{i:03d}-20261106',
               'uids': missing[start:start + 40]}
              for i, start in enumerate(range(0, len(missing), 40), 1)]
    save(DOC / 'selection.json.gz', {'rows': rows, 'manifestSHA256': sha(manifest_path),
                                    'inputHashes': pins, 'installationApproved': False})
    save(DOC / 'recovery-plan.json', {'groups': groups, 'reusedOriginals': len(rows) - len(missing),
                                     'missingOriginals': len(missing), 'models': len(rows),
                                     'originalAssetIndex': index, 'publication': False})
    LOCAL.mkdir(parents=True)
    print({'sources': len(rows), 'reused': len(rows) - len(missing), 'toRecover': len(missing)}, flush=True)


def verify_frozen():
    selected = read(DOC / 'selection.json.gz')
    for path, digest in selected['inputHashes'].items():
        assert sha(ROOT / path) == digest, path
    return selected


def recover(workers):
    selected = verify_frozen()
    plan = read(DOC / 'recovery-plan.json')
    def one(group):
        output = ROOT / 'docs/astra-city/government-import' / group['batch']
        private = HERE / 'local' / group['batch']
        if output.exists() or private.exists():
            raise ValueError('Existing attempt: inspect its exact receipt instead of overwriting')
        log = LOCAL / (group['batch'] + '.log')
        command = [sys.executable, '-u', HERE / 'acquire_current_original_sources_v1_20261024.py',
                   '--batch', group['batch'], *[v for uid in group['uids'] for v in ('--uid', uid)]]
        code = call(command, log)
        result = {'batch': group['batch'], 'models': len(group['uids']), 'exitCode': code, 'log': rel(log)}
        save(DOC / 'groups' / (group['batch'] + '.json'), result)
        print(json.dumps(result), flush=True)
        return result
    with ThreadPoolExecutor(max_workers=workers) as pool:
        outcomes = list(pool.map(one, plan['groups']))
    verify_frozen()
    index = asset_index(selected['rows'])
    missing = [r['uid'] for r in selected['rows'] if r['sourceSHA256'] not in index]
    save(DOC / 'recovered-assets.json', {'assets': index, 'missingUids': missing, 'groups': outcomes,
                                       'sourceGeometryChanges': 0, 'aiCalls': 0, 'publication': False})
    print({'recovered': len(selected['rows']) - len(missing), 'remaining': len(missing)}, flush=True)


def check(shard, owned=False):
    selected = verify_frozen()
    assert 0 <= shard < 4
    rows = selected['rows'][shard * 1000:(shard + 1) * 1000]
    batch = BATCH + f'-check-{shard}'
    doc, local = ROOT / 'docs/astra-city/government-import' / batch, HERE / 'local' / batch
    receipt = local / 'reservation.json'
    if not owned:
        assert not doc.exists() and not local.exists()
        claim = reservations.claim('codex-islands-cheung-' + str(uuid.uuid4()),
                                   ['building:' + r['uid'] for r in rows], batch=batch, ttl=3600)
        assert claim['ok'], 'Existing source owner; no takeover'
        try:
            save(receipt, json.loads(json.dumps(claim['reservation'], default=str)))
            code = call([sys.executable, HERE.parent / 'shared-modelling/reservations.py', 'run',
                         '--lease-file', receipt, '--ttl', '3600', '--', sys.executable, __file__,
                         'check', '--shard', shard, '--owned'], LOCAL / f'checks-{shard}.log')
            assert code == 0, f'Inspect checks-{shard}.log; failed attempt retained'
        finally:
            if reservations.owns(read(receipt)):
                reservations.release(read(receipt))
        return
    assert reservations.owns(read(receipt))
    recovered = read(DOC / 'recovered-assets.json')['assets']
    helper = module('islands_cheung_existing_check', HERE / 'xl-pass.py')
    helper.BATCH, helper.LOCAL, helper.DOC, helper.LIMIT = batch, local, doc, len(rows)
    frozen = {**selected, 'batch': batch, 'rows': rows, 'sourceCommit': subprocess.check_output(
        ['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(), 'aiCalls': 0}
    save(local / 'selection.json.gz', frozen); save(doc / 'selection.json.gz', frozen)
    packed, errors = [], {}
    for row in rows:
        digest = row['sourceSHA256']
        if digest not in recovered:
            errors[row['uid']] = 'Exact original recovery unresolved; see preserved recovery attempts'
            continue
        source = ROOT / recovered[digest]
        assert sha(source) == digest
        target = local / 'recovered/assets' / (digest + '.glb.gz')
        target.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(source, target)
        entry = helper.shape_prepare.entry(row['native'], row['source']['building'])
        assert entry['sha256'] == digest
        packed.append({'uid': row['uid'], 'building': row['source']['building'],
                       'candidate': {'path': rel(target), 'entry': entry}, 'currentNative': None})
    save(local / 'recovered/geometry-inputs.json', {'rows': packed, 'errors': errors, 'aiCalls': 0})
    helper.check_owned()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase', choices=('freeze', 'recover', 'check'))
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--shard', type=int)
    parser.add_argument('--owned', action='store_true')
    args = parser.parse_args()
    assert 1 <= args.workers <= 4
    if args.phase == 'freeze': freeze()
    elif args.phase == 'recover': recover(args.workers)
    else: check(args.shard, args.owned)


if __name__ == '__main__':
    main()
