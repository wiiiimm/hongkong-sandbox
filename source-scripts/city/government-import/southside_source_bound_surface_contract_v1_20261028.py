"""Repair numerical exterior holes and run the unchanged full native validator."""
import argparse
import sys
import uuid
from pathlib import Path
import numpy as np
import shapely
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
import native_patch_resolution as patches

BASE = ROOT/'docs/astra-city/government-import'
BATCH = 'government-xl-southside-source-bound-surface-contract-v1-20261028'
DOC, LOCAL = BASE/BATCH, HERE/'local'/BATCH
LEASE = LOCAL/'reservation.json'
CANDIDATE = BASE/'government-xl-southside-source-bound-terrain-candidate-v1-20261028'
MASK = BASE/'government-xl-southside-source-bound-terrain-mask-v1-20261028'


def owned():
    lease = read(LEASE)
    assert reservations.owns(lease) and not DOC.exists()
    refs, pins = [Path(__file__), Path(patches.__file__)], {}
    for batch in [CANDIDATE, MASK]:
        _, bound = authenticate(batch)
        refs.append(batch/'result.json')
        for path, sha in bound.items():
            assert path not in pins or pins[path] == sha
            pins[path] = sha

    def take(path):
        assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    source = take(CANDIDATE/'summary.json')
    assert not source['clippedCoreHeightDriftViolations']
    assert source['allWholeCoreFacesByteCoordinateEqual']
    mask = take(MASK/'summary.json')
    patch = take(ROOT/source['candidate']['path'])
    parentpath = ROOT/'3d-viewer/city/data/terrain.json'
    assert digest(parentpath.read_bytes()) == patch['meta']['parentSha256']
    parent = read(parentpath); refs.append(parentpath)
    builder = module('southside_source_bound_parent_sampler', HERE/'resolve-pass-indexed-parent-clipping.py')
    sampler = builder.terrain.fine.DemSampler(parent, rendered=True)
    bounds = mask['originalDomainExtent']
    protected = shapely.from_wkt(mask['sourceProjectionWKT'])
    before_tri = patches._faces(patch)
    _, _, missing, _ = patches.projected_context(patch, bounds)
    protected_missing = missing.intersection(protected).area
    fill = None
    if protected_missing < 1e-6:
        fill = patches.fill_parent_only_holes(patch, parent, bounds, protected, sampler)
        assert np.array_equal(patches._faces(patch)[:len(before_tri)], before_tri), 'Hole fill changed an existing source/apron face'
    else:
        save(DOC/'protected-gap-negative.json', dict(areaM2=protected_missing, parentFillRefused=True))
    sources = [Path(__file__), Path(patches.__file__), CANDIDATE/'result.json',
               CANDIDATE/'candidate-terrain.json.gz', MASK/'summary.json', parentpath]
    overlap = module('southside_source_bound_overlap_proof', HERE/'sham_shui_po_pool_shared_terrain_v2_20261016.py')
    overlap.DOC = DOC
    overlap.overlap_proof(patch, sources)
    validator = module('southside_source_bound_full_native_validator', HERE.parent/'island-detail-integration/native_terrain_validation.py')
    try:
        validator.validate_native_mesh(patch, parent)
        passed, failure = True, None
    except AssertionError as error:
        passed, failure = False, str(error)
    tri, _, remaining, excess = patches.projected_context(patch, bounds)
    faces = len(patch['nativeMesh']['index'])//3
    candidatepath = DOC/'private-terrain.json'
    save(candidatepath, patch)
    result = dict(uids=['landsd/315025:0'], candidate=dict(path=str(candidatepath.relative_to(ROOT)), sha256=digest(candidatepath.read_bytes())),
                  beforeFaces=source['candidateFaces'], finalFaces=faces, parentOnlyHoleFill=fill,
                  protectedMissingBeforeM2=float(protected_missing), remainingMissingM2=float(remaining.area),
                  projectedOverlapM2=excess, fullUnchangedNativeValidatorPassed=passed, nativeValidatorFailure=failure,
                  runtimeNodeBudgetPassed=faces <= 25000, noExistingFacesChanged=True,
                  singleNodeSurfaceContractPassed=passed and faces <= 25000,
                  terrainGeometryChanges=faces-source['candidateFaces'], publicTerrainGeometryChanges=0,
                  modelGeometryChanges=0, sourceGeometryChanges=0, newlyInstalled=0, publication=False,
                  scriptExternalAICalls=0, aiGeometryModelling=False, identityAccepted=False,
                  physicalAccepted=False, installationApproved=False, permanentRejection=False,
                  qualification='Fresh single-node source-bound candidate. Existing parent-only numerical hole repair is allowed only outside original building projection and appends faces without changing any prior source/apron face. Fresh complete overlap proof and unchanged native coverage/root/source validator; no rectangular/seam acceptance transfer. No BASIC/source/identity/physical/browser or installation acceptance, and no public terrain write.')
    save(DOC/'summary.json', result)
    refs.extend(sources + [Path(builder.__file__), Path(overlap.__file__), Path(validator.__file__)])
    assert reservations.owns(lease)
    checkpoint = module('southside_source_bound_private_checkpoint', HERE/'southside_source_bound_terrain_candidate_v1_20261028.py')
    checkpoint.BATCH, checkpoint.DOC = BATCH, DOC
    refs.append(Path(checkpoint.__file__))
    checkpoint.freeze(list(dict.fromkeys(refs)), result)
    print({k: result[k] for k in ['finalFaces', 'protectedMissingBeforeM2', 'remainingMissingM2',
                                'fullUnchangedNativeValidatorPassed', 'nativeValidatorFailure', 'runtimeNodeBudgetPassed']}, flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--owned', action='store_true')
    args = parser.parse_args()
    if args.owned:
        return owned()
    assert not DOC.exists() and not LOCAL.exists()
    authenticate(MASK)
    mask = read(MASK/'summary.json')
    resources = {'building:' + u for u in mask['uids']}
    resources.update('building:' + r['uid'] for r in mask['outsideForms'])
    resources.add('terrain:city/data/terrain.json')
    claim = reservations.claim('southside-source-bound-surface-' + str(uuid.uuid4()), sorted(resources), batch=BATCH, ttl=3600)
    assert claim['ok']
    execute_reserved(claim['reservation'], LEASE, [sys.executable, __file__, '--owned'])


if __name__ == '__main__':
    main()
