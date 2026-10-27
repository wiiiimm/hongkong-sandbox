"""Find prepared overlapping originals around Elegant Garden's raised source bases.

Bounds nominate candidates only; no support, identity, geometry or installation
approval is inferred. Different GIS parent IDs do not exclude original sources.
"""
from pathlib import Path
import uuid
from run import ROOT, HERE, read, save, digest, connect, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module

BATCH = 'government-xl-elegant-garden-lower-original-discovery-v1-20261027'
UIDS = ['landsd/173532:0', 'landsd/173768:0']
BASE = ROOT / 'docs/astra-city/government-import'
SELECTION = 'government-xl-remaining-178-v3-current-scene-v1-20261023-chunk-04-selection'
INVENTORY = 'government-xl-after-ocean-four-unfinished-exact-source-inventory-v1-20261027'


def main():
    out = BASE / BATCH
    assert not out.exists()
    claim = reservations.claim('elegant-original-discovery-' + str(uuid.uuid4()),
                               ['building:' + u for u in UIDS], batch=BATCH, ttl=1800)
    assert claim['ok'], 'Do not overlap another owner or take over their work'
    lease = claim['reservation']
    try:
        refs = [Path(__file__)]
        _, pins = authenticate(BASE / SELECTION)
        path = BASE / SELECTION / 'selection.json.gz'
        assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
        refs += [BASE / SELECTION / 'result.json', path]
        sources = {r['uid']: r for r in read(path)['rows'] if r['uid'] in UIDS}
        assert sorted(sources) == UIDS
        _, inventory_pins = authenticate(BASE / INVENTORY)
        path = BASE / INVENTORY / 'summary.json'
        assert digest(path.read_bytes()) == inventory_pins[str(path.relative_to(ROOT))]
        refs += [BASE / INVENTORY / 'result.json', path]
        inventory = read(path)
        assert inventory['currentNativeActors'] == 6989 and inventory['unfinished'] == 126
        # Require exact current absence, not a historical assumption.
        manifest_path = ROOT / '3d-viewer/city/data/manifest.json'
        assert digest(manifest_path.read_bytes()) == inventory['currentManifestSHA256']
        manifest = read(manifest_path)
        refs.append(manifest_path)
        installed = {}
        for url in manifest['officialModelCatalogues']:
            path = ROOT / '3d-viewer' / url
            for entry in read(path)['models']:
                assert entry['uid'] not in installed
                installed[entry['uid']] = dict(catalogue=url, sourceSHA256=entry['sha256'])
        assert not set(UIDS) & set(installed)
        rows = []
        with connect() as db:
            db.execute('SET TRANSACTION READ ONLY')
            for uid in UIDS:
                source = sources[uid]
                asset = ROOT / source['candidate']['path']
                assert digest(asset.read_bytes()) == source['sourceSHA256']
                refs.append(asset)
                native = source['native']
                lo, hi = native['model']['worldBounds']
                sha = db.execute('SELECT result_sha FROM astra_modelling.native_stage_results WHERE cache_key=%s',
                                 (native['cacheKey'],)).fetchone()
                assert sha == (native['resultSha'],), 'Prepared sheet revision changed'
                matches = db.execute("""
                    SELECT m FROM astra_modelling.native_stage_results r
                    CROSS JOIN LATERAL jsonb_array_elements(r.result->'models') m
                    WHERE r.cache_key=%s AND m->>'modelId'<>%s
                    AND jsonb_typeof(m->'worldBounds')='array'
                    AND (m->'worldBounds'->0->>0)::double precision < %s
                    AND (m->'worldBounds'->1->>0)::double precision > %s
                    AND (m->'worldBounds'->0->>2)::double precision < %s
                    AND (m->'worldBounds'->1->>2)::double precision > %s
                    AND (m->'worldBounds'->0->>1)::double precision < %s
                    AND (m->'worldBounds'->1->>1)::double precision >= %s
                    ORDER BY m->>'modelId'
                """, (native['cacheKey'], source['modelId'], hi[0], lo[0], hi[2], lo[2],
                      lo[1] + .5, lo[1] - .5)).fetchall()
                candidates = []
                for (m,) in matches:
                    low, high = m['worldBounds']
                    overlap = (min(hi[0], high[0]) - max(lo[0], low[0])) * (min(hi[2], high[2]) - max(lo[2], low[2]))
                    candidate = m.get('candidate') or {}
                    candidate_uid = candidate.get('uid')
                    candidates.append(dict(model=m, candidateUid=candidate_uid,
                                           installed=installed.get(candidate_uid),
                                           boundsOverlapAreaM2=overlap,
                                           sourceTopMinusTowerBottomM=high[1] - lo[1],
                                           supportApproved=False, identityApproved=False))
                rows.append(dict(uid=uid, sourceSHA256=source['sourceSHA256'],
                                 modelId=source['modelId'], cacheKey=native['cacheKey'],
                                 nativeResultSHA256=native['resultSha'], sourceBounds=[lo, hi],
                                 candidates=candidates))
        assert reservations.owns(lease)
        assert digest(manifest_path.read_bytes()) == inventory['currentManifestSHA256']
        result = dict(uids=UIDS, rows=rows, nominatedPairs=sum(len(r['candidates']) for r in rows),
                      sourceGeometryChanges=0, sourcePoseChanges=0, aiGeometryModellingCalls=0,
                      physicalAcceptance=False, identityApproved=False, installationApproved=False,
                      publication=False, qualification='Only the exact prepared sheet revision was searched. '
                      'Positive XZ bounds overlap and vertical span near the source bottom nominate lower '
                      'or complex original structures regardless of GIS parent. Bounds are not footprints '
                      'or finite surface contacts; source acquisition, membership, pose, complete support '
                      'and current terrain/browser obligations remain unapproved.')
        save(out / 'summary.json', result)
        module('elegant_source_discovery_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
            BATCH, 'prepared-original-lower-structure-bounds-nomination', refs, result)
        print(dict(sources=len(rows), nominatedPairs=result['nominatedPairs'],
                   candidates=[dict(uid=r['uid'], models=[dict(modelId=c['model']['modelId'],
                               uid=c['candidateUid'], topMinusBase=c['sourceTopMinusTowerBottomM'])
                               for c in r['candidates']]) for r in rows]), flush=True)
    finally:
        assert reservations.release(lease)['ok']


if __name__ == '__main__':
    main()
