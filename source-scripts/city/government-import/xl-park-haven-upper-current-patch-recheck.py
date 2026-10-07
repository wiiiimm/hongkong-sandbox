"""Recheck exact upper original against the unchanged installed low-podium TIN.

This stages replacement routing only, with zero terrain/model geometry changes.
Full current acceptance and retained-native regression checks remain mandatory.
No source projection-overlap guard is bypassed to construct new native terrain.
"""
import argparse
import importlib.util
import json
import subprocess
import sys
import uuid
from pathlib import Path
from types import SimpleNamespace
from run import ROOT, HERE, read, save, digest, reservations, connect

PREVIOUS = 'government-xl-park-haven-upper-podium-unchanged-low-ground-20261007'
INSTALLED = 'government-xl-park-haven-low-podium-installed-20261007'
BASE = Path('docs/astra-city/government-import/government-xl-park-haven-upper-podium-current-inputs-20261007')
URL = 'city/data/government-native-246270-0.json'
SHA = 'f9820f73a85954da92964500179d3ac4f42b4edca203c5def4337f443490e765'
UID = 'landsd/246467:0'
RETAINED = 'landsd/246270:0'


def verified(doc):
    result = read(doc / 'result.json')
    sync = read(doc / 'neon-sync.json')
    assert sync['resultVerified'] and sync['jobId'] == result['jobId']
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',
                           (result['jobId'],)).fetchone() == ('complete', result)
    for ref in result['evidenceRefs']:
        assert digest((ROOT / ref['path']).read_bytes()) == ref['sha256']
    return result


def owned(args, doc, local):
    assert reservations.owns(read(local / 'reservation.json'))
    previous = ROOT / 'docs/astra-city/government-import' / PREVIOUS
    original_result = verified(previous)
    installed_result = verified(ROOT / 'docs/astra-city/government-import' / INSTALLED)
    selection = read(previous / 'selection.json.gz')
    assert [r['uid'] for r in selection['rows']] == [UID]
    manifest_path = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest_path.read_bytes()) == selection['manifestSHA256']
    manifest = read(manifest_path)
    entry = next(p for p in manifest['terrainPatches'] if p['url'] == URL)
    assert entry['sha256'] == SHA
    raw = (ROOT / '3d-viewer' / URL).read_bytes()
    assert digest(raw) == SHA
    patch = read(ROOT / '3d-viewer' / URL)
    assert patch['meta']['targetUids'] == [RETAINED]
    # Copy exact geometry; only target routing metadata is augmented.
    patch['meta']['targetUids'] = [RETAINED, UID]
    path = local / Path(URL).name
    save(path, patch)
    copied = read(path)
    original = read(ROOT / '3d-viewer' / URL)
    assert copied['nativeMesh'] == original['nativeMesh']
    for field in ['elev', 'renderedElev', 'cell', 'coarseCells', 'h', 'w']:
        assert copied[field] == original[field]
    candidate = {'path': str(path.relative_to(ROOT)), 'sha256': digest(path.read_bytes()),
                 'bounds': [2772.5, 1012.5, 2912.5, 1152.5], 'uids': [UID],
                 'triangles': len(patch['nativeMesh']['index']) // 3,
                 'replaces': {'url': URL, 'sha256': SHA, 'retainedUids': [RETAINED]}}
    prepared = ROOT / 'docs/astra-city/government-import' / (args.batch + '-prepared')
    assert not prepared.exists()
    for name in ['selection.json.gz', 'neighbour-inputs.json.gz', 'identity-proof.json',
                 'owned-source-identity.json', 'owned-source-identity-contact.json', 'indexed-preflight.json']:
        save(prepared / name, read(previous / name))
    save(prepared / 'terrain-candidates.json', [candidate])
    sources = [s for native in entry['source']['nativeSources'] for s in native['sourceFiles']]
    for source in sources:
        assert digest((ROOT / source['path']).read_bytes()) == source['sha256']
    save(prepared / 'terrain.json', {'patch': candidate, 'sourceFiles': sources,
                                   'terrainGeometryChanges': 0, 'modelGeometryChanges': 0})
    neighbours = read(prepared / 'neighbour-inputs.json.gz')
    assert any(r['building']['uid'] == RETAINED and r['existingNative'] for r in neighbours['rows'])
    neighbours['patches'] = [candidate]
    save(prepared / 'neighbour-inputs.json.gz', neighbours)
    old_local = HERE / 'local' / PREVIOUS
    for name in ['catalogue.json', 'catalogue-index.json', 'source-forms.json']:
        save(HERE / 'local' / prepared.name / name, read(old_local / name))
    save(prepared / 'unchanged-retained-tin-routing.json', {
        'currentResultJobId': original_result['jobId'], 'installedLowJobId': installed_result['jobId'],
        'retainedURL': URL, 'retainedSHA256': SHA, 'uid': UID, 'retainedUid': RETAINED,
        'runnerSHA256': digest(Path(__file__).read_bytes()), 'publication': False,
        'terrainGeometryChanges': 0, 'modelGeometryChanges': 0, 'scriptExternalAICalls': 0,
        'qualification': 'Unchanged current TIN copy with target routing metadata only; complete physical and retained-native checks required.'})
    spec = importlib.util.spec_from_file_location('full_recheck', HERE / 'xl-cell-installation-recheck.py')
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    checker.owned(SimpleNamespace(previous=str(prepared.relative_to(ROOT)), batch=args.batch, base=BASE), doc, local)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--batch', required=True)
    parser.add_argument('--owned', action='store_true')
    args = parser.parse_args()
    assert Path(args.batch).name == args.batch and args.batch.startswith('government-xl-')
    doc = ROOT / 'docs/astra-city/government-import' / args.batch
    local = HERE / 'local' / args.batch
    if args.owned:
        owned(args, doc, local)
        return
    assert not doc.exists()
    previous = ROOT / 'docs/astra-city/government-import' / PREVIOUS
    scope = {r['building']['uid'] for r in read(previous / 'neighbour-inputs.json.gz')['rows']} | {UID, RETAINED}
    resources = [('building:' if u.startswith('landsd/') else 'source-form:') + u for u in sorted(scope)]
    resources.append('terrain-surface:' + URL)
    claim = reservations.claim('codex-xl-park-haven-current-tin-' + str(uuid.uuid4()), resources, batch=args.batch)
    assert claim['ok'], claim
    save(local / 'reservation.json', json.loads(json.dumps(claim['reservation'], default=str)))
    subprocess.run([sys.executable, str(HERE.parent / 'shared-modelling/reservations.py'), 'run',
                    '--lease-file', str(local / 'reservation.json'), '--', sys.executable, __file__,
                    '--batch', args.batch, '--owned'], cwd=ROOT, check=True)


if __name__ == '__main__':
    main()
