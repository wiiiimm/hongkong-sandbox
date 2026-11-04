"""Measure a frozen failed inset's boundary under the unchanged production rule.

Diagnostic only: no proposal edits, tolerance changes or installation approval.
"""
import argparse
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--batch', required=True)
    parser.add_argument('--failed-inset', required=True)
    args = parser.parse_args()
    assert all(n.startswith('government-xl-') and '/' not in n for n in [args.batch, args.failed_inset])
    base = ROOT / 'docs/astra-city/government-import'
    old, out = base / args.failed_inset, base / args.batch
    assert not out.exists()
    receipt, pins = authenticate(old)
    assert receipt['reason'] == 'Native terrain boundary does not join parent heights'
    refs = [Path(__file__), old / 'result.json']

    def take(path):
        assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    scope = take(old / 'scope.json')
    parent = take(ROOT / '3d-viewer/city/data/terrain.json')
    captured = take(HERE / 'local' / args.failed_inset / 'parent.json')
    template = take(HERE / 'local' / args.failed_inset / 'parent-template.json')
    candidate = take(old / 'unapproved-terrain.json')
    builder = module('failed_boundary_builder', HERE / 'resolve_pass_indexed_parent_clipping_v2.py')
    sampler = builder.terrain.fine.DemSampler(parent, rendered=True)
    x0, z0, x1, z1 = scope['bounds']
    rows = []
    for label, vertices in [('captured-parent', captured['triangles']), ('validated-template', template['nativeMesh']['position']), ('failed-candidate', candidate['nativeMesh']['position'])]:
        vertices = np.asarray(vertices).reshape(-1, 3).astype(np.float32).astype(float)
        distances = np.minimum.reduce([abs(vertices[:, 0]-x0), abs(vertices[:, 0]-x1), abs(vertices[:, 2]-z0), abs(vertices[:, 2]-z1)])
        edges = vertices[distances < .002]
        assert len(edges)
        gaps = np.array([y-sampler.ground(x, z) for x, y, z in edges])
        worst = int(np.argmax(abs(gaps)))
        rows.append(dict(kind=label, boundaryVertices=len(edges), failedBoundaryVertices=int(np.count_nonzero(abs(gaps) >= .01)), maximumAbsoluteGapM=float(abs(gaps[worst])), worstVertex=edges[worst].tolist(), signedGapM=float(gaps[worst]), passesExistingBoundaryRule=bool(abs(gaps).max() < .01)))
    assert not rows[-1]['passesExistingBoundaryRule']
    result = dict(uids=receipt['uids'], rows=rows, existingToleranceM=.01, sourceGeometryChanges=0, installationApproved=False, qualification='Frozen failed proposal measured against the unchanged production parent sampler, Float32 vertex conversion and .002m boundary selection. No source, terrain or tolerance edits; no acceptance credit.')
    save(out / 'summary.json', result)
    refs.extend([HERE / 'resolve_pass_indexed_parent_clipping_v2.py', HERE.parent / 'island-detail-integration/native_terrain_validation.py'])
    module('failed_boundary_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(args.batch, 'failed-original-inset-boundary-diagnostic', refs, result)
    print(rows, flush=True)


if __name__ == '__main__':
    main()
