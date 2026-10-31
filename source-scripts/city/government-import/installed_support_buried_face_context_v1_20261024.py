"""Retain exact full-face sampled burial details for installed-support diagnostics.
No acceptance or publication; original arrays and canonical sampling unchanged.
"""
import argparse
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate, face_diagnostics
from primrose_compound_foundation_v2_20261015 import module


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for key in ['batch', 'support-checks', 'runtime']:
        p.add_argument('--' + key, required=True)
    a = p.parse_args()
    assert a.batch.startswith('government-xl-') and '/' not in a.batch
    base = ROOT / 'docs/astra-city/government-import'
    out = base / a.batch
    assert not out.exists()
    refs, cache = [Path(__file__)], {}
    def take(batch, path):
        if batch not in cache:
            cache[batch] = authenticate(base / batch)[1]
            refs.append(base / batch / 'result.json')
        assert digest(path.read_bytes()) == cache[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)
    summary = take(a.support_checks, base / a.support_checks / 'summary.json')
    uid, support_uid = summary['supportedUid'], summary['installedSupportUid']
    geometry = take(a.runtime, HERE / 'local' / a.runtime / 'runtime-geometry.json.gz')
    ground = np.asarray(next(r for r in geometry['rows'] if r['uid'] == uid)['drawnGroundGeometry']).reshape(-1, 3, 3)
    final = module('native_support_buried_context', HERE / 'xl-final-script-pass.py')
    rows = []
    for check in summary['rows']:
        mode = check['mode']
        input_ = take(a.support_checks, base / a.support_checks / mode / 'input.json.gz')
        source = input_['rows'][0]
        assert source['uid'] == uid
        position = np.asarray(source['position'], dtype='<f8').reshape(-1, 3)
        triangles = position[np.asarray(source['index']).reshape(-1, 3)]
        support = np.asarray(input_['podium'], dtype='<f8')
        assert digest(triangles.tobytes()) == check['sourceWorldSHA256ByUid'][uid]
        assert digest(support.tobytes()) == check['sourceWorldSHA256ByUid'][support_uid]
        diagnostic = face_diagnostics(final, triangles, np.concatenate([ground, support]))
        assert diagnostic['completeTerrainTriangles'] == check['compoundFoundation']['completeTerrainTriangles']
        assert len(diagnostic['buriedFaces']) == check['compoundFoundation']['fullyBuriedTriangles']
        for face in diagnostic['buriedFaces']:
            t = triangles[face['faceIndex']]
            normal = np.cross(t[1] - t[0], t[2] - t[0])
            face['normal'] = normal.tolist()
            face['areaM2'] = float(np.linalg.norm(normal) / 2)
        row = dict(mode=mode, **diagnostic)
        save(out / (mode + '.json'), row)
        rows.append(row)
        print(dict(mode=mode, buriedFaces=[r['faceIndex'] for r in diagnostic['buriedFaces']]), flush=True)
    result = dict(uids=[uid, support_uid], rows=rows, installationApproved=False,
                  sourceGeometryChanges=0, physicalSupportAccepted=False)
    save(out / 'summary.json', result)
    refs.extend([HERE / 'china_ferry_current_foundations_v1_20261020.py', HERE / 'xl-final-script-pass.py'])
    module('native_buried_context_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch, 'installed-support-complete-source-sampled-buried-face-context', refs, result)


if __name__ == '__main__':
    main()
