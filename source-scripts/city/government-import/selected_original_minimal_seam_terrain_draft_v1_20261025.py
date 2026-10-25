"""Private additive seam repair with all original terrain and model bytes retained."""
import argparse
from pathlib import Path
from copy import deepcopy
import numpy as np
import shapely
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from float32_native_seam_cover_v2_20261025 import cover
from float32_coverage import approve_roundoff
from native_patch_resolution import projected_context

BASE = ROOT / 'docs/astra-city/government-import'
def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ('batch', 'previous', 'parent-receipt'):
        parser.add_argument('--' + key, required=True)
    args = parser.parse_args()
    for value in vars(args).values():
        assert value.startswith('government-xl-') and '/' not in value
    BATCH, OLD, PINNED = args.batch, args.previous, args.parent_receipt
    out, local = BASE / BATCH, HERE / 'local' / BATCH
    assert not out.exists() and not local.exists()
    receipt, pins = authenticate(BASE / OLD)
    _, parentpins = authenticate(BASE / PINNED)
    refs = [Path(__file__), HERE / 'float32_native_seam_cover_v2_20261025.py', HERE / 'native_patch_resolution.py', HERE / 'float32_coverage.py', BASE / OLD / 'result.json', BASE / PINNED / 'result.json']
    def take(path, bindings):
        assert digest(path.read_bytes()) == bindings[str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)
    before = take(ROOT / receipt['candidate']['path'], pins)
    parent = take(ROOT / '3d-viewer/city/data/terrain.json', parentpins)
    patch = deepcopy(before)
    helper = module('school_seam_validator', HERE / 'resolve_pass_indexed_parent_clipping_v2.py')
    bounds = helper.extent(patch['coarseCells'], parent)
    proof = cover(patch, bounds)
    assert len(patch['nativeMesh']['index'])//3 <= 25000
    for metadata in (patch['meta']['source'], patch['nativeMesh']['source']):
        metadata['derivedTerrainSeamCover'] = proof
    patch['nativeMesh']['source'].pop('numericalCoverageGap', None)
    out.mkdir(); local.mkdir()
    _, polygons, _, _ = projected_context(patch, bounds)
    if shapely.union_all(polygons).symmetric_difference(shapely.box(*bounds)).area:
        save(out / 'numerical-coverage.json', approve_roundoff(patch, bounds))
    overlap = module('school_seam_overlap', HERE / 'sham_shui_po_pool_shared_terrain_v2_20261016.py')
    overlap.DOC = out
    overlap.overlap_proof(patch, refs)
    save(out / 'before-validation-terrain.json', patch)
    helper.validate_patch(patch, parent)
    candidate = local / 'candidate-terrain.json'
    save(candidate, patch); refs.append(candidate)
    save(out / 'seam-cover-proof.json', proof)
    save(out / 'scope.json', take(BASE / OLD / 'scope.json', pins))
    result = dict(uids=receipt['uids'], sourceSHA256ByUid=receipt['sourceSHA256ByUid'], candidate=dict(path=str(candidate.relative_to(ROOT)), sha256=digest(candidate.read_bytes())), terrainTriangles=len(patch['nativeMesh']['index'])//3, status='private-terrain-validator-passed', seamCover=proof, sourceGeometryChanges=0, sourcePoseChanges=0, installationApproved=False, publication=False, qualification='Private additive repair of 2mm-bounded Float32 seams. All earlier terrain triangles and all source model bytes retained. Full source runtime clearance, exact coverage, neighbours and browser acceptance must be recomputed.')
    save(out / 'summary.json', result)
    refs.extend([HERE / 'resolve_pass_indexed_parent_clipping_v2.py', HERE / 'sham_shui_po_pool_shared_terrain_v2_20261016.py'])
    module('school_seam_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH, 'private-original-additive-float32-terrain-seam-cover', refs, result)
    print({k:v for k,v in result.items() if k!='sourceSHA256ByUid'}, flush=True)


if __name__ == '__main__':
    main()
