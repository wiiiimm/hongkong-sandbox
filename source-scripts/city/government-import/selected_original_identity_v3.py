"""Consistent complete-record identity projections for authenticated originals.

Both context and verifier include every original projected face, including exact
verticals. No tolerance, identity guard, pose or source geometry changes.
"""
import argparse
from pathlib import Path
import numpy as np
import shapely
from run import ROOT, HERE, read, save, digest, connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_georef_cell_identity_20261009 import apply_exact_cell
from routed_original_cell_identity import verify as routed_verify


def complete_identity(routed, triangles, binding):
    """Only apply the exact-cell fallback to a valid upstream geographic cell."""
    cell = routed['geographicCell']
    if cell.get('precisionMetres') == 1:
        return apply_exact_cell(routed, triangles, expected_binding=binding, current_binding=binding)
    assert not cell and routed['passed'] is False and routed['reasons'], 'Incomplete upstream cell must retain a failed identity'
    from copy import deepcopy
    proof = deepcopy(routed)
    proof['exactCellFallbackNotApplicable'] = dict(reason='Upstream geographic-cell validation failed; no exact cell exists', rawReasons=list(routed['reasons']))
    return proof


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--batch', required=True)
    parser.add_argument('--capture', required=True)
    args = parser.parse_args()
    assert args.batch.startswith('government-xl-') and '/' not in args.batch
    base = ROOT / 'docs/astra-city/government-import'
    doc, cap = base / args.batch, base / args.capture
    local = HERE / 'local' / args.batch
    assert not doc.exists() and not local.exists()
    _, pins = authenticate(cap)
    path = cap / 'selection.json.gz'
    assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
    selection = read(path)
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == selection['manifestSHA256']
    refs = [Path(__file__), cap / 'result.json', path, manifest]
    final = module('selected_identity_context', HERE / 'xl-final-script-pass.py')
    final.projection = lambda faces: shapely.union_all(shapely.polygons(np.asarray(faces)[:, :, [0, 2]]))
    route_sources = []
    route_hashes = {}
    prefixes = {r['modelId'][1:11] for r in selection['rows']}
    for tile in read(manifest)['tiles']:
        path = ROOT / '3d-viewer' / tile['url']
        raw = path.read_bytes()
        matching = [b for b in read(path)['buildings'] if str(b.get('buildingCSUID') or '')[:10] in prefixes]
        if matching:
            sha = digest(raw)
            route_hashes[tile['url']] = sha
            route_sources.extend(dict(building=b, tile=tile['url'], tileSHA256=sha) for b in matching)
            refs.append(path)
    results = []
    for row in selection['rows']:
        uid = row['uid']
        asset = ROOT / row['candidate']['path']
        assert digest(asset.read_bytes()) == row['sourceSHA256']
        refs.append(asset)
        with connect() as db:
            db.execute('SET TRANSACTION READ ONLY')
            assert db.execute('SELECT result_sha FROM astra_modelling.native_stage_results WHERE cache_key=%s', (row['native']['cacheKey'],)).fetchone() == (row['native']['resultSha'],)
        tri = decode_original_world_triangles(asset.read_bytes())
        assert len(tri) == row['triangles']
        lo, hi = tri.min((0, 1)), tri.max((0, 1))
        forms = final.load_forms([lo[0]-2, lo[2]-2, hi[0]+2, hi[2]+2])
        hashes = {tile: digest((ROOT / '3d-viewer' / tile).read_bytes()) for _, _, tile in forms}
        context = dict(sourceSHA256=row['sourceSHA256'], identity=final.identity_context(row, tri, forms), neighbourTileHashes=hashes)
        subdir = doc / uid.split('/')[1]
        save(subdir / 'context.json', context)
        sources = [s for s in route_sources if str(s['building'].get('buildingCSUID') or '')[:10] == row['modelId'][1:11]]
        routed = routed_verify(asset.read_bytes(), row, context, tri, current_identity=context['identity'], sources=sources)
        binding = dict(uid=uid, sourceSHA256=row['sourceSHA256'], decodedWorldTrianglesSHA256=digest(tri.astype('<f8').tobytes()))
        proof = complete_identity(routed, tri, binding)
        proof.update(exactRouteManifestSHA256=selection['manifestSHA256'], exactRouteTileHashes=route_hashes, completeRecordProjection=True)
        assert 'full-source-projection-evidence-differs' not in proof['reasons']
        save(subdir / 'identity.json', proof)
        refs.extend(ROOT / '3d-viewer' / name for name in hashes)
        result = dict(uid=uid, sourceSHA256=row['sourceSHA256'], passed=proof['passed'], reasons=proof['reasons'])
        results.append(result)
        print(result, flush=True)
    assert digest(manifest.read_bytes()) == selection['manifestSHA256']
    for tile, sha in route_hashes.items():
        assert digest((ROOT / '3d-viewer' / tile).read_bytes()) == sha
    result = dict(uids=[r['uid'] for r in results], rows=results, installationApproved=False, sourceGeometryChanges=0, scriptExternalAICalls=0)
    save(doc / 'summary.json', result)
    refs.extend(path for path in local.rglob('*') if path.is_file())
    refs.extend([HERE / 'xl-final-script-pass.py', HERE / 'exact_packed_world_geometry_20261009.py', HERE / 'exact_original_georef_cell_identity_20261009.py', HERE / 'routed_original_cell_identity.py', HERE / 'government_georef_cell_identity.py'])
    module('selected_identity_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(args.batch, 'selected-exact-original-source-identities', list(dict.fromkeys(refs)), result)


if __name__ == '__main__':
    main()
