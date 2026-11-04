"""Read-only exact seam census for root-grid cuts through a retained terrain.

No clipping, publication or placement approval. Counts are conservative preflight.
"""
import argparse
from fractions import Fraction
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from coordinated_native_boundary_v1_20261023 import seam_segments, seam_comparison_report, rational


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for k in ['batch', 'inventory', 'terrain-url', 'terrain-receipt']:
        p.add_argument('--'+k, required=True)
    a = p.parse_args()
    assert all(n.startswith('government-xl-') and '/' not in n for n in [a.batch, a.inventory, a.terrain_receipt])
    base = ROOT/'docs/astra-city/government-import'
    out = base/a.batch
    assert not out.exists()
    _, pins = authenticate(base/a.inventory)
    _, terrain_pins = authenticate(base/a.terrain_receipt)
    refs = [Path(__file__), base/a.inventory/'result.json', base/a.terrain_receipt/'result.json']
    manifest = ROOT/'3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == pins[str(manifest.relative_to(ROOT))]
    assert a.terrain_url in [r['url'] if isinstance(r, dict) else r for r in read(manifest)['terrainPatches']]
    path = ROOT/'3d-viewer'/a.terrain_url
    assert path.resolve().is_relative_to((ROOT/'3d-viewer/city/data').resolve())
    assert digest(path.read_bytes()) == terrain_pins[str(path.relative_to(ROOT))]
    terrain = read(path)
    rootpath = ROOT/'3d-viewer'/terrain['meta']['parentTerrain']
    assert digest(rootpath.read_bytes()) == terrain['meta']['parentSha256']
    parent = read(rootpath)
    mesh = terrain['nativeMesh']
    vertices = np.asarray(mesh['position'], dtype=np.float32).astype(float).reshape(-1, 3)
    faces = vertices[np.asarray(mesh['index']).reshape(-1, 3)]
    builder = module('root_cut_builder', HERE/'resolve_pass_indexed_parent_clipping_v2.py')
    sampler = builder.terrain.fine.DemSampler(parent, rendered=True)
    pg = parent['meta']['georef']
    c0, r0, c1, r1 = terrain['coarseCells']
    def point(c, r):
        return pg['bE']+c*pg['aE']-834500, 816500-pg['bN']-r*pg['aN']
    rows = []
    for axis, cuts, other_nodes in [(0, range(c0+1, c1), range(r0, r1+1)), (2, range(r0+1, r1), range(c0, c1+1))]:
        for cut in cuts:
            points = [point(cut, j) if axis == 0 else point(j, cut) for j in other_nodes]
            coordinate = points[0][0 if axis == 0 else 1]
            other = 2 if axis == 0 else 0
            root = sorted([(rational(z if axis == 0 else x), rational(sampler.ground(x, z))) for x, z in points])
            start, end = root[0][0], root[-1][0]
            root_segments = [(u[0], v[0], u[1], v[1], i) for i, (u, v) in enumerate(zip(root, root[1:]))]
            curves = seam_segments(faces, axis, coordinate, float(start), float(end))
            try:
                report = seam_comparison_report(curves, root_segments, float(start), float(end), Fraction(1, 100))
            except AssertionError as error:
                report = dict(passed=False, error=str(error), completeFiniteUpperEnvelopesChecked=False)
            lo, hi = faces[:, :, axis].min(1), faces[:, :, axis].max(1)
            crossing = int(np.count_nonzero((lo < coordinate) & (hi > coordinate)))
            counts = dict(lowerSideOriginalFaces=int(np.count_nonzero(lo < coordinate)), upperSideOriginalFaces=int(np.count_nonzero(hi > coordinate)), facesCrossingCut=crossing, facesExactlyOnCut=int(np.count_nonzero((lo == coordinate) & (hi == coordinate))))
            rows.append(dict(axis=axis, coarseIndex=cut, coordinate=coordinate, **counts, seam=report))
            print(dict(axis=axis, coordinate=coordinate, passed=report['passed'], maximumErrorM=report.get('maximumErrorM'), **counts), flush=True)
    assert digest(manifest.read_bytes()) == pins[str(manifest.relative_to(ROOT))]
    summary = dict(uids=terrain['meta']['targetUids'], terrainURL=a.terrain_url, terrainSHA256=digest(path.read_bytes()), originalFaces=len(faces), rows=rows, rootCompatibleCuts=sum(r['seam']['passed'] for r in rows), sourceGeometryChanges=0, installationApproved=False, qualification='Exact finite Float32 terrain upper envelopes compared to piecewise root-grid sampler heights on every internal coarse-grid cut. Diagnostic only; a clipped candidate must independently preserve the complete old domain, faces, targets, numerical coverage, actual 2mm boundary band and all placement/neighbour/browser/publication gates.')
    save(out/'summary.json', summary)
    refs += [manifest, path, rootpath, HERE/'coordinated_native_boundary_v1_20261023.py', HERE/'resolve_pass_indexed_parent_clipping_v2.py']
    module('root_cut_freeze', HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch, 'retained-native-exact-root-cut-census', refs, summary)


if __name__ == '__main__':
    main()
