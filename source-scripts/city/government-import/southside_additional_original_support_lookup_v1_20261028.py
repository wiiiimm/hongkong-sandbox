"""Find additional original government units intersecting the project, including unmatched units."""
from pathlib import Path
import shapely
from run import ROOT, HERE, read, save, digest, connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module

BASE = ROOT/'docs/astra-city/government-import'
BATCH = 'government-xl-southside-additional-original-support-lookup-v1-20261028'
DOC = BASE/BATCH
GROUND = BASE/'government-xl-la-marina-southside-original-terrain-v1-20261028'
MASK = BASE/'government-xl-southside-source-bound-terrain-mask-v1-20261028'
CAP = BASE/'government-xl-southside-project-original-recovery-v1-20261028'


def main():
    assert not DOC.exists()
    refs, pins = [Path(__file__)], {}
    for batch in [GROUND, MASK, CAP]:
        _, bound = authenticate(batch)
        refs.append(batch/'result.json')
        for path, sha in bound.items():
            assert path not in pins or pins[path] == sha
            pins[path] = sha

    def take(path):
        assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    mask = take(MASK/'summary.json')
    shape = shapely.from_wkt(mask['sourceProjectionWKT'])
    west, north, east, south = shape.bounds
    inputs = take(GROUND/'source-inputs.json')['inputs']
    originals = take(CAP/'selection.json.gz')['rows']
    known = {r['native']['cacheKey'] + '/' + r['modelId'] for r in originals}
    matches, records = [], []
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        for sheet, source in inputs.items():
            cache = source['cacheKey']
            assert db.execute('SELECT result_sha FROM astra_modelling.native_stage_results WHERE cache_key=%s', (cache,)).fetchone() == (source['resultSHA256'],)
            unknown = db.execute("SELECT count(*) FROM astra_modelling.native_stage_results s CROSS JOIN LATERAL jsonb_array_elements(s.result->'models') m WHERE s.cache_key=%s AND (m->'worldBounds' IS NULL OR m->'worldBounds'='null'::jsonb)", (cache,)).fetchone()[0]
            models = db.execute("""SELECT m FROM astra_modelling.native_stage_results s
                CROSS JOIN LATERAL jsonb_array_elements(s.result->'models') m
                WHERE s.cache_key=%s AND (m->'worldBounds'->0->>0)::double precision <= %s
                AND (m->'worldBounds'->1->>0)::double precision >= %s
                AND (m->'worldBounds'->0->>2)::double precision <= %s
                AND (m->'worldBounds'->1->>2)::double precision >= %s""", (cache, east, west, south, north)).fetchall()
            records.append(dict(sheet=sheet, cacheKey=cache, nativeResultSHA256=source['resultSHA256'],
                                boundingMatches=len(models), unitsWithUnknownBounds=unknown))
            for model, in models:
                low, high = model['worldBounds']
                rectangle = shapely.box(low[0], low[2], high[0], high[2])
                intersection = rectangle.intersection(shape)
                if intersection.is_empty:
                    continue
                key = cache + '/' + model['modelId']
                matches.append(dict(sourceKey=key, sheet=sheet, nativeCacheKey=cache,
                                    nativeResultSHA256=source['resultSHA256'],
                                    alreadyIn17Originals=key in known,
                                    boundingOverlapWithCompleteProjectM2=intersection.area,
                                    model=model))
    extra = [r for r in matches if not r['alreadyIn17Originals']]
    result = dict(uids=mask['uids'], records=records, projectBoundedOriginalUnits=matches,
                  additionalOriginalUnits=extra, additionalCount=len(extra),
                  unknownBoundsRetained=sum(r['unitsWithUnknownBounds'] for r in records),
                  identityAccepted=False, physicalAccepted=False, installationApproved=False, sourceGeometryChanges=0,
                  qualification='Read-only source-key metadata census across all four pinned government native records. Includes units without viewer UID matches; does not assume the17 named actor files exhaust the source scene. Finite metadata bounds are broad-phase nominations only; missing bounds are explicitly retained. Extra units require exact byte recovery, complete geometry/identity/support evidence and current-map checks before use. No geometry, leases on source actors, queues, source rejection or installation state changed.')
    save(DOC/'lookup.json', result)
    module('southside_additional_original_support_lookup_freeze', HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'additional-original-project-units-including-unmatched-source-keys', list(dict.fromkeys(refs)), result)
    print(dict(additionalOriginalUnits=len(extra), unknownBounds=result['unknownBoundsRetained'],
               extra=[dict(modelId=r['model']['modelId'], faces=r['model']['triangles'],
                           viewerMatches=[v['uid'] for v in r['model'].get('matching', {}).get('viewerMatches', [])],
                           worldBounds=r['model']['worldBounds']) for r in extra]), flush=True)


if __name__ == '__main__':
    main()
