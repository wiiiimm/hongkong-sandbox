"""Independent source-cache readback; never grants installation acceptance."""
from pathlib import Path
from collections import Counter
from run import ROOT, HERE, read, save, digest, connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module

BASE = ROOT / 'docs/astra-city/government-import'
B = 'government-xl-recovered-terrain-root-check-v1-20261023'
N = dict(recovery='government-xl-missing-original-terrain-restore-v3-20261023',
         original='government-xl-all-200-original-terrain-batch-v2-20261022',
         installed='government-xl-fu-wong-retained-original-installed-v7-20261023')


def main():
    assert not (BASE / B).exists()
    refs, pins, verified = [Path(__file__)], {}, {}
    for key, name in N.items():
        result, pins[key] = authenticate(BASE / name)
        refs.append(BASE / name / 'result.json')
        if key == 'recovery':
            for q in result['evidenceRefs']:
                path = ROOT / q['path']
                assert digest(path.read_bytes()) == q['sha256']
                verified[q['path']] = q['sha256']
    def take(key, filename):
        path = BASE / N[key] / filename
        assert digest(path.read_bytes()) == pins[key][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)
    audit = take('installed', 'full-xl-current-count.json')
    assert audit['counts'] == dict(total=521, installedVerified=334, remaining=187)
    pending = {r['sourceKey'] for r in audit['rows'] if not r['installedVerified']}
    original = take('original', 'summary.json')
    wanted = [r for r in original['rows'] if r['sourceKey'] in pending and r['status'] == 'source-terrain-recovery-required']
    recovery = take('recovery', 'summary.json')
    by_key = {r['cacheKey']: r for r in recovery['rows']}
    assert len(by_key) == len(recovery['rows'])
    assert set(by_key) == {r['nativeCacheKey'] for r in wanted}
    source_records = read(BASE / 'government-xl-missing-original-terrain-restore-v1-20261023/source-records.json')
    native = {r['cacheKey']: r for r in source_records}
    assert set(native) == set(by_key)
    results = []
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        for source in wanted:
            row = by_key[source['nativeCacheKey']]
            assert db.execute('SELECT result_sha FROM astra_modelling.native_stage_results WHERE cache_key=%s', (row['cacheKey'],)).fetchone() == (row['nativeResultSHA256'],)
            if row['error'] is None:
                expected = {n: h for terrain in native[row['cacheKey']]['terrain'] for n, h in terrain['sourceHashes'].items()}
                assert set(row['files']) == set(expected)
                for name, q in row['files'].items():
                    assert q['sha256'] == expected[name] == verified[q['path']]
            results.append(dict(uid=source['uid'], sourceKey=source['sourceKey'], nativeCacheKey=source['nativeCacheKey'], status=row['status'], reason=row['error'], originalTerrainPaths=[q['path'] for name, q in row['files'].items() if name.endswith('.gltf')]))
    summary = dict(uids=sorted(r['uid'] for r in wanted), fullXLCounts=audit['counts'], rows=results,
                   currentPendingTerrainRecoveryModels=len(wanted), sourceSheets=len(by_key),
                   restoredModels=sum(r['reason'] is None for r in results),
                   heldModels=sum(r['reason'] is not None for r in results),
                   heldReasons=dict(Counter(r['reason']['reason'] for r in results if r['reason'])),
                   distinctVerifiedRecoveryReferences=len(verified),
                   historicalFailureReceiptQualification='V1 infrastructure-failure receipt used35 historical missing-terrain UIDs. Current installed-ledger intersection is34 across29sheets; this readback is authoritative for current recovery counts. No prior installed review is revoked or granted.',
                   sourceGeometryChanges=0, installationApproved=False, newlyInstalled=0,
                   qualification='ROOT exact-Neon/native-result/source-member SHA readback, bound to all521 current XL ledger rows. Source cache recovery only; foundations, placement, identity and publication remain separate.')
    save(BASE / B / 'summary.json', summary)
    refs += [ROOT / p for p in verified]
    module('recovered_terrain_root_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(B, 'recovered-original-terrain-independent-readback', refs, summary)


if __name__ == '__main__':
    main()
