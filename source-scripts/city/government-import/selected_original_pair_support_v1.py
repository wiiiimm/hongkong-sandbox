"""Check a captured original source/support pair and bind reusable exact contacts."""
import argparse
import subprocess
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ['batch', 'capture', 'uid', 'support']:
        parser.add_argument('--' + key, required=True)
    parser.add_argument('--saved-contact')
    args = parser.parse_args()
    assert args.batch.startswith('government-xl-') and '/' not in args.batch
    base = ROOT / 'docs/astra-city/government-import'
    doc, cap = base / args.batch, base / args.capture
    assert not doc.exists() and args.uid != args.support
    _, pins = authenticate(cap)
    refs = [Path(__file__), cap / 'result.json']

    def take(path):
        assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    selection = take(cap / 'selection.json.gz')
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == selection['manifestSHA256']
    refs.append(manifest)
    rows = [r for r in selection['rows'] if r['uid'] in [args.uid, args.support]]
    assert len(rows) == 2
    for row in rows:
        path = ROOT / row['candidate']['path']
        assert digest(path.read_bytes()) == row['sourceSHA256']
        refs.append(path)
    runtime = take(HERE / 'local' / cap.name / 'runtime-geometry.json.gz')
    geometry = {g['uid']: g for g in runtime['rows']}
    world = {u: np.asarray(geometry[u]['position'], dtype='<f8').reshape(-1, 3)[np.asarray(geometry[u]['index']).reshape(-1, 3)] for u in [args.uid, args.support]}
    save(doc / 'support-inputs.json', dict(sources=rows, pairs=[dict(uid=args.uid, supportUid=args.support)]))
    tool = HERE / 'original-support-closure-interfaces.mjs'
    with (doc / 'worker.log').open('w') as log:
        subprocess.run(['node', str(tool), str(doc.relative_to(ROOT)) + '/'], cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, check=True)
    checks = read(doc / 'support-checks.json.gz')
    report = next(r for r in checks['rows'] if r['uid'] == args.uid)
    assert report['supportUid'] == args.support
    final = module('selected_pair_foundation', HERE / 'xl-final-script-pass.py')
    ground = np.asarray(geometry[args.uid]['drawnGroundGeometry']).reshape(-1, 3, 3)
    b = next(r['source']['building'] for r in rows if r['uid'] == args.uid)
    foundation = final.foundation_context(world[args.uid], np.concatenate([ground, world[args.support]]), Polygon(b['rings'][0], b['rings'][1:]))
    save(doc / 'foundation.json', foundation)
    reuse = dict(reused=False, resolvedWitnesses=0)
    if args.saved_contact:
        folder = base / args.saved_contact
        _, oldpins = authenticate(folder)
        contactpath = folder / 'contacts.json.gz'
        assert digest(contactpath.read_bytes()) == oldpins[str(contactpath.relative_to(ROOT))]
        refs.extend([folder / 'result.json', contactpath])
        old = read(contactpath)
        assert old['uid'] == args.uid and old['supportUid'] == args.support
        assert old['sourceSHA256'] == geometry[args.uid]['sourceSHA256']
        assert old['supportSHA256'] == geometry[args.support]['sourceSHA256']
        assert old['sourceWorldSHA256'] == digest(world[args.uid].tobytes())
        assert old['supportWorldSHA256'] == digest(world[args.support].tobytes())
        assert [t['witness'] for t in old['targets']] == report['interface']['unresolved']
        reuse = dict(reused=True, resolvedWitnesses=sum(bool(t['positiveContacts']) for t in old['targets']), exactOrderedSourceAndSupportGeometryEqual=True, exactWitnessesEqual=True)
    result = dict(uids=[args.uid, args.support], sourceSHA256=geometry[args.uid]['sourceSHA256'], supportSHA256=geometry[args.support]['sourceSHA256'], strictContacts=report['interface']['strictContacts'], samples=report['interface']['samples'], rawUnresolved=len(report['interface']['unresolved']), contactReuse=reuse, remainingUnexplained=len(report['interface']['unresolved']) - reuse['resolvedWitnesses'], foundation={k: foundation[k] for k in ['triangles', 'completeTerrainTriangles', 'fullyBuriedTriangles', 'fullyBuriedUpwardTriangles']}, installationApproved=False, publication=False, sourceGeometryChanges=0, scriptExternalAICalls=0)
    save(doc / 'summary.json', result)
    for name, sha in checks['inputHashes'].items():
        assert digest((ROOT / name).read_bytes()) == sha
        refs.append(ROOT / name)
    refs.extend([tool, HERE / 'xl-final-script-pass.py'])
    module('selected_pair_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(args.batch, 'selected-original-pair-support-binding', list(dict.fromkeys(refs)), result)
    print(result, flush=True)


if __name__ == '__main__':
    main()
