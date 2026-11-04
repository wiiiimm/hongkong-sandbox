"""Look beyond shared OSM parents for exact originals near unresolved rim points.

This read-only broad phase grants no support/component identity or acceptance.
Every previously checked pair is retained and excluded, never retried unchanged.
"""
import argparse
from collections import defaultdict
from pathlib import Path
import numpy as np
import shapely
from shapely.geometry import box, MultiPoint
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
    # Do not require shared OSM parent metadata. Exact official identities,
    # actual original bounds and later full contact checks remain mandatory.
    lower_forms = [b for b in forms.values() if b.get('structureType') in ('Tower', 'Podium')
                   and isinstance(b.get('baseHeightHKPD'), (int, float))]
    boxes = []
    for b in lower_forms:
        coords = np.asarray(b['rings'][0], dtype=float)
        boxes.append(box(*[coords[:, 0].min(), coords[:, 1].min(),
                          coords[:, 0].max(), coords[:, 1].max()]))
    tree = shapely.STRtree(boxes)
    possibilities = defaultdict(list)
    potential_metadata_pairs = 0
    for uid, samples in points.items():
        b = forms.get(uid)
        if not b or b.get('baseHeightHKPD') is None:
            continue
        query = MultiPoint([(p[0], p[2]) for p in sorted(samples)]).buffer(.001)
        for index in sorted(tree.query(query, predicate='intersects')):
            lower = lower_forms[int(index)]
            if lower['uid'] == uid or (uid, lower['uid']) in checked:
                continue
            if lower['baseHeightHKPD'] >= b['baseHeightHKPD']:
                continue
            possibilities[lower['uid']].append(uid)
            potential_metadata_pairs += 1
    print({'sourcesWithRimEvidence': len(points), 'newSpatialMetadataPairs': potential_metadata_pairs,
           'distinctPotentialSupports': len(possibilities)}, flush=True)
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
                    'potentialSamples': hits,
                    'sharesRecordedOSMParent': bool(forms[uid].get('parent') and forms[uid].get('parent') == forms[support_uid].get('parent'))})
    refs.extend({'path': str(path.relative_to(ROOT)), 'sha256': digest(path.read_bytes())}
                for path in (count_path, manifest_path, Path(__file__)))
    result = {'batch': a.batch, 'indexedRemaining': count['counts']['remaining'],
        'sourcesWithUnresolvedRimEvidence': len(points), 'exactLowerSources': len(source_matches),
        'sourceLookupExceptions': exceptions, 'pairs': candidates, 'inputRefs': refs,
        'newSpatialMetadataPairs': potential_metadata_pairs,
        'spatialSearchPolicy': 'current-form-bounds-at-failed-points-without-OSM-parent-filter-v1',
        'publication': False, 'newlyInstalled': 0, 'queuesCreated': 0,
        'qualification': 'Broad-phase lookup at recorded unresolved points across current official forms, without a shared-parent requirement. Exact source IDs and original bounds nominate checks only; they grant no support/component membership, identity, physical or installation acceptance. Previously checked pairs are excluded. Full original interfaces and all other gates remain required.'}
    for evidence in refs:
        assert digest((ROOT/evidence['path']).read_bytes()) == evidence['sha256'], 'Lookup input changed'
    save(doc / 'inventory.json', result)
    print({'sourcesWithRimEvidence': len(points), 'exactLowerSources': len(source_matches),
           'lookupExceptions': len(exceptions), 'newPairs': len(candidates)}, flush=True)
    print({'pairs': [{k: r[k] for k in ('uid', 'supportUid', 'name', 'supportName', 'type', 'supportType')}
                     | {'potentialSamples': len(r['potentialSamples'])} for r in candidates]}, flush=True)


if __name__ == '__main__':
    main()
