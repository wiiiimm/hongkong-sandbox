"""Reuse authenticated recovered ground for complete original foundation/contact checks."""
import argparse
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ['batch', 'capture', 'ground']:
        parser.add_argument('--' + key, required=True)
    parser.add_argument('--uid', action='append', required=True)
    args = parser.parse_args()
    assert args.batch.startswith('government-xl-') and '/' not in args.batch
    base = ROOT / 'docs/astra-city/government-import'
    doc = base / args.batch
    assert not doc.exists()
    refs, pins = [Path(__file__)], {}
    for name in [args.capture, args.ground]:
        _, bound = authenticate(base / name)
        refs.append(base / name / 'result.json')
        for key, sha in bound.items():
            assert key not in pins or pins[key] == sha
            pins[key] = sha
    def take(path):
        assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)
    selected = {r['uid']: r for r in take(base / args.capture / 'selection.json.gz')['rows']}
    runtime = {r['uid']: r for r in take(HERE / 'local' / args.capture / 'runtime-geometry.json.gz')['rows']}
    ground = np.asarray(take(HERE / 'local' / args.ground / 'original-terrain.json.gz')['triangles'])
    final = module('selected_saved_ground_foundation', HERE / 'xl-final-script-pass.py')
    audit = module('selected_saved_ground_contacts', HERE / 'resolve-pass-indexed-parent-clipping.py')
    results = []
    for uid in args.uid:
        row, g = selected[uid], runtime[uid]
        asset = ROOT / row['candidate']['path']
        assert digest(asset.read_bytes()) == row['sourceSHA256'] == g['sourceSHA256']
        refs.append(asset)
        tri = np.asarray(g['position']).reshape(-1, 3)[np.asarray(g['index']).reshape(-1, 3)]
        b = row['source']['building']
        foundation = final.foundation_context(tri, ground, Polygon(b['rings'][0], b['rings'][1:]))
        points, bottom = audit.sample_points(g)
        contact = audit.audit_native(points, bottom, ground)
        result = dict(uid=uid, sourceSHA256=row['sourceSHA256'], foundation=foundation, contact=contact, installationApproved=False)
        save(doc / (uid.split('/')[1] + '.json'), result)
        results.append(result)
        print(dict(uid=uid, faces=foundation['triangles'], covered=foundation['completeTerrainTriangles'], buried=foundation['fullyBuriedTriangles'], contactPassed=contact['passed'], contactReasons=contact['reasons'], lowRimGap=contact['lowRimGapRange']), flush=True)
    result = dict(uids=args.uid, rows=results, installationApproved=False, publication=False, sourceGeometryChanges=0, scriptExternalAICalls=0, qualification='Exact saved original source geometry against authenticated recovered ground. Current terrain composition, identity, neighbours and runtime/browser acceptance remain separate.')
    save(doc / 'summary.json', result)
    refs.extend([HERE / 'xl-final-script-pass.py', HERE / 'resolve-pass-indexed-parent-clipping.py'])
    module('selected_saved_ground_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(args.batch, 'selected-original-recovered-ground-foundation-contact', list(dict.fromkeys(refs)), result)


if __name__ == '__main__':
    main()
