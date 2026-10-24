"""Determine whether the flagged wall failure comes from original source terrain."""
from pathlib import Path
from fractions import Fraction
import numpy as np
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_triangle_pair_column_gap_20261010 import verify

B = 'government-xl-nam-cheong-authentic-wall-context-v1-20261023'
BASE = ROOT / 'docs/astra-city/government-import'
D = BASE / B


def main():
    assert not D.exists()
    refs, pins = [Path(__file__)], {}
    original = 'government-xl-all-200-original-terrain-batch-v2-20261022'
    capture = 'government-xl-nam-cheong-fu-yun-joint-current-v1-20261023-runtime'
    for batch in [original, capture]:
        _, bound = authenticate(BASE / batch)
        pins.update(bound)
        refs.append(BASE / batch / 'result.json')

    def take(path):
        assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    uid = 'landsd/268867:0'
    selected = next(r for r in take(BASE / capture / 'selection.json.gz')['rows'] if r['uid'] == uid)
    checked = next(r for r in take(BASE / original / 'summary.json')['rows'] if r['uid'] == uid)
    assert selected['sourceSHA256'] == checked['sourceSHA256']
    asset = ROOT / selected['candidate']['path']
    assert digest(asset.read_bytes()) == selected['sourceSHA256']
    refs.append(asset)
    face = decode_original_world_triangles(asset.read_bytes())[11390]
    decoder = module('nam_original_terrain_context', HERE / 'xl-second-pass.py')
    proofs, counts = [], []
    for name in checked['sourceTerrainPaths']:
        path = ROOT / name
        metadata = take(path)
        for buffer in metadata.get('buffers', []):
            member = path.parent / buffer['uri']
            assert digest(member.read_bytes()) == pins[str(member.relative_to(ROOT))]
            refs.append(member)
        ground = decoder.terrain_triangles(path)
        xz = ground[:, :, [0, 2]]
        ids = np.flatnonzero(np.all(xz.max(1) >= face[:, [0, 2]].min(0), axis=1) &
                             np.all(xz.min(1) <= face[:, [0, 2]].max(0), axis=1))
        counts.append(dict(path=name, completeOriginalTerrainFaces=len(ground), inclusiveCandidates=len(ids)))
        for i in ids:
            proof = verify(face, ground[i])
            proofs.append(dict(path=name, originalTerrainFace=int(i), proof=proof))
    gaps = [Fraction(p['proof']['exactMinimumFiniteColumnGapM']) for p in proofs
            if p['proof']['exactClosedHorizontalProjectionsMeet']]
    assert gaps
    minimum = min(gaps)
    save(D / 'exact-source-terrain-proofs.json.gz', proofs)
    result = dict(uids=[uid], sourceSHA256=selected['sourceSHA256'], sourceFace=11390,
                  originalSourceFace=face.tolist(), terrainSources=counts,
                  exactMinimumOriginalTerrainGapM=str(minimum), minimumGapM=float(minimum),
                  unchangedClearancePass=minimum >= Fraction(-1, 2),
                  sourceGeometryChanges=0, installationApproved=False,
                  qualification='Exact whole-original-wall versus complete original government terrain context. A failing source-terrain result cannot be repaired by an invented height offset; no approval or threshold waiver.')
    save(D / 'summary.json', result)
    refs.extend(HERE / n for n in ['xl-second-pass.py', 'exact_packed_world_geometry_20261009.py',
                                   'exact_original_triangle_pair_column_gap_20261010.py'])
    module('authentic_wall_context_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        B, 'exact-original-wall-authentic-terrain-context', refs, result)
    print(result, flush=True)


if __name__ == '__main__':
    main()
