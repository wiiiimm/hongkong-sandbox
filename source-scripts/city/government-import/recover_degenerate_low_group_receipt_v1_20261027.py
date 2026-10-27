"""Recover completed diagnostic plots after a zero-area normal serialization failure."""
import argparse
from PIL import Image
import math
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_low_face_group_views_v2_20261026 import groups


def canonical_facet(record, face, triangle):
    normal = np.cross(triangle[1]-triangle[0], triangle[2]-triangle[0])
    length = float(np.linalg.norm(normal))
    assert record['sourceFace'] == face and record['areaM2'] == length/2
    expected = float(normal[1]/length) if length > 0 else None
    actual = record['signedNormalYRatio']
    if length == 0:
        assert math.isnan(actual), 'Only the observed undefined zero-area normal may be repaired'
    else:
        assert actual == expected and math.isfinite(actual)
    return dict(sourceFace=face, areaM2=length/2, signedNormalYRatio=expected, degenerate=length == 0)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for key in ('batch', 'failed-batch', 'sequence', 'runtime', 'low-faces', 'uid'):
        p.add_argument('--'+key, required=True)
    a = p.parse_args()
    base = ROOT/'docs/astra-city/government-import'
    assert a.batch.startswith('government-xl-') and '/' not in a.batch
    out = base/a.batch
    assert not out.exists()
    failed = base/a.failed_batch
    assert not (failed/'result.json').exists(), 'Never replace a completed receipt'
    assert not (failed/'summary.json').exists(), 'Recovery expects the demonstrated pre-write failure'
    refs = [Path(__file__), HERE/'original_low_face_group_views_v2_20261026.py',
            HERE/'original_low_face_group_views_v3_20261027.py', HERE/'exact_packed_world_geometry_20261009.py']
    command_path = HERE/'local'/a.sequence/'command-0.json'
    command = read(command_path)
    assert digest((HERE/'original_low_face_group_views_v2_20261026.py').read_bytes()) == command['scriptSHA256']
    assert command['command'][1] == str(HERE/'original_low_face_group_views_v2_20261026.py')
    assert command['command'][2:] == ['--batch', a.failed_batch, '--runtime', a.runtime, '--low-faces', a.low_faces, '--uid', a.uid]
    refs.append(command_path)
    log_path = command_path.with_name('phase-0.log')
    log = log_path.read_text()
    assert "save(out/'summary.json',result)" in log and 'Out of range float values' in log and 'nan' in log
    assert '"released": true' in log
    refs.append(log_path)
    pins_by_batch = {}
    def take(name, path):
        if name not in pins_by_batch:
            pins_by_batch[name] = authenticate(base/name)[1]
            refs.append(base/name/'result.json')
        assert digest(path.read_bytes()) == pins_by_batch[name][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)
    selection = take(a.runtime, base/a.runtime/'selection.json.gz')
    source = next(r for r in selection['rows'] if r['uid'] == a.uid)
    asset = ROOT/source['candidate']['path']
    assert digest(asset.read_bytes()) == source['sourceSHA256']
    refs.append(asset)
    tri = decode_original_world_triangles(asset.read_bytes())
    low = take(a.low_faces, base/a.low_faces/'original.json.gz')
    assert digest(tri.astype('<f8').tobytes()) == low['sourceWorldSHA256']
    geometry = next(r for r in take(a.runtime, HERE/'local'/a.runtime/'runtime-geometry.json.gz')['rows'] if r['uid'] == a.uid)
    ground = np.asarray(geometry['drawnGroundGeometry'], dtype='<f8').reshape(-1, 3, 3)
    assert digest(ground.tobytes()) == low['groundSHA256']
    ids = [r['sourceFace'] for r in low['rows']]
    clusters = groups(tri, ids)
    assert len(list(failed.glob('*.png'))) == len(clusters)
    records, exports, degenerates = [], [], []
    for index, cluster in enumerate(clusters, 1):
        t = tri[cluster]
        normals = np.cross(t[:,1]-t[:,0], t[:,2]-t[:,0])
        lengths = np.linalg.norm(normals, axis=1)
        facets = []
        for k, face in enumerate(cluster):
            length = float(np.linalg.norm(np.cross(tri[face,1]-tri[face,0], tri[face,2]-tri[face,0])))
            record = dict(sourceFace=face, areaM2=length/2,
                          signedNormalYRatio=float(normals[k,1]/length) if length else float('nan'))
            facets.append(canonical_facet(record, face, tri[face]))
        degenerates.extend(r['sourceFace'] for r in facets if r['degenerate'])
        records.append(dict(sourceFaces=cluster, bounds=[t.min((0,1)).tolist(), t.max((0,1)).tolist()], facets=facets))
        path = failed/('low-group-'+str(index)+'.png')
        with Image.open(path) as image:
            assert image.size == (2100, 980)
            image.verify()
        refs.append(path)
        exports.append(dict(path=str(path.relative_to(ROOT)), sha256=digest(path.read_bytes())))
    assert degenerates, 'No demonstrated zero-area serialization failure'
    corrected = dict(uids=[a.uid], sourceSHA256=source['sourceSHA256'], completeAffectedFaces=ids,
                     groups=records, pair=None, exports=exports, sourceWorldSHA256=low['sourceWorldSHA256'],
                     groundSHA256=low['groundSHA256'], architectureReview=False, physicalAcceptance=False,
                     installationApproved=False, publication=False,
                     priorSummaryWasWritten=False, imageHashesFirstRegisteredByThisRecovery=True)
    corrected.update(receiptOnlyRecovery=True, failedBatch=a.failed_batch,
                     degenerateSourceFaces=degenerates, rerenderedImages=0,
                     sourceGeometryChanges=0, imagesActuallyViewed=False,
                     qualification='Receipt-only recovery after strict JSON rejected undefined normals on exact zero-area original facets. Every group, face, area and bound is recomputed from authenticated source/ground inputs. The failed producer is hash-bound to its command and the logged summary-write failure; all expected completed PNGs decode at native dimensions and their hashes are first registered here. Undefined normals become null with explicit degenerate=true; no facets are removed or repaired, no images rerendered, no physical/visual/installation approval granted. Historical captured ground remains historical diagnostic context.')
    save(out/'summary.json', corrected)
    module('low_group_receipt_recovery_freeze', HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        a.batch, 'recovered-complete-low-group-diagnostic-receipt-zero-area-normals', refs, corrected)
    print(dict(groups=len(clusters), faces=len(ids), zeroAreaFacets=len(degenerates), imagesRerendered=0), flush=True)


if __name__ == '__main__':
    main()
