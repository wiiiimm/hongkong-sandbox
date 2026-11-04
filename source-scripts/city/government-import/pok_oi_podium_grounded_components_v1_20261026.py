"""Check direct finite terrain contacts of the two isolated original wall shells."""
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts


def main():
    base = ROOT / 'docs/astra-city/government-import'
    prefix = 'government-xl-after-ying-hoi-pok-oi-'
    batch = prefix + 'podium-grounded-components-v1-20261026'
    runtime = prefix + 'pair-bound-ground-v1-20261026'
    attributes = prefix + 'pair-bound-attributes-v1-20261026'
    clearance = prefix + '71329-complete-clearance-v1-20261026'
    recursive = prefix + 'podium-recursive-cap-v1-20261026'
    out = base / batch
    assert not out.exists()
    refs, pins = [Path(__file__)], {}
    def take(n, p):
        if n not in pins:
            pins[n] = authenticate(base / n)[1]
            refs.append(base / n / 'result.json')
        assert digest(p.read_bytes()) == pins[n][str(p.relative_to(ROOT))]
        refs.append(p)
        return read(p)
    selection = take(runtime, base / runtime / 'selection.json.gz')
    uid = 'landsd/71329:0'
    row = next(r for r in selection['rows'] if r['uid'] == uid)
    g = next(r for r in take(runtime, HERE / 'local' / runtime / 'runtime-geometry.json.gz')['rows'] if r['uid'] == uid)
    attrs = take(attributes, base / attributes / 'attributes.json.gz')
    assert attrs['startEndAllInputsVerified']
    attr = next(r for r in attrs['rows'] if r['uid'] == uid)
    asset = ROOT / row['candidate']['path']
    raw = asset.read_bytes()
    assert digest(raw) == row['sourceSHA256'] == g['sourceSHA256'] == attr['sourceSHA256']
    refs.append(asset)
    ground = np.asarray(g['drawnGroundGeometry'], dtype='<f8').reshape(-1, 3, 3)
    ix = np.asarray(attr['completeOriginalIndex']).reshape(-1, 3)
    modes = dict(original=decode_original_world_triangles(raw), **{
        n: np.asarray(attr[k], dtype='<f8').reshape(-1, 3)[ix] for n, k in [
            ('literal', 'completeLiteralWorldPosition'), ('left', 'completeExplicitLeftAssociatedFloat32WorldPosition'),
            ('balanced', 'completeExplicitBalancedFloat32WorldPosition')]})
    results = []
    for mode, tri in modes.items():
        graph = take(recursive, base / recursive / (mode + '.json.gz'))
        ctx = take(clearance, base / clearance / (mode + '.json.gz'))
        assert digest(tri.tobytes()) == graph['sourceWorldSHA256'] == ctx['sourceWorldSHA256']
        assert digest(ground.tobytes()) == ctx['groundSHA256']
        groups = sorted({tuple(r['visitedFaces']) for r in graph['rows']})
        # These are completely explored exact eligible source components, not
        # proximity clusters or inferred contacts across an authored gap.
        assert len(groups) == 2 and all(len(group) == 24 for group in groups)
        byface = {r['sourceFace']: r for r in ctx['rows']}
        rows = []
        for group in groups:
            assert all(tuple(r['visitedFaces']) == group for r in graph['rows'] if r['sourceFace'] in group)
            assert all(i in byface and byface[i]['highestVertexAboveEveryOverlappingGroundFace'] for i in group)
            contacts = exact_finite_contacts(tri, group, ground, range(len(ground)))
            assert contacts['allPairsExamined'] and not contacts['sourceFacesOmitted']
            positive = [c for c in contacts['contacts'] if c['dimension'] > 0 and c['sourcePrimitiveDimensionA'] == c['sourcePrimitiveDimensionB'] == 2]
            rows.append(dict(sourceFaces=list(group), bounds=[tri[list(group)].min((0, 1)).tolist(), tri[list(group)].max((0, 1)).tolist()],
                             positiveTerrainContactPairs=len(positive), contactingSourceFaces=sorted({c['sourceFaceA'] for c in positive}),
                             everyHighestWallVertexExposed=True, directFiniteTerrainContact=bool(positive), completeContacts=contacts))
        detail = dict(mode=mode, sourceWorldSHA256=digest(tri.tobytes()), groundSHA256=digest(ground.tobytes()), rows=rows)
        save(out / (mode + '.json.gz'), detail)
        summary = dict(mode=mode, components=len(rows), faces=sum(len(r['sourceFaces']) for r in rows),
                       positiveTerrainContactPairs=[r['positiveTerrainContactPairs'] for r in rows],
                       allHaveDirectFiniteTerrainContacts=all(r['directFiniteTerrainContact'] for r in rows),
                       everyHighestWallVertexExposed=True)
        results.append(summary); print(summary, flush=True)
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == selection['manifestSHA256']
    refs.extend([manifest, HERE / 'exact_packed_world_geometry_20261009.py', HERE / 'exact_original_finite_triangle_contacts_20261010.py'])
    result = dict(uids=[uid], sourceSHA256=row['sourceSHA256'], rows=results,
                  sourceGeometryChanges=0, sourcePoseChanges=0, physicalAcceptance=False,
                  installationApproved=False, publication=False,
                  qualification='Exact positive-dimensional actual-ground surface contacts of each isolated wall-shell component, with independently pinned exposed upper vertices in all four representations. No roof connection, structural support, source identity or physical/publication approval is inferred.')
    save(out / 'summary.json', result)
    module('pok_oi_grounded_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        batch, 'original-isolated-wall-shell-direct-actual-ground-contact-diagnostic', refs, result)


if __name__ == '__main__':
    main()
