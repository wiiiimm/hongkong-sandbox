"""Retry an over-budget private terrain representation with exact consolidation.

Only existing derived terrain is input. Government building geometry is never
edited. Every finite surface and unchanged Float32 vertex is certified by the
existing integer-plane algorithm; all ordinary final guards remain mandatory.
"""
import argparse
import traceback
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_runtime_coplanar_consolidation_20261010 import consolidate


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--batch', required=True)
    p.add_argument('--failed-inset', required=True)
    a = p.parse_args()
    assert a.batch.startswith('government-xl-') and '/' not in a.batch
    base = ROOT / 'docs/astra-city/government-import'
    before, out, local = base / a.failed_inset, base / a.batch, HERE / 'local' / a.batch
    assert not out.exists() and not local.exists()
    _, pins = authenticate(before)
    refs = [Path(__file__), before / 'result.json']

    def take(path):
        assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    failed = take(before / 'summary.json')
    assert failed['status'] == 'bounded-inset-investigation' and failed['reason'] == 'terrain-runtime-budget'
    node = take(before / 'unapproved-terrain.json')
    rootpath = ROOT / '3d-viewer/city/data/terrain.json'
    assert digest(rootpath.read_bytes()) == node['meta']['parentSha256']
    root = read(rootpath)
    refs.append(rootpath)
    context = take(before / 'terrain-source-context.json')
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == context['currentRendererManifestSHA256']
    refs.append(manifest)
    # No earlier coverage/overlap approval transfers to the new triangulation.
    positions = np.asarray(node['nativeMesh']['position']).reshape(-1, 3)
    faces = positions[np.asarray(node['nativeMesh']['index']).reshape(-1, 3)]
    assert len(faces) > 25000 and node['meta']['targetUids'] == failed['uids']
    out.mkdir()
    local.mkdir(parents=True)
    result = dict(uids=failed['uids'], sourceSHA256ByUid=failed['sourceSHA256ByUid'],
                  originalPrivateTerrainFaces=len(faces), sourceGeometryChanges=0,
                  installationApproved=False, publication=False, newlyInstalled=0)
    try:
        after, proof = consolidate(faces)
        assert proof['allOriginalFacesAccounted'] and proof['allDegenerateOriginalsRetained']
        assert np.isfinite(after).all()
        save(out / 'exact-surface-certificate.json.gz', proof)
        result['consolidatedTerrainFaces'] = len(after)
        assert len(after) <= 25000, 'Exact consolidation still exceeds unchanged terrain budget'
        node['nativeMesh']['position'] = after.reshape(-1).tolist()
        node['nativeMesh']['index'] = list(range(after.size // 3))
        node['nativeMesh'].pop('sourceOverlap', None)
        node['nativeMesh']['source'].pop('numericalCoverageGap', None)
        node['nativeMesh']['source']['exactTerrainRepresentationCertificate'] = dict(path=str((out / 'exact-surface-certificate.json.gz').relative_to(ROOT)), sha256=digest((out / 'exact-surface-certificate.json.gz').read_bytes()))
        from float32_coverage import approve_roundoff
        from native_patch_resolution import projected_context
        import shapely
        bounds = module('terrain_budget_extent', HERE / 'resolve_pass_indexed_parent_clipping_v2.py').extent(node['coarseCells'], root)
        _, polygons, _, _ = projected_context(node, bounds)
        if shapely.union_all(polygons).symmetric_difference(shapely.box(*bounds)).area:
            save(out / 'coverage.json', approve_roundoff(node, bounds))
        overlap = module('terrain_budget_overlap', HERE / 'sham_shui_po_pool_shared_terrain_v2_20261016.py')
        overlap.DOC = out / 'overlap'
        overlap.DOC.mkdir()
        overlap.overlap_proof(node, [before / 'unapproved-terrain.json', out / 'exact-surface-certificate.json.gz', Path(__file__)])
        validator = module('terrain_budget_validator', HERE / 'resolve_pass_indexed_parent_clipping_v2.py')
        validator.validate_patch(node, root)
        path = local / 'candidate-terrain.json'
        save(path, node)
        refs.append(path)
        result.update(status='private-terrain-validator-passed', candidate=dict(path=str(path.relative_to(ROOT)), sha256=digest(path.read_bytes())), terrainTriangles=len(after), exactRenderedSurfacePreserved=True)
    except Exception as error:
        result.update(status='exact-terrain-budget-investigation', reason=str(error), errorType=type(error).__name__)
        save(out / 'failure.json', dict(errorType=type(error).__name__, message=str(error), traceback=traceback.format_exc()))
    assert digest(manifest.read_bytes()) == context['currentRendererManifestSHA256']
    result['qualification'] = 'Exact existing integer-plane/edge-chain consolidation of derived terrain only. Unproved/degenerate regions retain literal Float32 facets. No tolerance or25kbudget change; coverage, overlap and canonical root boundary checks rerun. Current actors, full foundations, identity and browser acceptance remain separate.'
    save(out / 'summary.json', result)
    refs.extend(HERE / name for name in ['exact_runtime_coplanar_consolidation_20261010.py', 'exact_coplanar_boundary_census_20261010.py', 'exact_runtime_coplanar_groups_20261010.py', 'resolve_pass_indexed_parent_clipping_v2.py', 'float32_coverage.py', 'native_patch_resolution.py', 'sham_shui_po_pool_shared_terrain_v2_20261016.py'])
    module('exact_terrain_budget_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch, 'exact-existing-derived-terrain-budget-recovery', refs, result)
    print({k: result.get(k) for k in ['status', 'originalPrivateTerrainFaces', 'consolidatedTerrainFaces', 'reason']}, flush=True)


if __name__ == '__main__': main()
