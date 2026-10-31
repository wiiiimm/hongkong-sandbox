"""Route unresolved original rim samples to untested original lower components.

Exact current form/native identifiers and original mesh bounds nominate checks.
Bounds are only a broad phase: they establish no contact, identity acceptance,
installation, source modification, or new queue.
"""
import argparse
from collections import defaultdict
from pathlib import Path
from run import ROOT, read, save, digest, connect, NATIVE_RUN
from government_georef_cell_identity import geographic_cell


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--count', required=True)
    p.add_argument('--batch', required=True)
    a = p.parse_args()
    assert Path(a.batch).name == a.batch and a.batch.startswith('government-xl-')
    doc = ROOT / 'docs/astra-city/government-import' / a.batch
    assert not doc.exists()
    count_path = ROOT / a.count
    count = read(count_path)
    manifest_path = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest_path.read_bytes()) == count['manifestSHA256']
    manifest = read(manifest_path)
    wanted = {r['uid']: r['indexedSourceSHA256'] for r in count['rows']
              if not r['installedVerified'] and r.get('uid')}
    forms, parents, refs = {}, defaultdict(list), []
    for tile in manifest['tiles']:
        path = ROOT / '3d-viewer' / tile['url']
        refs.append({'path': str(path.relative_to(ROOT)), 'sha256': digest(path.read_bytes())})
        for b in read(path)['buildings']:
            assert b['uid'] not in forms
            forms[b['uid']] = b
            if b.get('parent'):
                parents[b['parent']].append(b)
    checked, points = set(), defaultdict(set)
    for path in sorted(doc.parent.rglob('support-checks.json.gz')):
        data = read(path)
        relevant = False
        for r in data.get('rows', []):
            uid = r.get('uid')
            if uid and r.get('supportUid'):
                checked.add((uid, r['supportUid']))
            interface = r.get('interface')
            if uid not in wanted or r.get('sourceSHA256') != wanted[uid] or not interface:
                continue
            relevant = True
            for failure in interface.get('unresolved', []):
                points[uid].add(tuple(failure['position']))
        if relevant:
            refs.append({'path': str(path.relative_to(ROOT)), 'sha256': digest(path.read_bytes())})
    possibilities = defaultdict(list)
    for uid, samples in points.items():
        b = forms.get(uid)
        if not b or b.get('baseHeightHKPD') is None:
            continue
        for lower in parents[b.get('parent')]:
            if lower['uid'] == uid or (uid, lower['uid']) in checked:
                continue
            if lower.get('structureType') not in ('Tower', 'Podium'):
                continue
            if not set(b.get('osmRefs', [])) & set(lower.get('osmRefs', [])):
                continue
            if lower.get('baseHeightHKPD') is None or lower['baseHeightHKPD'] >= b['baseHeightHKPD']:
                continue
            possibilities[lower['uid']].append(uid)
    stage_cache, source_matches, exceptions = {}, {}, []
    with connect() as con:
        con.execute('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY')
        for support_uid in sorted(possibilities):
            lower = forms[support_uid]
            profiles = con.execute('SELECT DISTINCT cache_key,sheet FROM astra_modelling.native_model_sizes '
                'WHERE run_id=%s AND model_id LIKE %s',
                (NATIVE_RUN, 'B' + lower['buildingCSUID'][:10] + '%')).fetchall()
            matches = []
            for key, sheet in profiles:
                if key not in stage_cache:
                    stage_cache[key] = con.execute('SELECT r.result_sha,r.result FROM astra_modelling.native_stage_results r '
                        'JOIN astra_modelling.native_stage_members m USING(cache_key) '
                        'WHERE m.run_id=%s AND r.cache_key=%s', (NATIVE_RUN, key)).fetchone()
                assert stage_cache[key]
                sha, data = stage_cache[key]
                for model in data['models']:
                    try:
                        geographic_cell(model['modelId'], lower['buildingCSUID'], lower['structureType'])
                    except (KeyError, ValueError):
                        continue
                    exact = [m for m in model.get('matching', {}).get('officialCandidates', [])
                             if m.get('objectId') == lower['objectId'] and m.get('buildingCSUID') == lower['buildingCSUID']]
                    if len(exact) == 1:
                        matches.append({'cacheKey': key, 'resultSha': sha, 'sheet': sheet, 'model': model})
            if len(matches) != 1:
                exceptions.append({'uid': support_uid, 'matches': len(matches)})
                continue
            source_matches[support_uid] = matches[0]
    candidates = []
    for support_uid, native in sorted(source_matches.items()):
        lo, hi = native['model']['worldBounds']
        for uid in sorted(possibilities[support_uid]):
            # Ordinary 0.5m clearance bounds are used only for routing, never
            # increased or interpreted as complete source contact evidence.
            hits = [point for point in sorted(points[uid]) if
                    lo[0] - .001 <= point[0] <= hi[0] + .001 and
                    lo[2] - .001 <= point[2] <= hi[2] + .001 and
                    lo[1] - .5 <= point[1] <= hi[1] + .5]
            if hits:
                candidates.append({'uid': uid, 'supportUid': support_uid,
                    'name': forms[uid].get('name'), 'supportName': forms[support_uid].get('name'),
                    'type': forms[uid].get('structureType'), 'supportType': forms[support_uid]['structureType'],
                    'sourceSHA256': wanted[uid], 'supportSHA256': native['model']['asset']['sha256'],
                    'native': {k: native[k] for k in ('cacheKey', 'resultSha', 'sheet')},
                    'modelId': native['model']['modelId'], 'originalBounds': [lo, hi],
                    'potentialSamples': hits})
    refs.extend({'path': str(path.relative_to(ROOT)), 'sha256': digest(path.read_bytes())}
                for path in (count_path, manifest_path, Path(__file__)))
    result = {'batch': a.batch, 'indexedRemaining': count['counts']['remaining'],
        'sourcesWithUnresolvedRimEvidence': len(points), 'exactLowerSources': len(source_matches),
        'sourceLookupExceptions': exceptions, 'pairs': candidates, 'inputRefs': refs,
        'publication': False, 'newlyInstalled': 0, 'queuesCreated': 0,
        'qualification': 'Original source-bounds routing only, using exact identifiers and recorded unresolved samples. Bounds/shared parent are not physical support or source identity acceptance. Full original interfaces and all other gates remain required.'}
    save(doc / 'inventory.json', result)
    print({'sourcesWithRimEvidence': len(points), 'exactLowerSources': len(source_matches),
           'lookupExceptions': len(exceptions), 'newPairs': len(candidates)}, flush=True)
    print({'pairs': [{k: r[k] for k in ('uid', 'supportUid', 'name', 'supportName', 'type', 'supportType')}
                     | {'potentialSamples': len(r['potentialSamples'])} for r in candidates]}, flush=True)


if __name__ == '__main__':
    main()
