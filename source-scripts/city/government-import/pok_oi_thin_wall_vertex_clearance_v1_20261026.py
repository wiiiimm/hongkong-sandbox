"""Probe every original vertex of wall2699 against all finite current ground facets."""
from pathlib import Path
from fractions import Fraction
import numpy as np
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_triangle_pair_column_gap_20261010 import verify


def main():
    base = ROOT / 'docs/astra-city/government-import'
    prefix = 'government-xl-after-ying-hoi-pok-oi-'
    batch = prefix + 'podium-thin-wall-vertices-v1-20261026'
    runtime, attributes = prefix + 'pair-bound-ground-v1-20261026', prefix + 'pair-bound-attributes-v1-20261026'
    clearance = prefix + '71329-complete-clearance-v1-20261026'
    out = base / batch
    assert not out.exists()
    refs, pins = [Path(__file__)], {}
    def take(n, p):
        if n not in pins:
            pins[n] = authenticate(base / n)[1]; refs.append(base / n / 'result.json')
        assert digest(p.read_bytes()) == pins[n][str(p.relative_to(ROOT))]
        refs.append(p); return read(p)
    selection = take(runtime, base / runtime / 'selection.json.gz')
    uid = 'landsd/71329:0'
    row = next(r for r in selection['rows'] if r['uid'] == uid)
    geometry = next(r for r in take(runtime, HERE / 'local' / runtime / 'runtime-geometry.json.gz')['rows'] if r['uid'] == uid)
    attrs = take(attributes, base / attributes / 'attributes.json.gz'); assert attrs['startEndAllInputsVerified']
    attr = next(r for r in attrs['rows'] if r['uid'] == uid)
    asset = ROOT / row['candidate']['path']; raw = asset.read_bytes()
    assert digest(raw) == row['sourceSHA256'] == attr['sourceSHA256'] == geometry['sourceSHA256']
    refs.append(asset)
    ix = np.asarray(attr['completeOriginalIndex']).reshape(-1, 3)
    modes = dict(original=decode_original_world_triangles(raw), **{
        n: np.asarray(attr[k], dtype='<f8').reshape(-1, 3)[ix] for n, k in [
            ('literal', 'completeLiteralWorldPosition'), ('left', 'completeExplicitLeftAssociatedFloat32WorldPosition'),
            ('balanced', 'completeExplicitBalancedFloat32WorldPosition')]})
    ground = np.asarray(geometry['drawnGroundGeometry'], dtype='<f8').reshape(-1, 3, 3)
    results = []
    for mode, tri in modes.items():
        context = take(clearance, base / clearance / (mode + '.json.gz'))
        assert digest(tri.tobytes()) == context['sourceWorldSHA256']
        assert digest(ground.tobytes()) == context['groundSHA256']
        failed = [r['sourceFace'] for r in context['rows'] if not r['highestVertexAboveEveryOverlappingGroundFace']]
        assert failed == [2699]
        rows = []
        for i, vertex in enumerate(tri[2699]):
            proofs = []
            # Every finite ground facet, including vertical and degenerate ones.
            for j, face in enumerate(ground):
                proof = verify(np.repeat(vertex[None, :], 3, axis=0), face)
                if proof['exactClosedHorizontalProjectionsMeet']:
                    proofs.append(dict(groundFace=j, proof=proof))
            rows.append(dict(vertexIndex=i, originalVertex=vertex.tolist(), finiteGroundProofs=proofs,
                             aboveEveryOverlappingGroundFace=bool(proofs) and all(Fraction(p['proof']['exactMinimumFiniteColumnGapM']) > 0 for p in proofs),
                             minimumGapM=str(min((Fraction(p['proof']['exactMinimumFiniteColumnGapM']) for p in proofs), default=Fraction(0)))))
        detail = dict(mode=mode, sourceFace=2699, completeGroundFaces=len(ground), sourceWorldSHA256=digest(tri.tobytes()),
                      groundSHA256=digest(ground.tobytes()), vertices=rows)
        save(out / (mode + '.json.gz'), detail)
        result = dict(mode=mode, sourceFace=2699, exposedOriginalVertices=[r['vertexIndex'] for r in rows if r['aboveEveryOverlappingGroundFace']],
                      minimumGapByVertexM=[r['minimumGapM'] for r in rows])
        results.append(result); print(result, flush=True)
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == selection['manifestSHA256']
    refs.extend([manifest, HERE / 'exact_packed_world_geometry_20261009.py', HERE / 'exact_original_triangle_pair_column_gap_20261010.py'])
    result = dict(uids=[uid], sourceSHA256=row['sourceSHA256'], rows=results, sourceGeometryChanges=0, sourcePoseChanges=0,
                  installationApproved=False, physicalAcceptance=False, publication=False,
                  qualification='Every original triangle vertex checked against every finite actual-ground facet in each representation. Positive per-vertex exposure is diagnostic evidence, not architectural, support or publication acceptance. Earlier highest-vertex failure retained.')
    save(out / 'summary.json', result)
    module('pok_oi_thin_wall_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        batch, 'complete-three-vertex-exact-actual-ground-clearance-context', refs, result)


if __name__ == '__main__':
    main()
