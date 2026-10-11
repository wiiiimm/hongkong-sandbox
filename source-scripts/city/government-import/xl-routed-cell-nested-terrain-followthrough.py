"""Route a full-cell-qualified original into an existing composite terrain parent.

Reuse the established nested terrain pipeline and complete source/neighbour gates.
Candidate preparation only; no model, review or publication changes.
"""
import argparse
import importlib.util
import json
import subprocess
import sys
import uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations
from publication_lock import locked_publication

spec = importlib.util.spec_from_file_location('cell_nested_indexed', HERE / 'xl-routed-cell-indexed-terrain-continuation.py')
indexed = importlib.util.module_from_spec(spec)
spec.loader.exec_module(indexed)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ['uid', 'batch', 'base', 'parent']:
        parser.add_argument('--' + key, required=True)
    parser.add_argument('--owned', action='store_true')
    args = parser.parse_args()
    assert Path(args.batch).name == args.batch and args.batch.startswith('government-xl-')
    doc = ROOT / 'docs/astra-city/government-import' / args.batch
    local = HERE / 'local' / args.batch
    manifest = read(ROOT / '3d-viewer/city/data/manifest.json')
    assert args.parent in {r['url'] for r in manifest['terrainPatches']}
    parent = read(ROOT / '3d-viewer' / args.parent)
    assert parent.get('patches') and not parent.get('nativeMesh')
    if args.owned:
        with locked_publication(ROOT):
            assert reservations.owns(read(local / 'reservation.json'))
            save(doc / 'nested-parent-routing.json', {
                'parentURL': args.parent,
                'parentSHA256': digest((ROOT / '3d-viewer' / args.parent).read_bytes()),
                'runnerSHA256': digest(Path(__file__).read_bytes()),
                'modelGeometryChanges': 0, 'scriptExternalAICalls': 0, 'publication': False})
            original = indexed.module
            def configured(name, filename):
                value = original(name, filename)
                if filename == 'xl-routed-cell-contact-resolution.py':
                    value.PARENT_URL = args.parent
                    value.NESTED_PARENT = True
                return value
            indexed.module = configured
            indexed.owned(args, doc, local)
        return
    assert not doc.exists(), 'Fresh nested continuation only'
    row = next(r for r in read(ROOT / args.base / 'check-selection.json.gz')['rows'] if r['uid'] == args.uid)
    source = indexed.module('cell_nested_context', 'xl-final-script-pass.py')
    lo, hi = row['native']['model']['worldBounds']
    scope = {args.uid} | {uid for child in parent['patches'] for uid in child.get('meta', {}).get('targetUids', [])}
    scope.update(b['uid'] for b, _, _ in source.load_forms([lo[0]-2, lo[2]-2, hi[0]+2, hi[2]+2]))
    resources = [('building:' if uid.startswith('landsd/') else 'source-form:') + uid for uid in sorted(scope)]
    resources += ['terrain-patch:' + args.uid, 'terrain-surface:' + args.parent]
    claim = reservations.claim('codex-xl-cell-nested-' + str(uuid.uuid4()), resources, batch=args.batch)
    assert claim['ok'], claim
    save(local / 'reservation.json', json.loads(json.dumps(claim['reservation'], default=str)))
    subprocess.run([sys.executable, str(HERE.parent / 'shared-modelling/reservations.py'), 'run',
        '--lease-file', str(local / 'reservation.json'), '--', sys.executable, __file__,
        *sys.argv[1:], '--owned'], cwd=ROOT, check=True)


if __name__ == '__main__':
    main()
