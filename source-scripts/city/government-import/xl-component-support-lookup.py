"""Qualify exact support records before acquiring a component closure batch.

Metadata only: no original bytes acquired and no identity/installation approval.
Missing or ambiguous sources are recorded individually so others can proceed.
"""
import argparse
from pathlib import Path
from run import ROOT, read, save, digest, connect, NATIVE_RUN


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--selection', required=True)
    p.add_argument('--batch', required=True)
    p.add_argument('--exclude-support', action='append', default=[])
    a = p.parse_args()
    assert Path(a.batch).name == a.batch and a.batch.startswith('government-xl-')
    base = (ROOT / a.selection).resolve()
    assert base.parent == ROOT / 'docs/astra-city/government-import'
    doc = base.parent / a.batch
    assert not doc.exists(), 'Fresh immutable metadata only'
    inputs = read(base / 'inputs.json')
    pairs = inputs['pairs']
    manifest_path = ROOT / '3d-viewer/city/data/manifest.json'
    manifest = read(manifest_path)
    wanted = {r['supportUid'] for r in pairs} - set(a.exclude_support)
    forms = {}
    for tile in manifest['tiles']:
        path = ROOT / '3d-viewer' / tile['url']
        for b in read(path)['buildings']:
            if b['uid'] in wanted:
                assert b['uid'] not in forms
                forms[b['uid']] = {'building': b, 'tile': tile['url'], 'tileSHA256': digest(path.read_bytes())}
    assert set(forms) == wanted
    qualified, exceptions, stages = [], [], {}
    with connect() as con:
        con.execute('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY')
        for uid, source in sorted(forms.items()):
            b = source['building']
            profiles = con.execute('SELECT DISTINCT cache_key,sheet FROM astra_modelling.native_model_sizes '
                'WHERE run_id=%s AND model_id LIKE %s', (NATIVE_RUN, 'B' + b['buildingCSUID'][:10] + '%')).fetchall()
            matches = []
            for key, sheet in profiles:
                if key not in stages:
                    stages[key] = con.execute('SELECT r.result_sha,r.result FROM astra_modelling.native_stage_results r '
                        'JOIN astra_modelling.native_stage_members m USING(cache_key) '
                        'WHERE m.run_id=%s AND r.cache_key=%s', (NATIVE_RUN, key)).fetchone()
                assert stages[key]
                sha, data = stages[key]
                for m in data['models']:
                    if m['modelId'][1:11] == b['buildingCSUID'][:10] and any(
                        v['objectId'] == b['objectId'] and v['buildingCSUID'] == b['buildingCSUID']
                        for v in m.get('matching', {}).get('officialCandidates', [])):
                        matches.append({'cacheKey': key, 'resultSha': sha, 'sheet': sheet, 'model': m})
            if len(matches) != 1:
                exceptions.append({'uid': uid, 'exactMatches': len(matches),
                    'reason': 'missing-or-ambiguous-exact-original-support', 'source': source})
            else:
                qualified.append({'uid': uid, 'source': source, 'native': matches[0]})
    allowed = {r['uid'] for r in qualified}
    eligible = [pair for pair in pairs if pair['supportUid'] in allowed]
    refs = [{'path': str(path.relative_to(ROOT)), 'sha256': digest(path.read_bytes())}
            for path in [manifest_path, base / 'inputs.json', base / 'check-selection.json.gz', Path(__file__)]]
    save(doc / 'lookup.json.gz', {'qualifiedSources': qualified, 'lookupExceptions': exceptions})
    save(doc / 'inputs.json', {'batch': a.batch, 'pairs': eligible, 'sourceRefs': refs,
        'requestedPairs': pairs, 'excludedKnownFailedSupports': a.exclude_support,
        'lookupExceptions': [{k: r[k] for k in ('uid', 'exactMatches', 'reason')} for r in exceptions],
        'nativeRun': NATIVE_RUN, 'publication': False, 'newlyInstalled': 0,
        'qualification': 'Exact immutable metadata routing only; closure must reserve sources, rebind native receipts, recover exact bytes and run complete acceptance.'})
    print({'qualifiedPairs': len(eligible), 'lookupExceptions': [{k: r[k] for k in ('uid', 'exactMatches')} for r in exceptions]}, flush=True)


if __name__ == '__main__':
    main()
