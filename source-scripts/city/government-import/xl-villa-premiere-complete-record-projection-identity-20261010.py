"""Consistent complete-record projection census; preserve historical GEOS failure.

The original full-cell verifier unions all projected face records, while the
historical context producer omits zero-area records. Both represent the same
finite source but GEOS returns slightly different float areas. This diagnosis
recomputes both context and verifier with all records; no tolerance changes.
"""
import importlib.util
import json
import uuid
from fractions import Fraction
from pathlib import Path
import numpy as np
import shapely
from run import ROOT, HERE, read, save, digest, reservations, connect, NATIVE_RUN
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from routed_original_cell_identity import verify as routed_verify
from exact_original_georef_cell_identity_20261009 import apply_exact_cell

BATCH = 'government-xl-villa-premiere-complete-record-projection-identity-20261010'
DOC = ROOT / 'docs/astra-city/government-import' / BATCH
OLD = DOC.parent / 'government-xl-villa-premiere-current-original-identity-20261010'
UID = 'landsd/89917:0'


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def main():
    assert not DOC.exists()
    claim = reservations.claim('villa-complete-record-projection-' + str(uuid.uuid4()),
        ['building:' + UID], batch=BATCH, ttl=3600)
    assert claim['ok'], claim
    lease = claim['reservation']
    try:
        before = (ROOT / '3d-viewer/city/data/manifest.json').read_bytes()
        row = read(OLD / 'selection.json.gz')['rows'][0]
        source = ROOT / row['candidate']['path']
        raw = source.read_bytes()
        assert row['uid'] == UID and digest(raw) == row['sourceSHA256']
        triangles = decode_original_world_triangles(raw)
        assert len(triangles) == row['triangles'] == row['native']['model']['triangles']
        with connect() as connection:
            connection.execute('SET TRANSACTION READ ONLY')
            result = connection.execute('SELECT r.result_sha,r.result FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s', (NATIVE_RUN, row['native']['cacheKey'])).fetchone()
            assert result and result[0] == row['native']['resultSha']
            models = [m for m in result[1]['models'] if m['modelId'] == row['modelId']]
            assert models == [row['native']['model']]
        final = module('villa_complete_record_projection_context', 'xl-final-script-pass.py')
        old_projection = final.projection(triangles)
        final.projection = lambda faces: shapely.union_all(shapely.polygons(np.asarray(faces)[:, :, [0, 2]]))
        full_projection = final.projection(triangles)
        low, high = triangles.min(axis=(0, 1)), triangles.max(axis=(0, 1))
        forms = final.load_forms([low[0]-2, low[2]-2, high[0]+2, high[2]+2])
        own = [(b, t) for b, _, t in forms if b['uid'] == UID]
        assert len(own) == 1
        building, tile = own[0]
        assert building['buildingCSUID'] == row['source']['building']['buildingCSUID']
        row['source'] = dict(building=building, tile=tile, tileSHA256=digest((ROOT/'3d-viewer'/tile).read_bytes()))
        context = dict(uid=UID, sourceSHA256=row['sourceSHA256'], identity=final.identity_context(row, triangles, forms),
            neighbourTileHashes={t:digest((ROOT/'3d-viewer'/t).read_bytes()) for _,_,t in forms})
        sources = []
        route_tiles = {}
        for tile_record in json.loads(before)['tiles']:
            path = ROOT / '3d-viewer' / tile_record['url']
            data = path.read_bytes()
            matches = [b for b in json.loads(data)['buildings'] if str(b.get('buildingCSUID') or '')[:10] == row['modelId'][1:11]]
            if matches:
                route_tiles[tile_record['url']] = digest(data)
                sources.extend(dict(building=b, tile=tile_record['url'], tileSHA256=digest(data)) for b in matches)
        routed = routed_verify(raw, row, context, triangles, current_identity=context['identity'], sources=sources)
        binding = dict(uid=UID, sourceSHA256=digest(raw), decodedWorldTrianglesSHA256=digest(triangles.astype('<f8').tobytes()))
        proof = apply_exact_cell(routed, triangles, expected_binding=binding, current_binding=binding)
        proof['exactRouteTileHashes'] = route_tiles
        proof['exactRouteManifestSHA256'] = digest(before)
        # Explicitly certify every excluded historic record as exact zero, not
        # an arbitrary tiny-area omission or changed source triangle.
        area = shapely.area(shapely.polygons(triangles[:, :, [0, 2]]))
        excluded = np.flatnonzero(area <= 1e-10)
        exact_zero = []
        for face in excluded:
            a,b,c = [[Fraction.from_float(float(v)) for v in point] for point in triangles[face][:,[0,2]]]
            cross = (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
            assert cross == 0, 'No omitted nonzero finite facet may be called degenerate'
            exact_zero.append(int(face))
        assert len(exact_zero) == 9176 and len(triangles) == 16669
        assert 'full-source-projection-evidence-differs' not in proof['reasons']
        expected = {'fresh-current-spatial-bound:sourceExcessCoveredByUnrelatedFormsM2','full-source-unrelated-overlap'}
        assert set(proof['reasons']) == expected
        assert (ROOT/'3d-viewer/city/data/manifest.json').read_bytes() == before
        for t,h in {**context['neighbourTileHashes'],**route_tiles}.items():
            assert digest((ROOT/'3d-viewer'/t).read_bytes()) == h
        save(DOC/'selection.json.gz',dict(rows=[row],manifestSHA256=digest(before)))
        save(DOC/'context.json.gz',dict(rows=[context]))
        save(DOC/'identity.json',proof)
        save(DOC/'complete-record-projection-census.json',dict(completeOriginalFaces=len(triangles), worldTrianglesSHA256=binding['decodedWorldTrianglesSHA256'],
            historicalExactlyZeroProjectedFaceIds=exact_zero, exactZeroCount=len(exact_zero), nonzeroProjectedFaces=len(triangles)-len(exact_zero),
            allRecordsIncludedInConsistentContextAndVerifier=True, historicalFilteredUnionAreaM2=old_projection.area,
            completeRecordUnionAreaM2=full_projection.area, rawAreaDifferenceM2=full_projection.area-old_projection.area,
            legacyRawIdentity=read(OLD/'identity.json'), numericToleranceChanges=0, sourceGeometryChanges=0))
        (DOC/'captured-manifest.json').write_bytes(before)
        paths=[Path(__file__),source,OLD/'result.json',OLD/'identity.json',HERE/'routed_original_cell_identity.py',HERE/'government_georef_cell_identity.py',
            HERE/'exact_original_georef_cell_identity_20261009.py',HERE/'exact_packed_world_geometry_20261009.py',HERE/'xl-final-script-pass.py']
        paths += [ROOT/'3d-viewer'/t for t in {**context['neighbourTileHashes'],**route_tiles}]
        result=module('villa_complete_record_census_fence','xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,
            'consistent-complete-original-record-projection-identity-diagnosis-v1',paths,
            dict(uids=[UID],manifestSHA256=digest(before),completeOriginalFaces=len(triangles),exactZeroProjectedFaces=len(exact_zero),
                 rawIdentityPassed=proof['passed'],rawIdentityReasons=proof['reasons'],identityAccepted=False,physicalAccepted=False,
                 historicalProjectionMismatchPreserved=True,numericToleranceChanges=0,
                 qualification='Complete-record geometry context and independent unchanged source verifier use the same full finite source union. Exact Fraction census proves all9176 historically excluded records have zero XZ area, not omitted tiny facets. Historical GEOS numeric variance preserved; only the mismatched bookkeeping is corrected. Both true unrelated-overlap failures remain. No acceptance, geometry/pose or tolerance change.'))
        print(json.dumps(dict(jobId=result['jobId'],reasons=proof['reasons'],manifestSHA256=digest(before))),flush=True)
    finally:
        assert reservations.release(lease)['ok']


if __name__ == '__main__':main()
