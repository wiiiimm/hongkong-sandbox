"""Exact full-facet column clearance for the single flagged original wall."""
from pathlib import Path
from fractions import Fraction
import numpy as np
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_triangle_pair_column_gap_20261010 import verify

B = 'government-xl-nam-cheong-wall-exact-clearance-v1-20261023'
BASE = ROOT / 'docs/astra-city/government-import'
D = BASE / B


def main():
    assert not D.exists()
    refs, pins = [Path(__file__)], {}
    runtime = 'government-xl-nam-cheong-fu-yun-joint-current-v1-20261023-runtime'
    attributes = 'government-xl-nam-cheong-fu-yun-joint-attributes-v1-20261023'
    continuous = 'government-xl-nam-cheong-joint-prephysical-v2-20261023-continuous'
    for batch in [runtime, attributes, continuous]:
        _, bound = authenticate(BASE / batch)
        pins.update(bound)
        refs.append(BASE / batch / 'result.json')

    def take(path):
        assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    uid = 'landsd/268867:0'
    selected = next(r for r in take(BASE / runtime / 'selection.json.gz')['rows'] if r['uid'] == uid)
    geometry = next(r for r in take(HERE / 'local' / runtime / 'runtime-geometry.json.gz')['rows'] if r['uid'] == uid)
    attr = next(r for r in take(BASE / attributes / 'attributes.json.gz')['rows'] if r['uid'] == uid)
    context = take(BASE / continuous / '268867:0.json.gz')
    assert context['continuousAffectedFaces'] == [11390]
    asset = ROOT / selected['candidate']['path']
    assert digest(asset.read_bytes()) == selected['sourceSHA256'] == attr['sourceSHA256']
    refs.append(asset)
    ix = np.asarray(attr['completeOriginalIndex']).reshape(-1, 3)
    modes = {name: np.asarray(attr[key]).reshape(-1, 3)[ix] for name, key in [
        ('literal', 'completeLiteralWorldPosition'),
        ('left', 'completeExplicitLeftAssociatedFloat32WorldPosition'),
        ('balanced', 'completeExplicitBalancedFloat32WorldPosition')]}
    modes['original'] = decode_original_world_triangles(asset.read_bytes())
    ground = np.asarray(geometry['drawnGroundGeometry']).reshape(-1, 3, 3)
    rows = []
    for mode, triangles in modes.items():
        face = triangles[11390]
        xz = ground[:, :, [0, 2]]
        ids = np.flatnonzero(np.all(xz.max(1) >= face[:, [0, 2]].min(0), axis=1) &
                             np.all(xz.min(1) <= face[:, [0, 2]].max(0), axis=1))
        proofs = [dict(groundFace=int(i), proof=verify(face, ground[i])) for i in ids]
        gaps = [Fraction(p['proof']['exactMinimumFiniteColumnGapM']) for p in proofs
                if p['proof']['exactClosedHorizontalProjectionsMeet']]
        assert gaps
        minimum = min(gaps)
        save(D / (mode + '.json.gz'), proofs)
        row = dict(mode=mode, sourceFace=11390, completeGroundFaces=len(ground),
                   inclusiveGroundCandidates=len(ids), exactMinimumGapM=str(minimum),
                   minimumGapM=float(minimum), unchangedClearancePass=minimum >= Fraction(-1, 2))
        rows.append(row)
        print(row, flush=True)
    result = dict(uids=[uid], sourceSHA256=selected['sourceSHA256'], rows=rows,
                  sourceGeometryChanges=0, installationApproved=False,
                  qualification='Exact column diagnostic for the raw failing wall only; no other facet approval, terrain edit or threshold relaxation.')
    save(D / 'summary.json', result)
    refs.extend(HERE / name for name in ['exact_packed_world_geometry_20261009.py',
        'exact_original_triangle_pair_column_gap_20261010.py'])
    module('wall_exact_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        B, 'exact-original-wall-current-terrain-clearance', refs, result)


if __name__ == '__main__':
    main()
