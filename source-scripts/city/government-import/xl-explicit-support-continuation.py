"""Run independent pinned source/support diagnostics without publishing or remodelling."""
import argparse
import json
import subprocess
import sys
from pathlib import Path
from run import ROOT, HERE, read, save, digest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', required=True)
    parser.add_argument('--pairs-file', required=True)
    parser.add_argument('--batch', required=True)
    args = parser.parse_args()
    assert Path(args.batch).name == args.batch and args.batch.startswith('government-xl-')
    base = (ROOT / args.base).resolve()
    pairs_path = (ROOT / args.pairs_file).resolve()
    assert base.is_relative_to(ROOT) and pairs_path.is_relative_to(ROOT)
    pairs = read(pairs_path)['pairs']
    assert 1 <= len(pairs) <= 50
    assert len({(r['uid'], r['supportUid']) for r in pairs}) == len(pairs)
    contexts = {r['uid']: r for r in read(base / 'context.json.gz')['rows']}
    # Intersections select diagnostic candidates, never establish support/identity.
    for pair in pairs:
        assert pair['uid'] != pair['supportUid']
        assert any(r['uid'] == pair['supportUid'] and r['intersectionAreaM2'] > .01
                   for r in contexts[pair['uid']]['identity']['intersectingForms'])
    doc = ROOT / 'docs/astra-city/government-import' / args.batch
    local = HERE / 'local' / args.batch
    assert not doc.exists(), 'Completed evidence is immutable; choose a fresh explicit stage'
    local.mkdir(parents=True, exist_ok=True)
    outcomes = []
    for pair in pairs:
        child = args.batch + '-' + pair['uid'].split('/')[1].replace(':', '-')
        child += '-support-' + pair['supportUid'].split('/')[1].replace(':', '-')
        target = ROOT / 'docs/astra-city/government-import' / child
        assert not target.exists(), 'Never overwrite a previous source/support diagnostic'
        command = [sys.executable, str(HERE / 'xl-exact-support-closure.py'),
                   '--base', args.base, '--batch', child,
                   '--pair', pair['uid'] + '=' + pair['supportUid']]
        log = local / (child + '.log')
        print(json.dumps({'starting': pair, 'completed': len(outcomes), 'total': len(pairs)}), flush=True)
        with log.open('w') as output:
            proc = subprocess.run(command, cwd=ROOT, stdout=output, stderr=subprocess.STDOUT)
        result = read(target / 'result.json') if (target / 'result.json').exists() else None
        outcomes.append({**pair, 'batch': child, 'command': command,
                         'returncode': proc.returncode, 'result': result,
                         'log': str(log.relative_to(ROOT))})
        save(doc / 'working-commands.json', {'batch': args.batch, 'rows': outcomes})
        print(json.dumps({'completed': pair, 'returncode': proc.returncode,
                          'outcomes': result and result['rows']}), flush=True)
    save(doc / 'commands.json', {'batch': args.batch, 'rows': outcomes,
         'pairsFile': {'path': str(pairs_path.relative_to(ROOT)), 'sha256': digest(pairs_path.read_bytes())},
         'primarySources': len({r['uid'] for r in pairs}), 'newlyInstalled': 0,
         'scriptExternalAICalls': 0, 'modelGeometryChanges': 0, 'publication': False,
         'qualification': 'Each pair has its own fenced stage. Exact source lookup and unchanged full-mesh interfaces only; failed lookup commands remain explicit. No support, identity or installation credit from spatial selection.'})


if __name__ == '__main__':
    main()
