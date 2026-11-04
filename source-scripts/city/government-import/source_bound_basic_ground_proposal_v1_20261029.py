"""Compute private BASIC continuation hints; never edit original data or publish."""
import argparse
from pathlib import Path
import numpy as np
import shapely
from shapely.geometry import Polygon
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for key in ['batch', 'runtime', 'patch']:
        p.add_argument('--' + key, required=True)
    p.add_argument('--uid', action='append', required=True)
    a = p.parse_args()
    base = ROOT / 'docs/astra-city/government-import'
    out = base / a.batch
    assert a.batch.startswith('government-xl-') and '/' not in a.batch and not out.exists()
    _, pins = authenticate(base / a.runtime)
    refs = [Path(__file__), base / a.runtime / 'result.json']

    def take(path):
        assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    selection = take(base / a.runtime / 'selection.json.gz')
    geometry = take(HERE / 'local' / a.runtime / 'runtime-geometry.json.gz')
    _, patch_pins = authenticate(base / a.patch)
    patch_summary_path = base / a.patch / 'summary.json'
    assert digest(patch_summary_path.read_bytes()) == patch_pins[str(patch_summary_path.relative_to(ROOT))]
    patch_summary = read(patch_summary_path)
    assert patch_summary['status'] == 'private-terrain-validator-passed'
    terrain_asset = ROOT / patch_summary['candidate']['path']
    terrain_sha = patch_summary['candidate']['sha256']
    assert digest(terrain_asset.read_bytes()) == terrain_sha == pins[str(terrain_asset.relative_to(ROOT))]
    refs.extend([base / a.patch / 'result.json', patch_summary_path, terrain_asset])
    assert len(a.uid) == len(set(a.uid))
    rows = []
    for uid in a.uid:
        source = next(r for r in selection['rows'] if r['uid'] == uid)
        captured = next(r for r in geometry['rows'] if r['uid'] == uid)
        b = source['source']['building']
        assert b['structureType'] in ['Tower', 'Podium'] and b['baseSource'] == b['heightSource'] == 'landsd'
        assert not b.get('modelGeometry') and b.get('foundationBase') is None and not b.get('nativeFallbackGround')
        assert b['base'] == b['baseHeightHKPD'] and abs(b['base'] + b['height'] - b['topHeightHKPD']) < 1e-9
        asset = ROOT / source['candidate']['path']
        assert digest(asset.read_bytes()) == source['sourceSHA256'] == captured['sourceSHA256']
        assert patch_summary['sourceSHA256ByUid'][uid] == source['sourceSHA256']
        refs.append(asset)
        original = decode_original_world_triangles(asset.read_bytes())
        source_minimum = float(original[:, :, 1].min())
        ground = np.asarray(captured['drawnGroundGeometry'], dtype='<f8').reshape(-1, 3, 3)
        polygon = Polygon(b['rings'][0], b['rings'][1:])
        projections = shapely.polygons(ground[:, :, [0, 2]])
        valid = shapely.area(projections) > 1e-10
        missing = polygon.difference(shapely.union_all(projections[valid]))
        assert missing.is_empty, 'Whole BASIC footprint ground coverage required; no tolerance credit'
        extrema, clipped = [], []
        for i in np.flatnonzero(valid & shapely.intersects(projections, polygon)):
            part = projections[i].intersection(polygon)
            if part.area <= 0:
                continue
            points = shapely.get_coordinates(part)
            t = ground[i]
            n = np.cross(t[1] - t[0], t[2] - t[0])
            assert n[1] != 0
            heights = t[0, 1] - (n[0]*(points[:, 0]-t[0, 0]) + n[2]*(points[:, 1]-t[0, 2]))/n[1]
            extrema.extend(map(float, heights))
            clipped.append(int(i))
        assert extrema
        bottom = b['base'] + (b.get('minimum') or 0)
        proposed = min(extrema)
        # This never supplies a foundation for a genuinely elevated native part.
        assert bottom-proposed > 1 and proposed >= 1.2 and proposed >= source_minimum-.5
        assert max(extrema) < b['base'] + b['height'] - .1
        hint = dict(recipe='original-source-basic-ground-v1', uid=uid, sourceSHA256=source['sourceSHA256'], terrainSHA256=terrain_sha, drawnGroundSHA256=digest(ground.tobytes()), originalBottom=bottom, sourceMinimumY=source_minimum, base=proposed)
        rows.append(dict(uid=uid, originalBuilding=b, proposedBuilding=dict(b, nativeFallbackGround=hint), hint=hint, fullFootprintCoverage=True, missingFootprintAreaM2=float(missing.area), completePositiveProjectionGroundFacesConsidered=int(valid.sum()), clippedGroundFaceIds=clipped, groundRangeHKPD=[min(extrema), max(extrema)], originalRoofTopHKPD=b['base']+b['height'], sourceGeometryChanges=0))
    result = dict(uids=a.uid, rows=rows, viewerIntegrationImplemented=False, privateProposalOnly=True, originalGovernmentGeometryChanges=0, recordedHeightChanges=0, physicalAcceptance=False, collisionAndVisualAcceptance=False, installationApproved=False, publication=False, qualification='Continuous clipped-ground hint for the existing procedural BASIC envelope only. No tile, mesh, roof elevation or source asset is changed. Native part must already extend to the proposed lower band. Explicit source/footprint review, renderer/collision preservation, all affected neighbours, failure/Base-only tests and a fenced publisher contract remain required. This is not an optimisation variant or a published derived model.')
    save(out / 'summary.json', result)
    refs.extend([HERE / 'exact_packed_world_geometry_20261009.py', ROOT / '3d-viewer/city/source-bound-basic-ground.js'])
    module('source_bound_basic_ground_proposal', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch, 'private-source-bound-procedural-basic-ground-proposal', refs, read(out / 'summary.json'))
    print([(r['uid'], r['hint']['originalBottom'], r['hint']['base']) for r in rows], flush=True)


if __name__ == '__main__':
    main()
